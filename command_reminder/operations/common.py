import subprocess
from dataclasses import dataclass

import giturlparse


class InvalidArgumentException(ValueError):
    pass


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
        subprocess.run([directory, f'cd {directory} &&'
                                   ' git pull origin master'],
                       shell=True, check=True)

    @staticmethod
    def validate(repo: str) -> ParsedGitRepository:
        parsed = giturlparse.parse(repo)
        if not parsed.valid:
            raise InvalidArgumentException("Invalid git repository url")
        return ParsedGitRepository(parsed.owner, parsed.name)
