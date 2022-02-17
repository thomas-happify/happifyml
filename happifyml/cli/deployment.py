import os
from argparse import ArgumentDefaultsHelpFormatter, ArgumentParser, Namespace
from pathlib import Path
from typing import List

import questionary
from happifyml.utils.cli import print_error_exit, print_success, print_success_exit

from . import SubParserAction


def register(subparsers: SubParserAction, parents: List[ArgumentParser]) -> None:
    """
    Examples:
    1. create modelling repo
    `happifyml init project`

    2. create deployment repo
    `happifyml init deployment`

    """
    parser = subparsers.add_parser(
        "deploy",
        parents=parents,
        help="model deployment",
        formatter_class=ArgumentDefaultsHelpFormatter,
    )

    parser.add_argument("config", type=str, help="Kubernetes config file")

    parser.set_defaults(func=run_deployment)


def run_deployment(args: Namespace) -> None:
    import time

    print("⌛ Allocating Kubernetes resources...")
    time.sleep(4)
    print("✅ View deployment: http://localhost:8888/")
