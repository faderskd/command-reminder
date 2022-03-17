import os
from dataclasses import dataclass

from command_reminder.config.config import Configuration
from command_reminder.exceptions import InvalidArgumentException
from command_reminder.operations.base_processors import Processor, OperationData
from command_reminder.operations.common.git import GitRepositoryManager, ParsedGitRepository
from command_reminder.config.peristent_repository_config import PersistentConfig


@dataclass
class PullExternalRepositoryDto:
    repo: str
    refresh_all: bool


class PullExternalRepoProcessor(Processor):
    def __init__(self, config: Configuration, persistent_config: PersistentConfig,
                 git_repo_manager: GitRepositoryManager):
        self._config = config
        self._git_repo_manager = git_repo_manager
        self._persistent_config = persistent_config

    def process(self, data: OperationData) -> None:
        if not isinstance(data, PullExternalRepositoryDto):
            return
        if data.repo and data.refresh_all:
            raise InvalidArgumentException(
                'Use only one option --update_all or --repo while pulling external repositories.')
        if data.repo:
            self._pull_single_repository(data.repo)
        elif data.refresh_all:
            self._refresh_all_repositories()

    def _pull_single_repository(self, repo_url: str):
        parsed_repo = self._git_repo_manager.validate(repo_url)
        external_repo_directory = self._get_target_dir_path(parsed_repo)
        self._prepare_external_repo_dir(repo_url, external_repo_directory)
        self._persistent_config.save_external_repo(repo_url)

    def _prepare_external_repo_dir(self, repo: str, external_repo_directory: str):
        self._create_dir(external_repo_directory)
        self._git_repo_manager.init_repo(external_repo_directory, repo)

    def _get_target_dir_path(self, parsed_repo: ParsedGitRepository):
        external_repo_dir_name = (parsed_repo.owner + '_' + parsed_repo.name).replace('-', '_')
        target_directory = os.path.join(self._config.external_repository_directory(external_repo_dir_name))
        return target_directory

    def _refresh_all_repositories(self):
        for repo_url in self._persistent_config.get_external_repositories():
            parsed_repo = self._git_repo_manager.validate(repo_url)
            external_repo_directory = self._get_target_dir_path(parsed_repo)
            if os.path.exists(external_repo_directory):
                self._git_repo_manager.pull_changes_from_remote(external_repo_directory)
            else:
                self._prepare_external_repo_dir(repo_url, external_repo_directory)
