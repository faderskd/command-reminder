import json
import os
import re
import typing
import subprocess
from abc import ABC, abstractmethod

import giturlparse
from termcolor import colored

from command_reminder import common
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
        self._generate_init_script()

    @staticmethod
    def _validate(data: InitOperationDto) -> None:
        if data.repo and not giturlparse.validate(data.repo):
            raise common.InvalidArgumentException("Invalid git repository url")

    @staticmethod
    def _init_git_repo(directory: str, repo: str):
        if repo:
            subprocess.run([f'cd {directory} && git init && git remote add origin {repo}'],
                           shell=True, check=True)

    def _generate_init_script(self):
        self._script_setting_functions_dir_to_search_path()

    def _script_setting_functions_dir_to_search_path(self) -> None:
        main_functions_dir_exists = os.path.exists(self._config.main_repository_fish_functions)

        if main_functions_dir_exists:
            print(
                f'set -gx {FISH_FUNCTIONS_PATH_ENV} ${FISH_FUNCTIONS_PATH_ENV} {self._config.main_repository_fish_functions}')


class RecordCommandProcessor(Processor):
    ECHO_COLOR = 'blue'

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
        name = self.parse_name(data.name)
        fish_func_file = os.path.join(self._config.main_repository_fish_functions, name + '.fish')
        if os.path.exists(fish_func_file):
            return
        with open(fish_func_file, 'w+') as f:
            f.write(f'''
            function {name}
                set color {self.ECHO_COLOR}; echo '{data.command}'
            end
            ''')

    @staticmethod
    def parse_name(name):
        return re.sub('\\s+', '_', name)


class ListCommandsProcessor(Processor):
    def __init__(self, config: Configuration):
        self._config = config

    def process(self, operation: OperationData) -> None:
        if not isinstance(operation, ListOperationDto):
            return
        if not os.path.exists(self._config.main_repository_commands_file):
            self._print_colored([])

        with open(self._config.main_repository_commands_file, 'r') as f:
            commands = read_file_content(f)
            results = self._search_for_commands_with_tags(commands, operation.tags)
        self._print_results(results)
        self._populate_fish_history(results)

    @staticmethod
    def _search_for_commands_with_tags(commands: typing.Dict[str, typing.List[typing.List[str]]],
                                       search_tags: typing.List[str]) -> typing.List[FoundCommandsDto]:
        results = []
        search_tags = set(search_tags)
        for (name, (content, tags)) in commands.items():
            tags = set(tags)
            if not search_tags or search_tags.issubset(tags):
                results.append(FoundCommandsDto(command=content, name=name))
        return results

    def _print_results(self, results: typing.List[FoundCommandsDto]):
        for r in results:
            self._print_colored(f"{r.name}: {r.command}")

    @staticmethod
    def _print_colored(text):
        print(colored(text, 'blue'))

    def _populate_fish_history(self, results: typing.List[FoundCommandsDto]):
        if len(results) > 1:
            return
        command = results[0].command
        with open(self._config.fish_history_file, 'a') as f:
            f.writelines([f'- cmd {command}\n',
                          f'  when {common.get_timestamp()}\n'])


class CompoundProcessor(Processor):
    def __init__(self, processors: typing.List[Processor]):
        self.processors = processors

    def process(self, operation: OperationData) -> None:
        for p in self.processors:
            p.process(operation)
