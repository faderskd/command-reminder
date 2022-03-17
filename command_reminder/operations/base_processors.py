import json
import os
import typing
from abc import ABC, abstractmethod

from termcolor import colored

from command_reminder.common import FilesMixin


def read_file_content(f) -> typing.Dict[str, typing.List[typing.List[str]]]:
    s = f.read()
    if not s:
        commands = {}
    else:
        commands = json.loads(s)
    return commands


class OperationData: ...


class Processor(ABC, FilesMixin):
    @abstractmethod
    def process(self, operation: OperationData) -> None:
        pass

    @staticmethod
    def _print_colored(text):
        print(colored(text, 'blue'))
