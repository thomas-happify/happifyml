import os
from argparse import REMAINDER, ArgumentDefaultsHelpFormatter, ArgumentParser, Namespace
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
        workspace: Optional[Workspace] = None,
        push_to_azure: bool = False,
        push_to_hub: bool = False,
        **kwargs,
    ):
        """
        difference between arg `push_to_azure` and AzureML.push_to_azure() is that:
        1. AzureML.push_to_azure() will push any artifacts.
        2. `push_to_azure only push model folder from `save_pretrained` without other artifacts.

        You can set push_to_azure=True, and push_to_hub=True at the same time which will push to 2 places.
        """

        if push_to_azure and not workspace:
            raise TypeError("push_to_azure requires Azure Workspace object")

        super().save_pretrained(save_directory, save_config, state_dict, save_function, push_to_hub, **kwargs)

        if push_to_azure:
            self.push_to_azure(save_directory, workspace)

    @staticmethod
    def push_to_azure(model_path, workspace, **kwargs):
        model_name = Path(model_path).name
        print(f"Pushing {model_name} to {workspace.name} ... ")
        Model.register(workspace=workspace, model_path=model_path, model_name=model_name, **kwargs)


class AzureML:
    def __init__(
        self, output_dir: Optional[str] = None, subscription_id=None, resource_group=None, workspace_name=None
    ):
        self.workspace = self.get_workspace(subscription_id, resource_group, workspace_name)
        self.output_dir = output_dir

    @staticmethod
    def get_workspace(subscription_id=None, resource_group=None, workspace_name=None):

        azure_cred = AzureML.login(subscription_id, resource_group, workspace_name)

        return Workspace(**azure_cred)

    @staticmethod
    def login(subscription_id=None, resource_group=None, workspace_name=None):

        azure_cred = AzureCredentials.get()
        if not azure_cred:
            print("Find Azure properties in browser here: https://portal.azure.com/")
            try:
                subscription_id = questionary.text("subscription_id:").unsafe_ask()
                resource_group = questionary.text("resource_group:").unsafe_ask()
                workspace_name = questionary.text("workspace_name:").unsafe_ask()

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
            Workspace(**azure_cred)

            # save correct credentials
            AzureCredentials.save(azure_cred)

        return azure_cred

    def relogin(subscription_id=None, resource_group=None, workspace_name=None):
        AzureCredentials.delete()

        return AzureML.login(subscription_id, resource_group, workspace_name)

    def push_to_azure(
        self, run_id: Optional[str] = None, output_dir: Optional[str] = None, model_name: Optional[str] = None
    ):
        from azureml.core.run import Run

        if not output_dir and not self.output_dir:
            raise ValueError(
                "output_dir is missing, please specify output_dir by calling `AzureML(output_dir)` or `AzureML.push(run_id, output_dir)`"
            )

        else:
            output_dir = self.output_dir if self.output_dir else output_dir

        if not model_name:
            model_name = Path(output_dir).name

        if not run_id:
            # if no run_id specified, try the current run.
            run = Run.get_context()
            run_id = run.id

        run = self.workspace.get_run(run_id)
        details = run.get_details()
        print(f"Registering model from run: {run.id}, completed on (UTC): {details['endTimeUtc']}")
        model = run.register_model(model_name=model_name, model_path=output_dir)
        print(model)

    def list_models(self):
        model_dict = self.workspace.models
        for model in model_dict:
            print(model_dict[model].id)


# def login() -> None:
#     print("Find Azure properties in browser here: https://portal.azure.com/")
#     subscription_id = questionary.text("subscription_id:").unsafe_ask()
#     resource_group = questionary.text("resource_group:").unsafe_ask()
#     workspace_name = questionary.text("workspace_name:").unsafe_ask()
#     azure_cred = {
#         "subscription_id": subscription_id,
#         "resource_group": resource_group,
#         "workspace_name": workspace_name,
#     }
#     AzureCredentials.save(azure_cred)
#     return azure_cred

# def get_workspace():
#     azure_cred = AzureCredentials.get()

#     if not azure_cred:
#         azure_cred = login()

#     return Workspace(**azure_cred)

# def relogin() -> None:
#     AzureCredentials.delete()
#     return login()


def register_model(args: Namespace, ws: Workspace) -> None:
    run = ws.get_run(args.register)
    print(f"Registering {args.model_name}")
    model = run.register_model(model_name=args.model_name, model_path=args.model_path)
    print(model)


def submit_training(args: Namespace, ws: Workspace) -> None:
    # TODO(Thomas) to move training from cloud.py to here.
    pass
