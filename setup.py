"""
Simple check list from AllenNLP repo: https://github.com/allenai/allennlp/blob/master/setup.py
PEP0440 compatible formatted version, see:
https://www.python.org/dev/peps/pep-0440/
release markers:
  X.Y
  X.Y.Z   # For bugfix releases
pre-release markers:
  X.YaN   # Alpha release
  X.YbN   # Beta release
  X.YrcN  # Release Candidate
  X.Y     # Final release
version.py defines the VERSION and VERSION_SHORT variables.
We use exec here so we don't import allennlp whilst setting up.
"""
import re

from setuptools import find_namespace_packages, find_packages, setup

_dependencies = [
    "questionary",
    "coloredlogs==15.0.1",
    "psutil",
    "pytest",
    "pytest-sugar",
    "pytest-cov",
    "mkdocs==1.1.2",
    "mkdocs-macros-plugin==0.5.0",
    "mkdocs-material==6.2.4",
    "mkdocstrings==0.14.0",
    "black==21.4b0",
    "flake8>=3.8.3",
    "isort>=5.5.4",
    "pre-commit==2.11.1",
]

deps = {b: a for a, b in (re.findall(r"^(([^!=<>]+)(?:[!=<>].*)?$)", x)[0] for x in _dependencies)}


def deps_list(*pkgs):
    return [deps[pkg] for pkg in pkgs]


extras = {}
# extras["test"] = deps_list("pytest", "pytest-sugar", "pytest-cov", "scikit-learn", "datasets")
# extras["docs"] = deps_list("mkdocs", "mkdocs-macros-plugin", "mkdocs-material", "mkdocstrings")
# extras["dev"] = deps_list("black", "flake8", "isort", "pre-commit") + extras["test"] + extras["docs"]

install_requires = [
    deps["questionary"],
    deps["psutil"],
]

print(find_namespace_packages())

setup(
    name="happifyml",
    version="0.0.1.dev0",
    description="Happify Health Inc. MLOps package",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="Thomas Yue",
    author_email="thomas@happify.com",
    url="https://github.com/thomas-happify/happifyml",
    # extras_require=extras,
    entry_points={"console_scripts": ["hml=happifyml.__main__:main"]},
    install_requires=install_requires,
    packages=find_packages(),
    include_package_data=True,  # configered in MANIFEST.in to include extra files weren't included in find_packages()
)
