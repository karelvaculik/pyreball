from setuptools import setup, find_packages

with open('requirements_test.txt') as f:
    test_required = f.read().splitlines()

with open('requirements_examples.txt') as f:
    examples_required = f.read().splitlines()

import codecs
import os.path


def read(rel_path):
    here = os.path.abspath(os.path.dirname(__file__))
    with codecs.open(os.path.join(here, rel_path), 'r') as fp:
        return fp.read()


def get_version(rel_path):
    # based on https://packaging.python.org/guides/single-sourcing-package-version/
    for line in read(rel_path).splitlines():
        if line.startswith('__version__'):
            delim = '"' if '"' in line else "'"
            return line.split(delim)[1]
    else:
        raise RuntimeError("Unable to find version string.")


setup(
    name='pyreball',
    version=get_version("pyreball/__init__.py"),
    description='pyreball',
    author='Karel Vaculik',
    author_email='vaculik.dev@gmail.com',
    packages=find_packages(exclude=('examples', 'tests')),
    package_data={'pyreball': ['cfg/html_begin.template', 'cfg/html_end.template']},
    include_package_data=True,
    tests_require=test_required + examples_required,
    entry_points={
        'console_scripts': [
            'pyreball = pyreball.__main__:main',
            'pyreball-generate-config = pyreball.config_generator:main',
        ]
    },
)
