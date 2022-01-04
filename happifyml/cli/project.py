import os
import shutil
import sys
from argparse import ArgumentDefaultsHelpFormatter, ArgumentParser, Namespace
from pathlib import Path
from re import template
from typing import List

import questionary

from happifyml.utils.cli import print_error_exit, print_success, print_success_exit

from . import BaseCLICommand, SubParserAction


def register(subparsers: SubParserAction, parents: List[ArgumentParser]) -> None:
    parser = subparsers.add_parser(
        "init",
        parents=parents,
        help="initialize a new project",
        formatter_class=ArgumentDefaultsHelpFormatter,
    )

    # parser.set_defaults(func=run)

    parsers = parser.add_subparsers()

    project_parser = parsers.add_parser(
        "project",
        parents=parents,
        conflict_handler="resolve",
        formatter_class=ArgumentDefaultsHelpFormatter,
        help="Create training template",
    )

    project_parser.add_argument(
        "--name", type=str, default="new_project", help="Project/Model name for the new project"
    )

    project_parser.set_defaults(func=init_project)

    deploy_parser = parsers.add_parser(
        "deployment",
        parents=parents,
        conflict_handler="resolve",
        formatter_class=ArgumentDefaultsHelpFormatter,
        help="Create deployment template",
    )

    deploy_parser.add_argument(
        "--name", type=str, default="new_deployment", help="Project/Model name for the new deployment"
    )

    deploy_parser.set_defaults(func=init_deployment)


def init_deployment(args: Namespace) -> None:
    path = args.name

    if not os.path.isdir(path):
        _ask_create(path)

    if os.path.exists(path):
        _ask_overwrite(path)

    print_success("Mock deployment success!")


def init_project(args: Namespace) -> None:
    path = args.name

    if not os.path.isdir(path):
        _ask_create(path)

    if os.path.exists(path):
        # if len(os.listdir(path)) > 0:
        _ask_overwrite(path)

    create_project(path)


def _ask_create(path):
    create = questionary.confirm(f"'{path}' does not exist 🧐. Create now?").ask()

    if create:
        try:
            os.makedirs(path)
        except (PermissionError, OSError, FileExistsError) as e:
            print_error_exit(f"Failed creating '{path}' ❌. " f"Error: {e}")

    else:
        print_success_exit()


def _ask_overwrite(path):
    overwrite = questionary.confirm("Directory '{}' is not empty. Continue?".format(os.path.abspath(path))).ask()

    if not overwrite:
        print_success_exit()


def create_project(path) -> None:
    from distutils.dir_util import copy_tree

    import pkg_resources

    os.chdir(path)
    template_path = pkg_resources.resource_filename(__name__, " ")
    template_path = Path(template_path).parents[1] / "templates" / "pl_research_template"
    copy_tree(template_path, ".")
    print(f"Created project directory at {path}")
