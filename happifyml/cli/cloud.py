import os
import sys
from argparse import REMAINDER, ArgumentDefaultsHelpFormatter, ArgumentParser, Namespace
from pathlib import Path
from typing import List

import questionary

from happifyml.utils.cli import print_error_exit, print_success, print_success_exit

from . import SubParserAction


def register(subparsers: SubParserAction, parents: List[ArgumentParser]) -> None:

    azure_parser = subparsers.add_parser(
        "azure",
        parents=parents,
        help="submit argument to Azure clout compute",
        formatter_class=ArgumentDefaultsHelpFormatter,
    )

    aws_parser = subparsers.add_parser(
        "aws",
        parents=parents,
        help="submit argument to Azure clout compute",
        formatter_class=ArgumentDefaultsHelpFormatter,
    )

    parsers = [azure_parser, aws_parser]

    for parser in parsers:
        parser.add_argument(
            "training_script", type=str, help="path to the training script you want to submit to the cloud"
        )
        parser.add_argument("training_args", nargs=REMAINDER, help="Arguments of the training script.")

        if "azure" in parser.prog:
            parser.set_defaults(func=run_azure)
        elif "aws" in parser.prog:
            parser.set_defaults(func=run_aws)


def run_azure(args: Namespace) -> None:
    cmd = [args.training_script]
    cmd.extend(args.training_args)

    print(cmd)


def run_aws(args: Namespace) -> None:
    raise NotImplementedError


def run_core_weave(args: Namespace) -> None:
    raise NotImplementedError
