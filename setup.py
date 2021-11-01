import pathlib
from setuptools import setup, find_packages

# The directory containing this file
HERE = pathlib.Path(__file__).parent

# The text of the README file
README = (HERE / "README.md").read_text()

# This call to setup() does all the work
setup(
    name="command-reminder",
    version="0.1.0",
    description="Tool for saving/sharing your mostly used commands for fish shell",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://github.com/faderskd/command-reminder",
    author="faderskd",
    author_email="daniel.faderski@gmail.com",
    license="MIT",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
    ],
    packages=find_packages(exclude=("tests",)),
    include_package_data=True,
    install_requires=[],
    scripts=["scripts/cr"]
)
