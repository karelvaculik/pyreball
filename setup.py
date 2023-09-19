from setuptools import find_packages, setup

with open("requirements_test.txt") as f:
    test_required = f.read().splitlines()

with open("requirements_examples.txt") as f:
    examples_required = f.read().splitlines()

import codecs
import os.path


def read(rel_path):
    here = os.path.abspath(os.path.dirname(__file__))
    with codecs.open(os.path.join(here, rel_path), "r") as fp:
        return fp.read()


def get_version(rel_path):
    # based on https://packaging.python.org/guides/single-sourcing-package-version/
    for line in read(rel_path).splitlines():
        if line.startswith("__version__"):
            delim = '"' if '"' in line else "'"
            return line.split(delim)[1]
    else:
        raise RuntimeError("Unable to find version string.")


setup(
    name="pyreball",
    version=get_version("pyreball/__init__.py"),
    description="Python reporting tool.",
    url="https://github.com/karelvaculik/pyreball",
    license="Apache License 2.0",
    author="Karel Vaculik",
    author_email="vaculik.dev@gmail.com",
    packages=find_packages(exclude=("examples", "tests")),
    package_data={
        "pyreball": [
            "cfg/config.ini",
            "cfg/css.template",
            "cfg/external_links.ini",
            "cfg/html.template",
        ]
    },
    include_package_data=True,
    tests_require=test_required + examples_required,
    long_description="Python reporting tool.",
    long_description_content_type="text/markdown",
    entry_points={
        "console_scripts": [
            "pyreball = pyreball.__main__:main",
            "pyreball-generate-config = pyreball.config_generator:main",
        ]
    },
)
