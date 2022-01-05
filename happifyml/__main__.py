import argparse
import logging
import os
import platform
import sys

# from version import VERSION
from happifyml.cli import cloud, project
from happifyml.version import VERSION

logger = logging.getLogger(__name__)


def get_parser() -> argparse.ArgumentParser:

    parser = argparse.ArgumentParser(
        prog="happifyml",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        description="HappifyML command line interface. ",
    )

    parser.add_argument(
        "-V", "--version", action="store_true", default=argparse.SUPPRESS, help="Print installed HappifyML version"
    )

    main_parser = argparse.ArgumentParser(add_help=False)

    subparsers = parser.add_subparsers(help="HappifyML commands")

    project.register(subparsers, parents=[main_parser])
    cloud.register(subparsers, parents=[main_parser])

    return parser


def print_version() -> None:
    print(f"HappifyML Version : {VERSION}")
    print(f"Python Version    : {platform.python_version()}")
    print(f"Operating System  : {platform.platform()}")
    print(f"Interpreter Path  : {sys.executable}")


def main():
    arg_parser = get_parser()
    cmd = arg_parser.parse_args()

    sys.path.insert(1, os.getcwd())

    try:
        if hasattr(cmd, "func"):
            cmd.func(cmd)

        elif hasattr(cmd, "version"):
            print_version()

        else:
            logger.error("No command specified.")
            arg_parser.print_help()
            sys.exit(1)

    except Exception as e:
        logger.debug("Failed to run CLI command due to an exception.", exc_info=e)
        print(f"{e.__class__.__name__}: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
