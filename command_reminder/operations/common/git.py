import os
import subprocess
from dataclasses import dataclass

import giturlparse
from command_reminder.config.config import FISH_FUNCTIONS_DIR_NAME, COMMANDS_FILE_NAME, CONFIG_FILE_NAME

from command_reminder.exceptions import InvalidArgumentException


@dataclass
class ParsedGitRepository:
    owner: str
    name: str


class GitRepositoryManager:
    def init_repo(self, directory: str, repo: str) -> None:
        self.init_git(directory, repo)
        self.pull_changes_from_remote(directory)

    @staticmethod
    def init_git(directory: str, repo: str):
        subprocess.run([f'cd {directory} &&'
                        f' git init &&'
                        f' git remote add origin {repo}'],
                       shell=True, check=True)

    @staticmethod
    def pull_changes_from_remote(directory: str):
        subprocess.run([f'cd {directory} &&'
                        f' git pull origin main &&'
                        f' git checkout main'],
                       shell=True, check=True)

    @staticmethod
    def push_changes_to_remote(directory: str):
        subprocess.run([f'cd {directory} &&'
                        f' git checkout main &&'
                        f' git add {FISH_FUNCTIONS_DIR_NAME}/* &&'
                        f' git add {COMMANDS_FILE_NAME} &&'
                        f' git add {CONFIG_FILE_NAME} &&'
                        f' git commit -a -m \'update repo\' &&'
                        f' git push origin main'],
                       shell=True, check=True)

    @staticmethod
    def validate(repo_url: str) -> ParsedGitRepository:
        parsed = giturlparse.parse(repo_url)
        if not parsed.valid:
            raise InvalidArgumentException("Invalid git repository url")
        return ParsedGitRepository(parsed.owner, parsed.name)

    @staticmethod
    def is_git_repo(directory: str):
        return '.git' in os.listdir(directory)
