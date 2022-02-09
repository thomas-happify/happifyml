import os
import sys
from argparse import REMAINDER, ArgumentDefaultsHelpFormatter, ArgumentParser, Namespace
from pathlib import Path
from typing import List

import questionary

from happifyml.utils.cli import print_error_exit, print_success, print_success_exit

from . import SubParserAction
from ..utils.credentials import AzureCredentials, HfCredentials, WandbCredentials
from ..integrations import azure
from pathlib import Path

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
        parser.add_argument("--model-name", required='--register' in sys.argv, type=str, help="model name")
        parser.add_argument("--model-path", required='--register' in sys.argv, type=str, help="model path in experiment")
        parser.add_argument("--experiment", type=str, default=current_dir, help="experiment name")
        parser.add_argument("--docker", type=str, default="HappifyML-pytorch-1.8-cuda11-cudnn8", help="docker image")
        parser.add_argument("--nodes", type=int, default=1, help="number of nodes")

        if "azure" in parser.prog:
            parser.set_defaults(func=run_azure)
        elif "aws" in parser.prog:
            parser.set_defaults(func=run_aws)


def run_azure(args: Namespace) -> None:
    from azureml.core import Environment, Experiment, ScriptRunConfig, Workspace
    from azureml.core.runconfig import PyTorchConfiguration

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

    print(f"Workspace: {azure_cred['workspace_name']}")

    # if register model
    if args.register:
        azure.register_model(args, ws)

    elif args.training_command:
        available_computes = ws.compute_targets.keys()

        compute_target = questionary.select("Please choose compute", choices=available_computes).ask()

        try:
            env = Environment.get(workspace=ws, name=args.docker)
        except:
            env = Environment(name=args.docker)
            env.docker.base_image = f"thomasyue/happifyml:{args.docker}"
            env.python.user_managed_dependencies = True
            env.register(ws)

        # set environment variables
        env.environment_variables["WANDB_API_KEY"] = wandb_cred

        # huggingface private keys for use_auth_token when pushes to hub
        # https://github.com/huggingface/transformers/blob/f21bc4215aa979a5f11a4988600bc84ad96bef5f/src/transformers/file_utils.py#L2508
        # for more advance usage: https://github.com/aws/sagemaker-huggingface-inference-toolkit/blob/722edfbe255763637f69b9d14a05045e8771412b/src/sagemaker_huggingface_inference_toolkit/transformers_utils.py#L165
        env.environment_variables["HF_API_KEY"] = hf_cred
        
        # Azure credentials
        env.environment_variables["AZURE_SUBSCRIPTION_ID"] = azure_cred["subscription_id"]
        env.environment_variables["AZURE_RESOURCE_GROUP"] = azure_cred["resource_group"]
        env.environment_variables["AZURE_WORKSPACE_NAME"] = azure_cred["workspace_name"]

        experiment = Experiment(workspace=ws, name=args.experiment)

        # TODO: should extract arguments from yaml files instead of arguments which is less accurate.
        # num_nodes = int([arg for arg in args.training_command if "node" in arg][0].split("=")[-1])
        num_nodes = args.nodes

        config = ScriptRunConfig(
            source_directory="./",
            command=args.training_command,
            compute_target=compute_target,
            environment=env,
            distributed_job_config=PyTorchConfiguration(node_count=num_nodes),
        )

        run = experiment.submit(config)
        run.wait_for_completion(show_output=True)


def run_aws(args: Namespace) -> None:
    raise NotImplementedError


def run_core_weave(args: Namespace) -> None:
    raise NotImplementedError
