import json
import os
import typing
import subprocess
from abc import ABC, abstractmethod

import giturlparse

from command_reminder.common import InvalidArgumentException
from command_reminder.config.config import Configuration, FISH_FUNCTIONS_PATH_ENV
from command_reminder.operations.dto import OperationData, InitOperationDto, RecordCommandOperationDto, \
    ListOperationDto, FoundCommandsDto


def read_file_content(f):
    s = f.read()
    if not s:
        commands = {}
    else:
        commands = json.loads(s)
    return commands


class Processor(ABC):
    @abstractmethod
    def process(self, operation: OperationData) -> None:
        pass

    @staticmethod
    def _create_dir(path: str) -> None:
        if not os.path.exists(path):
            os.makedirs(path)


class InitRepositoryProcessor(Processor):
    def __init__(self, config: Configuration):
        self._config = config

    def process(self, data: OperationData) -> None:
        if not isinstance(data, InitOperationDto):
            return
        self._validate(data)
        self._create_dir(self._config.main_repository_fish_functions)
        self._init_git_repo(self._config.base_dir, data.repo)
        self._add_functions_dir_to_search_path()

    @staticmethod
    def _validate(data: InitOperationDto) -> None:
        if data.repo and not giturlparse.validate(data.repo):
            raise InvalidArgumentException("Invalid git repository url")

    @staticmethod
    def _init_git_repo(directory: str, repo: str):
        if repo:
            subprocess.run([f'cd {directory} && git init && git remote add origin {repo}'],
                           shell=True, check=True)

    def _add_functions_dir_to_search_path(self) -> None:
        current_path = os.getenv(FISH_FUNCTIONS_PATH_ENV)
        main_functions_dir_exists = os.path.exists(self._config.main_repository_fish_functions)

        if main_functions_dir_exists and (
                not current_path or self._config.main_repository_fish_functions not in current_path):
            os.environ[FISH_FUNCTIONS_PATH_ENV] = f'{current_path} {self._config.main_repository_fish_functions}'


class RecordCommandProcessor(Processor):
    def __init__(self, config: Configuration):
        self._config = config

    def process(self, data: OperationData) -> None:
        if not isinstance(data, RecordCommandOperationDto):
            return
        self._append_command(data)
        self._create_fish_function(data)

    def _append_command(self, data: RecordCommandOperationDto) -> None:
        flags = 'w+'
        if os.path.exists(self._config.main_repository_commands_file):
            flags = 'r+'
        with open(self._config.main_repository_commands_file, flags) as f:
            commands = read_file_content(f)
            f.seek(0)
            commands[data.name] = (data.command, data.tags)
            json.dump(commands, f)
            f.truncate()

    def _create_fish_function(self, data: RecordCommandOperationDto) -> None:
        fish_func_file = os.path.join(self._config.main_repository_fish_functions, data.name + '.fish')
        if os.path.exists(fish_func_file):
            return
        with open(fish_func_file, 'w+') as f:
            f.write(f'''
            function {data.name}
                echo '{data.command}'
            end
            ''')


class ListCommandsProcessor(Processor):
    def __init__(self, config: Configuration):
        self._config = config

    def process(self, operation: OperationData) -> None:
        if not isinstance(operation, ListOperationDto):
            return
        if not os.path.exists(self._config.main_repository_commands_file):
            print([])

        with open(self._config.main_repository_commands_file, 'r') as f:
            commands = read_file_content(f)
            results = self._search_for_commands_with_tags(commands, operation.tags)
        self.print_results(results)

    @staticmethod
    def _search_for_commands_with_tags(commands: typing.Dict[str, typing.List[typing.List[str]]],
                                       search_tags: typing.List[str]) -> typing.List[FoundCommandsDto]:
        results = []
        search_tags = set(search_tags)
        for (name, (content, tags)) in commands.items():
            tags = set(tags)
            if search_tags.issubset(tags):
                results.append(FoundCommandsDto(command=content, name=name))
        return results

    @staticmethod
    def print_results(results: typing.List[FoundCommandsDto]):
        for r in results:
            print(f"{r.name}: {r.command}")


class CompoundProcessor(Processor):
    def __init__(self, processors: typing.List[Processor]):
        self.processors = processors

    def process(self, operation: OperationData) -> None:
        for p in self.processors:
            p.process(operation)
