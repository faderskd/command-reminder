import os
from dataclasses import dataclass

from command_reminder.config.config import Configuration, FISH_FUNCTIONS_PATH_ENV, FISH_FUNCTIONS_DIR_NAME, \
    HISTORY_LOAD_FILE_NAME
from command_reminder.operations.base_processors import Processor, OperationData
from command_reminder.operations.common import GitRepository


@dataclass
class InitOperationDto(OperationData):
    repo: str


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
        script = self._script_setting_main_functions_dir_to_search_path()
        if script:
            script = self._enhance_script_with_external_functions_dir(script)
        print(script)

    def _script_setting_main_functions_dir_to_search_path(self) -> str:
        main_functions_dir_exists = os.path.exists(self._config.main_repository_fish_functions)

        if main_functions_dir_exists:
            return f'set -gx {FISH_FUNCTIONS_PATH_ENV} ${FISH_FUNCTIONS_PATH_ENV} {self._config.main_repository_fish_functions}'
        return ''

    def _enhance_script_with_external_functions_dir(self, script) -> str:
        external_repos_directory = self._config.external_repositories_directory()
        if not os.path.exists(external_repos_directory):
            return script

        enhanced_script = self._get_fish_directories_of_external_repos(external_repos_directory, script)
        return " ".join(enhanced_script)

    def _get_fish_directories_of_external_repos(self, external_repos_directory, script):
        enhanced_script = [script]
        for external_file in os.listdir(external_repos_directory):
            external_dir_path = os.path.join(external_repos_directory, external_file)
            if self._is_directory(external_dir_path) and self._contains_fish_dir(external_dir_path):
                enhanced_script.append(os.path.join(external_dir_path, FISH_FUNCTIONS_DIR_NAME))
        return enhanced_script

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

    @staticmethod
    def _is_directory(directory: str) -> bool:
        return os.path.isdir(directory)

    @staticmethod
    def _contains_fish_dir(external_dir: str):
        return FISH_FUNCTIONS_DIR_NAME in os.listdir(external_dir)

