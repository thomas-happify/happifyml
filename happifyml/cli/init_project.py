from re import template
from . import BaseCLICommand, SubParserAction
from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter, Namespace
from typing import List
import os
import sys
from pathlib import Path
import shutil
import questionary
from happifyml.utils.cli import print_error_exit, print_success_exit


def create_command_factory(args: Namespace):
    return CreateCommand(args.init_dir)
    
    
class CreateCommand(BaseCLICommand):

    def register(parser: SubParserAction, parents: List[ArgumentParser]):
        new_project_parser = parser.add_parser(
            "create",        
            parents=parents,
            help="Creates a new project",
            formatter_class=ArgumentDefaultsHelpFormatter,
        )

        new_project_parser.add_argument(
            "--init-dir", 
            type=str, 
            default=".", 
            help="Project/Model name for the new project"
        )


        new_project_parser.set_defaults(func=create_command_factory)
    
    def __init__(self, init_dir: str):
        self.init_dir = init_dir

    
    def run(self):
        if self.init_dir is not None:
            path = self.init_dir

        else:
            path = (
                questionary.text(
                    "Please enter a path where the project will be "
                    "created [default: current directory]",
                ).ask()
            )

        if not os.path.isdir(path):
            print_error_exit(f"{path} not found. ❌")
            sys.exit(1)

        if path and not os.path.isdir(path):
            self._ask_create(path)
        
        # if path:
        #     print_success_exit()

        if len(os.listdir(path)) > 0:
            self._ask_overwrite(path)

        self.create_project(path)


    @staticmethod
    def _ask_create(path):
        create = questionary.confirm(
            f"'{path}' does not exist 🧐. Create now?"
        ).ask()

        if create:
            try:
                os.makedirs(path)
            except (PermissionError, OSError, FileExistsError) as e:
                print_error_exit(
                    f"Failed creating '{path}' ❌. " f"Error: {e}"
                )

        else:
            print_success_exit()

    @staticmethod
    def _ask_overwrite(path):
        overwrite = questionary.confirm(
            "Directory '{}' is not empty. Continue?".format(os.path.abspath(path))
        ).ask()

        if not overwrite:
            print_success_exit()

    @staticmethod
    def create_project(path) -> None:
        import pkg_resources

        os.chdir(path)
        template_path = pkg_resources.resource_filename(__name__, " ")
        template_path = Path(template_path).parents[1] / "templates" / "pl_research_template"
        print(template_path)
        shutil.copytree(template_path, path)
        print(f"Created project directory at {path}")
        