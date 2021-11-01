import json
import os
import typing
import subprocess
from abc import ABC, abstractmethod

import giturlparse

from command_reminder.common import InvalidArgumentException
from command_reminder.config.config import Configuration
from command_reminder.operations.dto import OperationData, InitOperationDataDto, RecordCommandOperationDataDto


class Processor(ABC):
    @abstractmethod
    def process(self, operation: OperationData) -> None:
        pass

    @staticmethod
    def _create_dir(path) -> None:
        if not os.path.exists(path):
            os.makedirs(path)


class InitRepositoryProcessor(Processor):
    def __init__(self, config: Configuration):
        self._config = config

    def process(self, data: OperationData) -> None:
        if not isinstance(data, InitOperationDataDto):
            return
        self._validate(data)
        self._create_dir(self._config.repositories_dir)
        self._init_git_repo(self._config.base_dir, data.repo)

    @staticmethod
    def _validate(data: InitOperationDataDto) -> None:
        if data.repo and not giturlparse.validate(data.repo):
            raise InvalidArgumentException("Invalid git repository url")

    @staticmethod
    def _init_git_repo(directory, repo):
        if repo:
            subprocess.run([f'cd {directory} && git init && git remote add origin {repo}'],
                           shell=True, check=True)


class RecordCommandProcessor(Processor):
    def __init__(self, config: Configuration):
        self._config = config

    def process(self, data: OperationData) -> None:
        if not isinstance(data, RecordCommandOperationDataDto):
            return
        self._create_dir(self._config.main_repository_dir)
        self._append_command(data)

    def _append_command(self, data: RecordCommandOperationDataDto) -> None:
        with open(self._config.main_repository_commands_file, 'w+') as f:
            s = f.read()
            if not s:
                commands = {}
            else:
                commands = json.loads(s)
            commands[data.name] = (data.command, data.tags)
            json.dump(commands, f)


class CompoundProcessor:
    def __init__(self, processors: typing.List[Processor]):
        self.processors = processors

    def process(self, operation: OperationData) -> None:
        for p in self.processors:
            p.process(operation)
