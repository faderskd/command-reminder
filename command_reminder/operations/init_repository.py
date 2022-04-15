import os
from dataclasses import dataclass

from command_reminder.config.config import Configuration, FISH_FUNCTIONS_PATH_ENV, FISH_FUNCTIONS_DIR_NAME, \
    HISTORY_LOAD_FILE_NAME
from command_reminder.operations.base_processors import Processor, OperationData
from command_reminder.operations.common.dict_viewer import DirectoriesViewer
from command_reminder.operations.common.git import GitRepositoryManager


@dataclass
class InitOperationDto(OperationData):
    repo: str


class InitRepositoryProcessor(Processor):
    def __init__(self, config: Configuration, git_repo: GitRepositoryManager, dir_viewer: DirectoriesViewer):
        self._config = config
        self._git_repo = git_repo
        self._dir_viewer = dir_viewer

    def process(self, data: OperationData) -> None:
        if not isinstance(data, InitOperationDto):
            return
        self._validate(data)
        self._create_dir(self._config.main_repository_fish_functions)
        self._init_git_repo(self._config.main_repository_dir, data.repo)
        self._create_empty_file(self._config.main_repository_commands_file)
        self._create_empty_file(self._config.config_file)
        self._create_load_history_alias()
        self._generate_init_script()

    def _validate(self, data: InitOperationDto) -> None:
        if data.repo:
            self._git_repo.validate(data.repo)

    def _init_git_repo(self, directory: str, repo: str) -> None:
        if repo:
            self._git_repo.init_repo(directory, repo)

    def _generate_init_script(self) -> None:
        print(self._script_with_functions_dirs())

    def _script_with_functions_dirs(self) -> str:
        script = f'set -gx {FISH_FUNCTIONS_PATH_ENV} ${FISH_FUNCTIONS_PATH_ENV}'
        enhanced_script = self._enhance_with_fish_directories_repos(script)
        return " ".join(enhanced_script)

    def _enhance_with_fish_directories_repos(self, script):
        enhanced_script = [script]
        for dir_path in self._dir_viewer.list_all_repo_directories():
            if self._contains_fish_dir(dir_path):
                enhanced_script.append(os.path.join(dir_path, FISH_FUNCTIONS_DIR_NAME))
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
