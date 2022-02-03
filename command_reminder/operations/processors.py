import json
import os
import re
import typing
import subprocess
from abc import ABC, abstractmethod

import giturlparse
from termcolor import colored

from command_reminder import common
from command_reminder.config.config import Configuration, FISH_FUNCTIONS_PATH_ENV, HISTORY_LOAD_FILE_NAME, \
    FISH_FUNCTIONS_DIR_NAME
from command_reminder.operations.common import InvalidArgumentException, GitRepository
from command_reminder.operations.dto import OperationData, InitOperationDto, RecordCommandOperationDto, \
    ListOperationDto, FoundCommandsDto, LoadCommandsListDto, RemoveCommandDto, PullExternalRepositoryDto


def read_file_content(f) -> typing.Dict[str, typing.List[typing.List[str]]]:
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

    @staticmethod
    def _print_colored(text):
        print(colored(text, 'blue'))


class InitRepositoryProcessor(Processor):
    def __init__(self, config: Configuration, git_repo: GitRepository):
        self._config = config
        self._git_repo = git_repo

    def process(self, data: OperationData) -> None:
        if not isinstance(data, InitOperationDto):
            return
        self._validate(data)
        self._create_dir(self._config.main_repository_fish_functions)
        self._create_empty_file(self._config.main_repository_commands_file)
        self._init_git_repo(self._config.main_repository_dir, data.repo)
        self._create_load_history_alias()
        self._generate_init_script()

    def _validate(self, data: InitOperationDto) -> None:
        if data.repo:
            self._git_repo.validate(data.repo)

    def _init_git_repo(self, directory: str, repo: str) -> None:
        self._git_repo.init_repo(directory, repo)

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
            commands[data.name] = (data.command, self._preprocess_tags(data.tags))
            json.dump(commands, f)
            f.truncate()

    def _create_fish_function(self, data: RecordCommandOperationDto) -> None:
        fish_func_file = self._config.internal_fish_function_file(data.name)
        if os.path.exists(fish_func_file):
            return
        with open(fish_func_file, 'w+') as f:
            f.write(f'''
function {data.name}
    set color {self.ECHO_COLOR}; echo '{data.command}'
end''')

    @staticmethod
    def _preprocess_tags(tags: typing.List[str]) -> typing.List[str]:
        stripped = [t.strip() for t in tags]
        return [t for t in stripped if t]


class ListCommandsProcessor(Processor):
    def __init__(self, config: Configuration):
        self._config = config

    def process(self, data: OperationData) -> None:
        if not isinstance(data, ListOperationDto):
            return
        if not os.path.exists(self._config.main_repository_commands_file):
            self._print_colored([])

        with open(self._config.main_repository_commands_file, 'r') as f:
            commands = read_file_content(f)
            results = self._search_for_commands_with_tags(commands, data.tags)
        self._print_results(results, data.pretty)

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


class LoadCommandProcessor(Processor):
    COMMAND_LINE_REGEX = "[\\w+-]+: (.+)"

    def __init__(self, config: Configuration):
        self._config = config

    def process(self, data: OperationData) -> None:
        if not isinstance(data, LoadCommandsListDto):
            return
        self._populate_fish_history(data.commands)

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


class TagsProcessor(Processor):
    def __init__(self, config: Configuration):
        super().__init__()
        self.config = config

    def process(self, _: OperationData) -> None:
        with open(self.config.main_repository_commands_file) as f:
            commands = read_file_content(f)
            all_tags = set()
            for (name, (content, tags)) in commands.items():
                for t in tags:
                    all_tags.add(t)
        for t in all_tags:
            self._print_colored(t)


class RemoveCommandProcessor(Processor):
    def __init__(self, config: Configuration):
        super().__init__()
        self._config = config

    def process(self, data: OperationData) -> None:
        if not isinstance(data, RemoveCommandDto):
            return
        if not os.path.exists(self._config.main_repository_commands_file):
            return
        self.remove_command(data)
        self.remove_fish_function(data)

    def remove_command(self, data: RemoveCommandDto):
        with open(self._config.main_repository_commands_file, 'r+') as f:
            commands = read_file_content(f)
            if data.command_name in commands:
                del commands[data.command_name]
            else:
                raise InvalidArgumentException(f'Command {data.command_name} does not exist.')
            f.seek(0)
            json.dump(commands, f)
            f.truncate()

    def remove_fish_function(self, data: RemoveCommandDto):
        func_file = self._config.internal_fish_function_file(data.command_name)
        if os.path.exists:
            os.remove(func_file)


class PullExternalRepoProcessor(Processor):
    def __init__(self, config: Configuration, git_repo: GitRepository):
        self._config = config
        self._git_repo = git_repo

    def process(self, data: OperationData) -> None:
        if not isinstance(data, PullExternalRepositoryDto):
            return
        parsed_repo = self._git_repo.validate(data.repo)
        external_repo_directory = self.get_target_dir_path(parsed_repo)
        self.prepare_external_repo_dir(data, external_repo_directory)

    def prepare_external_repo_dir(self, data, external_repo_directory):
        self._create_dir(external_repo_directory)
        self._git_repo.init_repo(external_repo_directory, data.repo)

    def get_target_dir_path(self, parsed_repo):
        external_repo_dir_name = (parsed_repo.owner + '_' + parsed_repo.name).replace('-', '_')
        target_directory = os.path.join(self._config.external_repository_directory(external_repo_dir_name))
        return target_directory
