#!/usr/bin/env python

from setuptools import setup, find_packages

with open("README.md", "rt") as fh:
    long_description = fh.read()

dependencies = [
    "requests",
    "chia-blockchain@git+https://github.com/Chia-Network/chia-blockchain.git@main#fa2cdd6492bcffbe61f50fde8b5e1d4fd2ac5a16",
]

dev_dependencies = [
]

setup(
    name="kissmp",
    version="0.0.8",
    author="sometwit",  # ..probably
    packages=find_packages(exclude=("tests",)),
    entry_points={
        "console_scripts": ["kissmp = kissmp.kissmp:main"],
    },
    author_email="twit@inboxmail.e4ward.com",
    setup_requires=["setuptools_scm"],
    install_requires=dependencies,
    url="https://github.com/sometwit/kissmp",
    license="https://opensource.org/licenses/GPL-3.0",
    description="I would love to know that too.",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "License :: OSI Approved :: Apache Software License",
        "Topic :: Security :: Cryptography",
    ],
    extras_require=dict(
        dev=dev_dependencies,
    ),
    project_urls={
#        "Bug Reports": "https://github.com/don'tfuckingknowyet..",
        "Source": "https://github.com/sometwit/kissmp",
    },
)
