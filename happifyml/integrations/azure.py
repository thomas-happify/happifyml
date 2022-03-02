import os
from multiprocessing.sharedctypes import Value
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Set, Tuple, Union

import torch

import questionary
from azureml.core import Workspace
from azureml.core.model import Model

from ..utils.credentials import AzureCredentials


class AzureMixin:
    @classmethod
    def from_pretrained(
        cls,
        pretrained_model_name_or_path: str,
        workspace: Optional[str] = None,
        revision: Optional[Union[str, int]] = None,
        *model_args,
        **kwargs,
    ):
        """
        Download and initialize model from azure ml studio
        """
        if workspace and not os.path.isdir(pretrained_model_name_or_path):
            credential = AzureCredentials.get(workspace)
            workspace = Workspace(**credential)

            model = Model(workspace, pretrained_model_name_or_path, version=revision)
            print(f"Downloading {pretrained_model_name_or_path} from {workspace.name} model registry...")
            remote_path = model.download()
            os.rename(remote_path, pretrained_model_name_or_path)

        # try to look for hf model directory
        for root, dirs, files in os.walk(pretrained_model_name_or_path):
            for filename in files:
                if filename == "pytorch_model.bin":
                    pretrained_model_name_or_path = root
                    break

        return super(AzureMixin, cls).from_pretrained(pretrained_model_name_or_path, *model_args, **kwargs)

    def save_pretrained(
        self,
        save_directory: Union[str, os.PathLike],
        save_config: bool = True,
        state_dict: Optional[dict] = None,
        save_function: Callable = torch.save,
        push_to_azure: Optional[Union[bool, str]] = False,
        push_to_hub: bool = False,
        **kwargs,
    ):
        """
        difference between arg `push_to_azure` and AzureML.push_to_azure() is that:
        1. AzureML.push_to_azure() will push any artifacts.
        2. `push_to_azure only push model folder from `save_pretrained` without other artifacts.

        You can set push_to_azure=True, and push_to_hub=True at the same time which will push to 2 places.
        """

        super().save_pretrained(save_directory, save_config, state_dict, save_function, push_to_hub, **kwargs)

        if push_to_azure:
            if isinstance(push_to_azure, str):
                workspace_name = push_to_azure
            else:
                # use default workspace
                workspace_name = None

            # get credentials
            credential = AzureCredentials.get(workspace_name)
            workspace = Workspace(**credential)

            
            AzureMixin.push_to_azure(save_directory, workspace)

    @staticmethod
    def push_to_azure(model_path, workspace, **kwargs):
        model_name = Path(model_path).name
        print(f"Pushing {model_name} to {workspace.name} ... ")
        Model.register(workspace=workspace, model_path=model_path, model_name=model_name, **kwargs)


# TODO(Thomas) to add typing and comments
class AzureML:
    def __init__(self, subscription_id=None, resource_group=None, workspace_name=None):
        self.credentials = AzureML.login(subscription_id, resource_group, workspace_name)
        self.workspace = Workspace(**self.credentials)

    @staticmethod
    def login(subscription_id=None, resource_group=None, workspace_name=None):

        azure_cred = AzureCredentials.get()
        if not azure_cred:
            print("Find Azure properties in browser here: https://portal.azure.com/")
            try:
                subscription_id = questionary.text("subscription_id:").unsafe_ask()
                resource_group = questionary.text("resource_group:").unsafe_ask()
                workspace_name = questionary.text("workspace_name:").unsafe_ask()

            # if using in Jupyter
            except RuntimeError:
                subscription_id = input("subscription_id:")
                resource_group = input("resource_group:")
                workspace_name = input("workspace_name:")

            azure_cred = {
                "subscription_id": subscription_id,
                "resource_group": resource_group,
                "workspace_name": workspace_name,
            }

            # test if credentials are correct
            # TODO(Thomas) to find better approach to test if credentials can successfully login
            Workspace(**azure_cred)

            # save correct credentials
            AzureCredentials.save(azure_cred)

        return azure_cred

    @staticmethod
    def push(
        workspace: Optional[Workspace] = None,
        run_id: Optional[str] = None,
        model_remote_path: Optional[str] = None,
        model_name: Optional[str] = None,
    ):
        from azureml.core.run import Run

        # if model_name not available, we use model folder name by default
        if not model_name:
            model_name = Path(model_remote_path).name

        # if no run_id specified, try to get the current run.
        if not run_id:
            run = Run.get_context()
        else:
            run = workspace.get_run(run_id)

        details = run.get_details()
        print(f"Registering model from run: {run.id}, completed on (UTC): {details['endTimeUtc']}")
        model = run.register_model(model_name=model_name, model_path=model_remote_path)
        print(model)

    # def register_model(self, run_id, model_name, model_remote_path) -> None:
    #     run = self.workspace.get_run(run_id)
    #     print(f"Registering {model_name}")
    #     model = run.register_model(model_name=model_name, model_path=model_remote_path)
    #     print(model)

    def list_models(self):
        model_dict = self.workspace.models
        for model in model_dict:
            print(model_dict[model].id)

    def submit_training(self, command, experiment_name, base_docker, num_nodes, compute_target=None, **kwargs) -> None:
        from azureml.core import Environment, Experiment, ScriptRunConfig
        from azureml.core.runconfig import DockerConfiguration, MpiConfiguration

        if not compute_target:
            available_computes = self.workspace.compute_targets.keys()
            compute_target = questionary.select("Please choose compute", choices=available_computes).ask()

        # TODO(Thoams) parse environment for:
        # 1. pytorch version
        # 2. base_docker cuda, cudnn version
        env = Environment.from_conda_specification(experiment_name, "environment.yaml")
        env.docker.base_image = base_docker
        env.register(self.workspace)
        # docker_config = DockerConfiguration(use_docker=True)

        # set environment variables
        env.environment_variables["AZURE_SUBSCRIPTION_ID"] = self.credentials["subscription_id"]
        env.environment_variables["AZURE_RESOURCE_GROUP"] = self.credentials["resource_group"]
        env.environment_variables["AZURE_WORKSPACE_NAME"] = self.credentials["workspace_name"]

        # TODO(Thomas) handel exception if kwargs not provided
        env.environment_variables["WANDB_API_KEY"] = kwargs.get("hf_cred")
        env.environment_variables["HF_API_KEY"] = kwargs.get("hf_cred")

        experiment = Experiment(workspace=self.workspace, name=experiment_name)

        # TODO(Thomas) to include `export` to command for multi-node training environmental variables.
        # command = + command
        config = ScriptRunConfig(
            source_directory=".",
            command=command,
            compute_target=compute_target,
            environment=env,
            distributed_job_config=MpiConfiguration(node_count=num_nodes) if num_nodes > 1 else None,
            # docker_runtime_config=docker_config,
        )

        run = experiment.submit(config)
        run.wait_for_completion(show_output=True)
