import yaml
from command_reminder.config.config import Configuration

from command_reminder.common import FilesMixin


class PersistentConfig(FilesMixin):
    def __init__(self, config: Configuration):
        self._config = config

    def save_external_repo(self, repo: str):
        with open(self._config.config_file, 'r+') as f:
            data = f.read()
            parsed_data = yaml.compose(data)
            if not parsed_data:
                parsed_data = self._get_initial_config_content()
            external_repos = set(parsed_data['repositories']['external'])
            external_repos.add(repo)
            parsed_data['repositories']['external'] = list(external_repos)
            output = yaml.dump(parsed_data)
            f.seek(0)
            f.write(output)
            f.truncate()

    def get_external_repositories(self):
        with open(self._config.config_file, 'r') as f:
            data = f.read()
            parsed_data = yaml.safe_load(data)
            if parsed_data:
                return parsed_data['repositories']['external']
        return []

    @staticmethod
    def _get_initial_config_content():
        return {
            'repositories': {
                'external': []
            }
        }
