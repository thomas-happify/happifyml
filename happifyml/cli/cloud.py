import os
import sys
from argparse import REMAINDER, ArgumentDefaultsHelpFormatter, ArgumentParser, Namespace
from pathlib import Path
from typing import List

import questionary

from happifyml.utils.cli import print_error_exit, print_success, print_success_exit

from . import SubParserAction
from .credentials import AzureCredentials


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
    from azureml.core.runconfig import MpiConfiguration

    cred = AzureCredentials.get()

    if not cred:
        subscription_id = questionary.text("subscription_id:").ask()
        resource_group = questionary.text("resource_group:").ask()
        workspace_name = questionary.text("workspace_name:").ask()
        cred = {"subscription_id": subscription_id, "resource_group": resource_group, "workspace_name": workspace_name}
        AzureCredentials.save(cred)

    # access workspace
    ws = Workspace(**cred)

    print(f"Workspace: {cred['workspace_name']}")

    available_computes = ws.compute_targets.keys()

    compute_target = questionary.select("Please choose compute", choices=available_computes).ask()

    env = Environment(name="pytorch1.8")
    env.docker.base_image = "thomasyue/happifyml:HappifyML-pytorch-1.8-cuda11-cudnn8"
    env.python.user_managed_dependencies = True

    # set environment variables
    env.environment_variables["WANDB_API_KEY"] = "b3cb88ec1072ee5d4455cc074f1cd1842880f4a2"

    experiment = Experiment(workspace=ws, name="test_gpt_gpu")

    num_nodes = int([arg for arg in args.training_script if "node" in arg][0].split("=")[-1])

    config = ScriptRunConfig(
        source_directory="./",
        script=args.training_script,
        compute_target=compute_target,
        environment=env,
        arguments=args.training_args,
        distributed_job_config=MpiConfiguration(node_count=num_nodes),
    )

    run = experiment.submit(config)
    run.wait_for_completion(show_output=True)


def run_aws(args: Namespace) -> None:
    raise NotImplementedError


def run_core_weave(args: Namespace) -> None:
    raise NotImplementedError
