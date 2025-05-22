import sys
import os
import argparse
from setuptools import setup, find_packages

ROOT = os.path.dirname(__file__)


def get_long_description():
    with open(os.path.join(ROOT, 'README.md'), encoding='utf-8') as f:
        markdown_txt = f.read()
        return markdown_txt


def get_version():
    for line in open(os.path.join(ROOT, "version")).readlines():
        words = line.strip().split()
        if len(words) == 0:
            continue
        if words[0] == "version" and len(words) > 1:
            return words[-1]
    return "0.0.0"


def get_requirements(filename):
    with open(os.path.join(ROOT, filename)) as f:
        return [line.strip() for line in f]


parser = argparse.ArgumentParser(add_help=False)
parser.add_argument(
    '-r', '--requirement', help='Optionally specify a different requirements file.',
    required=False
)
args, unparsed_args = parser.parse_known_args()
sys.argv[1:] = unparsed_args

if args.requirement is None:
    install_requires = get_requirements("requirements.txt")
else:
    install_requires = get_requirements(args.requirement)

args = dict(
    name='DART',

    version=get_version(),

    description='Distributed Agent Run Time.',
    long_description=get_long_description(),

    url='*****',
    author='***',
    author_email='*****@mail.com',
    maintainer_email='*****@mail.com',

    license='****',

    python_requires='>=3.12',

    # packages=find_packages(include=['src/DART', 'src/DART.*'], exclude=("*.test", "test.*")),
    packages=find_packages(where='src', exclude=("*.test", "test.*")),
    package_dir={'': 'src'},

    setup_requires=['pytest-runner'],
    tests_require=['pytest', 'pytest-cov', 'pillow'],

    extras_require={
        'optional': ['tensorboard', 'matplotlib'],
    },

    install_requires=install_requires,

    classifiers=[
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python :: 3 :: Only',
    ],
)

setup(**args)
