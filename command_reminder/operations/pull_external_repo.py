import os
from dataclasses import dataclass

from command_reminder.config.config import Configuration
from command_reminder.operations.base_processors import Processor, OperationData
from command_reminder.operations.common import GitRepository


@dataclass
class PullExternalRepositoryDto:
    repo: str


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
