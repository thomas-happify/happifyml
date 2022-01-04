
import sys
from typing import Any, Text, NoReturn

class colors:
    HEADER = "\033[95m"
    OKBLUE = "\033[94m"
    OKGREEN = "\033[92m"
    WARNING = "\033[93m"
    FAIL = "\033[91m"
    ENDC = "\033[0m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"

def wrap_with_color(*args: Any, color: Text) -> Text:
    return color + " ".join(str(s) for s in args) + colors.ENDC

def print_color(*args: Any, color: Text) -> None:
    output = wrap_with_color(*args, color=color)
    print(output)


def print_success(*args: Any) -> None:
    print_color(*args, color=colors.OKGREEN)


def print_info(*args: Any) -> None:
    print_color(*args, color=colors.OKBLUE)


def print_warning(*args: Any) -> None:
    print_color(*args, color=colors.WARNING)


def print_error(*args: Any) -> None:
    print_color(*args, color=colors.FAIL)

def print_error_exit(msg: Text, exit_code: int = 1) -> None:
    print_error(msg)
    sys.exit(exit_code)

def print_success_exit(msg: Text = "No problem. You can continue setting up by running 'happifyml create' at any time 😊" , 
                       exit_code: int = 0) -> None:
    print_success(msg)
    sys.exit(exit_code)