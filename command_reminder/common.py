import os
from datetime import datetime


def get_timestamp() -> int:
    return int(datetime.now().timestamp())


class FilesMixin(object):
    @staticmethod
    def _create_dir(path: str) -> None:
        if not os.path.exists(path):
            os.makedirs(path)

    @staticmethod
    def _create_empty_file(path: str) -> None:
        if not os.path.exists(path):
            with open(path, 'w+'): ...
