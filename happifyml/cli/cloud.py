import os
import sys
from argparse import REMAINDER, ArgumentDefaultsHelpFormatter, ArgumentParser, Namespace
from pathlib import Path
from typing import List

import questionary
from happifyml.utils.cli import print_error_exit, print_success, print_success_exit

from ..integrations import azure
from ..utils.credentials import AzureCredentials, HfCredentials, WandbCredentials
from . import SubParserAction

file_suffix = (".py", ".sh")
current_dir = Path(os.getcwd()).name


def register(subparsers: SubParserAction, parents: List[ArgumentParser]) -> None:

    # Azure cloud parsers
    azure_parser = subparsers.add_parser(
        "azure",
        parents=parents,
        formatter_class=ArgumentDefaultsHelpFormatter,
        help="submit argument to Azure cloud compute",
    )

    # Example AWS cloud parsers
    aws_parser = subparsers.add_parser(
        "aws",
        parents=parents,
        help="submit argument to AWS cloud compute",
        formatter_class=ArgumentDefaultsHelpFormatter,
    )

    parsers = [azure_parser, aws_parser]

    for parser in parsers:
        parser.add_argument("training_command", nargs="*", help="Arguments of the training script.")
        parser.add_argument("--register", type=str, default=False, help="run id")
        parser.add_argument("--model-name", required="--register" in sys.argv, type=str, help="model name")
        parser.add_argument(
            "--model-path", required="--register" in sys.argv, type=str, help="model path in experiment"
        )
        parser.add_argument("--experiment", type=str, default=current_dir, help="experiment name")
        parser.add_argument(
            "--base-docker",
            type=str,
            default="mcr.microsoft.com/azureml/openmpi4.1.0-cuda11.1-cudnn8-ubuntu18.04",
            help="base docker image",
        )
        parser.add_argument(
            "--docker",
            type=str,
            default="thomasyue/happifyml:HappifyML-pytorch-1.8-cuda11-cudnn8",
            help="docker image",
        )
        parser.add_argument("--nodes", type=int, default=None, help="number of nodes")

        if "azure" in parser.prog:
            parser.set_defaults(func=run_azure)
        elif "aws" in parser.prog:
            parser.set_defaults(func=run_aws)


def run_azure(args: Namespace) -> None:
    from azureml.core import Environment, Experiment, ScriptRunConfig, Workspace
    from azureml.core.runconfig import DockerConfiguration, MpiConfiguration, PyTorchConfiguration

    # simple sanity check if training_command file exists
    for item in args.training_command:
        if item.endswith(file_suffix):
            if not os.path.exists(item):
                print_error_exit(f"{item} not found.")

    # simple parse args and look for "args.nodes", if unavailable, prompt to ask for nodes
    for i, item in enumerate(args.training_command):
        if "nodes" in item:
            if "=" in item:
                args.nodes = item.split("=", 1)[-1]
            else:
                args.nodes = args.training_command[i + 1]

    if not args.nodes:
        args.nodes = questionary.text("Number of nodes not found, please enter number of nodes").unsafe_ask()

    azure_cred = AzureCredentials.get()
    hf_cred = HfCredentials.get()
    wandb_cred = WandbCredentials.get()

    try:
        if not azure_cred:
            azure_cred = azure.login()

        if not hf_cred:
            print("Find HF token in browser here: https://huggingface.co/settings/token")
            hf_cred = questionary.text("Huggingface User Access Token: ").unsafe_ask()
            HfCredentials.save(hf_cred)

        if not wandb_cred:
            print("Find API key in browser here: https://wandb.ai/authorize")
            wandb_cred = questionary.text("Wandb API Key: ").unsafe_ask()
            WandbCredentials.save(wandb_cred)

    except KeyboardInterrupt:
        print_success_exit("Cancelled, Run `happifyml azure` at any time to start distributed training")

    # access workspace
    ws = Workspace(**azure_cred)

    print(f"Current Workspace: {azure_cred['workspace_name']}")

    # if register model
    if args.register:
        azure.register_model(args, ws)

    elif args.training_command:
        print(args.training_command)
        available_computes = ws.compute_targets.keys()

        compute_target = questionary.select("Please choose compute", choices=available_computes).ask()

        # TODO(Thoams) parse environment for:
        # 1. pytorch version
        # 2. base_docker cuda, cudnn version
        env = Environment.from_conda_specification(args.experiment, "environment.yaml")
        env.docker.base_image = args.base_docker
        env.register(ws)
        docker_config = DockerConfiguration(use_docker=True)

        # set environment variables
        env.environment_variables["WANDB_API_KEY"] = wandb_cred
        env.environment_variables["HF_API_KEY"] = hf_cred
        env.environment_variables["AZURE_SUBSCRIPTION_ID"] = azure_cred["subscription_id"]
        env.environment_variables["AZURE_RESOURCE_GROUP"] = azure_cred["resource_group"]
        env.environment_variables["AZURE_WORKSPACE_NAME"] = azure_cred["workspace_name"]

        experiment = Experiment(workspace=ws, name=args.experiment)

        # TODO(Thomas) to include `export` to training_command for multi-node training environmental variables.

        # training_command = + training_command
        config = ScriptRunConfig(
            source_directory="./",
            command=args.training_command,
            compute_target=compute_target,
            environment=env,
            distributed_job_config=MpiConfiguration(node_count=args.nodes) if args.nodes > 1 else None,
            docker_runtime_config=docker_config,
        )

        run = experiment.submit(config)
        run.wait_for_completion(show_output=True)


def run_aws(args: Namespace) -> None:
    raise NotImplementedError


def run_core_weave(args: Namespace) -> None:
    raise NotImplementedError
