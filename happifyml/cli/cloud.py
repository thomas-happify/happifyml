import os
import sys
from argparse import REMAINDER, ArgumentDefaultsHelpFormatter, ArgumentParser, Namespace
from pathlib import Path
from typing import List

import questionary
from happifyml.utils.cli import print_error_exit, print_success, print_success_exit

# from ..integrations import azure
from ..integrations.azure import AzureML
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
        parser.add_argument("--relogin", action="store_true", help="relogin to Azure with different workspace")
        parser.add_argument("--set-env", action="store_true", help="set multi node training environment")

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

    if args.relogin:
        AzureML.relogin()

    aml = AzureML()

    if args.set_env:
        AzureML.set_multinode_environment()

    # azure_cred = AzureCredentials.get()
    hf_cred = HfCredentials.get()
    wandb_cred = WandbCredentials.get()

    try:
        # if not azure_cred:
        #     azure_cred = AzureML.login()

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

    # if register model
    if args.register:
        aml.register_model(run_id=args.register, model_name=args.model_name, model_remote_path=args.model_path)

    elif args.training_command:
        print(f"Current Workspace: {aml.azure_cred['workspace_name']}")

        # simple parse args and look for "nodes", if unavailable, prompt to ask for nodes
        for i, item in enumerate(args.training_command):
            if "nodes" in item:
                if "=" in item:
                    args.nodes = item.split("=", 1)[-1]
                else:
                    args.nodes = args.training_command[i + 1]

        if not args.nodes:
            args.nodes = questionary.text("Number of nodes not found, please enter number of nodes").unsafe_ask()

        aml.submit_training(
            command=args.training_command,
            experiment_name=args.experiment,
            base_docker=args.base_docker,
            num_nodes=int(args.nodes),
            hf_cred=hf_cred,
            wandb_cred=wandb_cred,
        )


def run_aws(args: Namespace) -> None:
    raise NotImplementedError


def run_core_weave(args: Namespace) -> None:
    raise NotImplementedError
