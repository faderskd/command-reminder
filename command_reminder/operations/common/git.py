import os
import subprocess
from dataclasses import dataclass

import giturlparse

from command_reminder.operations.common.exceptions import InvalidArgumentException


@dataclass
class ParsedGitRepository:
    owner: str
    name: str


class GitRepository:
    def init_repo(self, directory: str, repo: str) -> None:
        if repo:
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
                        f' git co main'],
                       shell=True, check=True)

    @staticmethod
    def push_changes_to_remote(directory: str):
        subprocess.run([f'cd {directory} &&'
                        f' co main &&'
                        f' git commit -a -m "update repo" &&'
                        f' git push origin main'])

    @staticmethod
    def validate(repo: str) -> ParsedGitRepository:
        parsed = giturlparse.parse(repo)
        if not parsed.valid:
            raise InvalidArgumentException("Invalid git repository url")
        return ParsedGitRepository(parsed.owner, parsed.name)

    @staticmethod
    def is_git_repo(directory: str):
        return '.git' in os.listdir(directory)