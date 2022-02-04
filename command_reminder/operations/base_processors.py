import json
import os
import typing
from abc import ABC, abstractmethod

from termcolor import colored


def read_file_content(f) -> typing.Dict[str, typing.List[typing.List[str]]]:
    s = f.read()
    if not s:
        commands = {}
    else:
        commands = json.loads(s)
    return commands


class OperationData: ...


class Processor(ABC):
    @abstractmethod
    def process(self, operation: OperationData) -> None:
        pass

    @staticmethod
    def _create_dir(path: str) -> None:
        if not os.path.exists(path):
            os.makedirs(path)

    @staticmethod
    def _create_empty_file(path: str) -> None:
        if not os.path.exists(path):
            with open(path, 'w+'): ...

    @staticmethod
    def _print_colored(text):
        print(colored(text, 'blue'))
