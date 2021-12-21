import json
import os
import re
import typing
import subprocess
from abc import ABC, abstractmethod

import giturlparse
from termcolor import colored

from command_reminder import common
from command_reminder.config.config import Configuration, FISH_FUNCTIONS_PATH_ENV, HISTORY_LOAD_FILE_NAME
from command_reminder.operations.dto import OperationData, InitOperationDto, RecordCommandOperationDto, \
    ListOperationDto, FoundCommandsDto, LoadCommandsListDto


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

    @staticmethod
    def _create_empty_file(path: str) -> None:
        if not os.path.exists(path):
            with open(path, 'w+'): ...


class InitRepositoryProcessor(Processor):
    def __init__(self, config: Configuration):
        self._config = config

    def process(self, data: OperationData) -> None:
        if not isinstance(data, InitOperationDto):
            return
        self._validate(data)
        self._create_dir(self._config.main_repository_fish_functions)
        self._create_empty_file(self._config.main_repository_commands_file)
        self._init_git_repo(self._config.base_dir, data.repo)
        self._create_load_history_alias()
        self._generate_init_script()

    @staticmethod
    def _validate(data: InitOperationDto) -> None:
        if data.repo and not giturlparse.validate(data.repo):
            raise common.InvalidArgumentException("Invalid git repository url")

    @staticmethod
    def _init_git_repo(directory: str, repo: str) -> None:
        if repo:
            subprocess.run([f'cd {directory} && git init && git remote add origin {repo}'],
                           shell=True, check=True)

    def _generate_init_script(self) -> None:
        self._script_setting_functions_dir_to_search_path()

    def _script_setting_functions_dir_to_search_path(self) -> None:
        main_functions_dir_exists = os.path.exists(self._config.main_repository_fish_functions)

        if main_functions_dir_exists:
            print(
                f'set -gx {FISH_FUNCTIONS_PATH_ENV} ${FISH_FUNCTIONS_PATH_ENV} {self._config.main_repository_fish_functions}')

    def _create_load_history_alias(self) -> None:
        alias_file = os.path.join(self._config.main_repository_fish_functions, HISTORY_LOAD_FILE_NAME)
        if os.path.exists(alias_file):
            return
        with open(alias_file, 'w+') as f:
            f.write('''
function h
    cr load && history merge
end
''')


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
        fish_func_file = os.path.join(self._config.main_repository_fish_functions, data.name + '.fish')
        if os.path.exists(fish_func_file):
            return
        with open(fish_func_file, 'w+') as f:
            f.write(f'''
function {data.name}
    set color {self.ECHO_COLOR}; echo '{data.command}'
end''')


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
        self._print_results(results, operation.pretty)

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

    def _print_results(self, results: typing.List[FoundCommandsDto], pretty: bool):
        for r in results:
            if pretty:
                self._print_colored(f"{r.name}: {r.command}")
            else:
                print(f"{r.name}: {r.command}")

    @staticmethod
    def _print_colored(text):
        print(colored(text, 'blue'))


class LoadCommandProcessor(Processor):
    COMMAND_LINE_REGEX = "[\\w+-]+: (.+)"

    def __init__(self, config: Configuration):
        self._config = config

    def process(self, operation: OperationData) -> None:
        if not isinstance(operation, LoadCommandsListDto):
            return
        self._populate_fish_history(operation.commands)

    def _populate_fish_history(self, commands: typing.List[str]):
        with open(self._config.fish_history_file, 'a') as f:
            for c in self._preprocess(commands):
                f.writelines([f'- cmd: {c}\n',
                              f'  when: {common.get_timestamp()}\n'])

    def _preprocess(self, commands: typing.List[str]) -> typing.Iterable[str]:
        filtered_commands = filter(lambda s: s.strip() and not s.strip().isspace(), commands)
        parsed_commands = list(map(lambda s: s.strip(), filtered_commands))

        for fc in parsed_commands:
            if match := re.match(self.COMMAND_LINE_REGEX, fc):
                yield match.group(1)


class CompoundProcessor(Processor):
    def __init__(self, processors: typing.List[Processor]):
        self.processors = processors

    def process(self, operation: OperationData) -> None:
        for p in self.processors:
            p.process(operation)
