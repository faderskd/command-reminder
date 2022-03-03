import os
from dataclasses import dataclass

from command_reminder.config.config import Configuration
from command_reminder.exceptions import InvalidArgumentException
from command_reminder.operations.base_processors import Processor, OperationData
from command_reminder.operations.common.git import GitRepository
from command_reminder.config.peristent_repository_config import PersistentConfig


@dataclass
class PullExternalRepositoryDto:
    repo: str
    refresh_all: bool


class PullExternalRepoProcessor(Processor):
    def __init__(self, config: Configuration, persistent_config: PersistentConfig, git_repo: GitRepository):
        self._config = config
        self._git_repo = git_repo
        self._persistent_config = persistent_config

    def process(self, data: OperationData) -> None:
        if not isinstance(data, PullExternalRepositoryDto):
            return
        if data.repo and data.refresh_all:
            raise InvalidArgumentException(
                'Use only one option --update_all or --repo while pulling external repositories.')
        if data.repo:
            self._pull_single_repository(data)
        elif data.refresh_all:
            self._refresh_all_repositories()

    def _pull_single_repository(self, data):
        parsed_repo = self._git_repo.validate(data.repo)
        external_repo_directory = self._get_target_dir_path(parsed_repo)
        self._prepare_external_repo_dir(data, external_repo_directory)
        self._persistent_config.save_external_repo(data.repo)

    def _prepare_external_repo_dir(self, data: PullExternalRepositoryDto, external_repo_directory: str):
        self._create_dir(external_repo_directory)
        if data.repo:
            self._git_repo.init_repo(external_repo_directory, data.repo)

    def _get_target_dir_path(self, parsed_repo):
        external_repo_dir_name = (parsed_repo.owner + '_' + parsed_repo.name).replace('-', '_')
        target_directory = os.path.join(self._config.external_repository_directory(external_repo_dir_name))
        return target_directory

    def _refresh_all_repositories(self):
        pass
