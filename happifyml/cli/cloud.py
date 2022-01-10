import os
import sys
from argparse import REMAINDER, ArgumentDefaultsHelpFormatter, ArgumentParser, Namespace
from pathlib import Path
from typing import List

import questionary

from happifyml.utils.cli import print_error_exit, print_success, print_success_exit

from . import SubParserAction
from .credentials import AzureCredentials, HfCredentials, WandbCredentials


def register(subparsers: SubParserAction, parents: List[ArgumentParser]) -> None:

    azure_parser = subparsers.add_parser(
        "azure",
        parents=parents,
        help="submit argument to Azure cloud compute",
        formatter_class=ArgumentDefaultsHelpFormatter,
    )

    aws_parser = subparsers.add_parser(
        "aws",
        parents=parents,
        help="submit argument to AWS cloud compute",
        formatter_class=ArgumentDefaultsHelpFormatter,
    )

    parsers = [azure_parser, aws_parser]

    for parser in parsers:
        parser.add_argument("training_script", type=str, help="path to the script you want to submit to the cloud")
        parser.add_argument("training_args", nargs=REMAINDER, help="Arguments of the training script.")
        parser.add_argument("--config_file", type=str, metavar="FILE", help="path to config file")

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

    if not azure_cred:
        subscription_id = questionary.text("subscription_id:").ask()
        resource_group = questionary.text("resource_group:").ask()
        workspace_name = questionary.text("workspace_name:").ask()
        azure_cred = {
            "subscription_id": subscription_id,
            "resource_group": resource_group,
            "workspace_name": workspace_name,
        }
        AzureCredentials.save(azure_cred)

    if not hf_cred:
        hf_cred = questionary.text("Huggingface User Access Token: ").ask()
        HfCredentials.save(hf_cred)

    if not wandb_cred:
        wandb_cred = questionary.text("Wandb API Key: ").ask()
        WandbCredentials.save(hf_cred)

    # access workspace
    ws = Workspace(**azure_cred)

    print(f"Workspace: {azure_cred['workspace_name']}")

    available_computes = ws.compute_targets.keys()

    compute_target = questionary.select("Please choose compute", choices=available_computes).ask()

    env = Environment(name="pytorch1.8")
    env.docker.base_image = "thomasyue/happifyml:HappifyML-pytorch-1.8-cuda11-cudnn8"
    env.python.user_managed_dependencies = True

    # set environment variables
    env.environment_variables["WANDB_API_KEY"] = wandb_cred
    # huggingface private keys for use_auth_token when push to hub
    # https://github.com/huggingface/transformers/blob/f21bc4215aa979a5f11a4988600bc84ad96bef5f/src/transformers/file_utils.py#L2508
    # for more advance usage: https://github.com/aws/sagemaker-huggingface-inference-toolkit/blob/722edfbe255763637f69b9d14a05045e8771412b/src/sagemaker_huggingface_inference_toolkit/transformers_utils.py#L165
    env.environment_variables["HF_API_KEY"] = hf_cred

    experiment = Experiment(workspace=ws, name="test_gpt_gpu")

    # TODO: should extract arguments from yaml files instead of arguments which is less accurate.
    num_nodes = int([arg for arg in args.training_args if "node" in arg][0].split("=")[-1])

    config = ScriptRunConfig(
        source_directory="./",
        script=args.training_script,
        compute_target=compute_target,
        environment=env,
        arguments=args.training_args,
        distributed_job_config=PyTorchConfiguration(node_count=num_nodes),
    )

    run = experiment.submit(config)
    run.wait_for_completion(show_output=True)


def run_aws(args: Namespace) -> None:
    raise NotImplementedError


def run_core_weave(args: Namespace) -> None:
    raise NotImplementedError
