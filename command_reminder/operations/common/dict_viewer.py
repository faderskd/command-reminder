import os

from command_reminder.config.config import Configuration


class DirectoriesViewer:
    def __init__(self, config: Configuration):
        self._config = config

    def list_all_repo_directories(self):
        results = [self._config.main_repository_dir]
        external_repos_directory = self._config.external_repositories_directory()
        if not os.path.exists(external_repos_directory):
            return results

        for external_file in os.listdir(external_repos_directory):
            external_file_path = os.path.join(external_repos_directory, external_file)
            if self._is_directory(external_file_path):
                results.append(external_file_path)

        return results

    @staticmethod
    def _is_directory(directory: str) -> bool:
        return os.path.isdir(directory)
