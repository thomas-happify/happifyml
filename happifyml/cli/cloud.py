import os
from argparse import ArgumentDefaultsHelpFormatter, ArgumentParser, Namespace
from pathlib import Path
from typing import List

import questionary

from happifyml.utils.cli import print_error_exit, print_success, print_success_exit

from . import SubParserAction


def register(subparsers: SubParserAction, parents: List[ArgumentParser]) -> None:
    parser = subparsers.add_parser(
        "azure",
        parents=parents,
        help="submit argument to Azure clout compute",
        formatter_class=ArgumentDefaultsHelpFormatter,
    )

    parser.add_argument("command", type=str, help="Python command you with to run in the cloud")

    parser.set_defaults(func=run)


def run(args: Namespace) -> None:
    print(args.command)
