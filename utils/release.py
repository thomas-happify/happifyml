import argparse
import re

import git
import packaging.version

REPLACE_PATTERNS = {
    "init": (re.compile(r'^__version__\s+=\s+"([^"]+)"\s*$', re.MULTILINE), '__version__ = "VERSION"\n'),
    "setup": (re.compile(r'^(\s*)version\s*=\s*"[^"]+",', re.MULTILINE), r'\1version="VERSION",'),
}

REPLACE_FILES = {
    "init": "happifyml/__init__.py",
    "setup": "setup.py",
}


def get_version():
    """Reads the current version in the __init__."""
    with open(REPLACE_FILES["init"], "r") as f:
        code = f.read()
    default_version = REPLACE_PATTERNS["init"][0].search(code).groups()[0]
    return packaging.version.parse(default_version)


def bump_version_in_file(fname, version, pattern):
    """Update the version in one file using a specific pattern."""
    with open(fname, "r", encoding="utf-8", newline="\n") as f:
        code = f.read()
    re_pattern, replace = REPLACE_PATTERNS[pattern]
    replace = replace.replace("VERSION", version)
    code = re_pattern.sub(replace, code)
    with open(fname, "w", encoding="utf-8", newline="\n") as f:
        f.write(code)


def bump_global_version(version, patch=False):
    """Update the version in all needed files."""
    for pattern, fname in REPLACE_FILES.items():
        bump_version_in_file(fname, version, pattern)


def run_pre_release(patch=False):
    """Do all the necessary pre-release steps."""
    # First let's get the default version: base version if we are in dev, bump minor otherwise.
    default_version = get_version()
    if patch and default_version.is_devrelease:
        raise ValueError("Can't create a patch version from the dev branch, checkout a released version!")
    if default_version.is_devrelease:
        default_version = default_version.base_version
    elif patch:
        default_version = f"{default_version.major}.{default_version.minor}.{default_version.micro + 1}"
    else:
        default_version = f"{default_version.major}.{default_version.minor + 1}.0"

    # Now let's ask nicely if that's the right one.
    version = input(f"Which version are you releasing? [{default_version}]")
    if len(version) == 0:
        version = default_version

    print(f"Updating version to {version}.")
    bump_global_version(version, patch=patch)


def run_post_release():
    """Do all the necesarry post-release steps."""
    # First let's get the current version
    current_version = get_version()
    dev_version = f"{current_version.major}.{current_version.minor + 1}.0.dev0"
    current_version = current_version.base_version
    # Get the current commit hash
    repo = git.Repo(".", search_parent_directories=True)
    version_commit = repo.head.object.hexsha[:7]

    # Check with the user we got that right.
    version = input(f"Which version are we developing now? [{dev_version}]")
    commit = input(f"Commit hash to associate to v{current_version}? [{version_commit}]")
    if len(version) == 0:
        version = dev_version
    if len(commit) == 0:
        commit = version_commit

    print(f"Updating version to {version}.")
    bump_global_version(version)


def run_post_patch():
    """Do all the necesarry post-patch steps."""
    # Try to guess the right info: last patch in the minor release before current version and its commit hash.
    current_version = get_version()
    repo = git.Repo(".", search_parent_directories=True)
    repo_tags = repo.tags
    default_version = None
    version_commit = None
    for tag in repo_tags:
        if str(tag).startswith(f"v{current_version.major}.{current_version.minor - 1}"):
            if default_version is None:
                default_version = packaging.version.parse(str(tag)[1:])
                version_commit = str(tag.commit)[:7]
            elif packaging.version.parse(str(tag)[1:]) > default_version:
                default_version = packaging.version.parse(str(tag)[1:])
                version_commit = str(tag.commit)[:7]

    # Confirm with the user or ask for the info if not found.
    if default_version is None:
        version = input("Which patch version was just released?")
        commit = input("Commit hash to associated to it?")
    else:
        version = input(f"Which patch version was just released? [{default_version}]")
        commit = input(f"Commit hash to associated to it? [{version_commit}]")
        if len(version) == 0:
            version = default_version
        if len(commit) == 0:
            commit = version_commit


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--post_release", action="store_true", help="Whether this is pre or post release.")
    parser.add_argument("--patch", action="store_true", help="Whether or not this is a patch release.")
    args = parser.parse_args()
    if not args.post_release:
        run_pre_release(patch=args.patch)
    elif args.patch:
        run_post_patch()
    else:
        run_post_release()
