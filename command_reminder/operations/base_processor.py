from abc import ABC, abstractmethod

from termcolor import colored

from command_reminder.common import FilesMixin


class OperationData: ...


class Processor(ABC, FilesMixin):
    @abstractmethod
    def process(self, operation: OperationData) -> None:
        pass

    @staticmethod
    def _print_colored(text):
        print(colored(text, 'blue'))
