import os

from setuptools import setup, find_packages


def read(file_name):
    with open(os.path.join(os.path.dirname(__file__), file_name)) as file:
        return file.read()


def read_lines(file_name):
    with open(os.path.join(os.path.dirname(__file__), file_name)) as file:
        return file.readlines()


setup(
    name="fiasco_backend",
    version="1.0.0-dev",
    keywords=["fiasco-backend", "fiasco", "games", "board-games", "board"],
    url="https://github.com/fadich/fiasco-backend",
    author="Fadi A.",
    author_email="royalfadich@gmail.com",
    description="Utilities for board games.",
    long_description=read("README.md"),
    long_description_content_type="text/markdown",
    packages=find_packages(),
    install_requires=read_lines("requirements.txt"),
    entry_points={
        "console_scripts": [
            "fiasco-backend = fiasco_backend.__main__:main",
        ],
    }
)