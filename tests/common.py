import os
import unittest
import shutil
from contextlib import redirect_stdout
from typing import List

from command_reminder.config.config import FISH_HISTORY_DIR, FISH_HISTORY_FILE_NAME
from tests.helpers import TEST_PATH


class StdoutRedirectionContext:
    class ListIO:
        def __init__(self):
            self.output = []

        def write(self, s):
            if s in ("\n", ""):
                return
            self.output.append(s)

    def __enter__(self):
        buf = self.ListIO()
        self._ctx = redirect_stdout(buf)
        self._ctx.__enter__()
        return buf

    def __exit__(self, exc_type, exc_value, exc_traceback):
        self._ctx.__exit__(exc_type, exc_value, exc_traceback)


def assert_stdout() -> StdoutRedirectionContext:
    return StdoutRedirectionContext()


class BaseTestCase(unittest.TestCase):
    def setUp(self) -> None:
        history_dir = os.path.join(TEST_PATH, FISH_HISTORY_DIR)
        self.history_file = os.path.join(history_dir, FISH_HISTORY_FILE_NAME)
        os.makedirs(history_dir)
        with open(self.history_file, 'w') as f:
            f.write(f'''
- cmd: brew install fish
  when: 1639436632
''')

    def tearDown(self) -> None:
        try:
            shutil.rmtree(TEST_PATH)
        except:
            pass

    def assertOutputContains(self, stdout: List[str], expected: str):
        self.assertTrue(any(expected in s for s in stdout))

    def assertFileContent(self, file_path, expected: str):
        with open(file_path, 'r') as f:
            content = ''.join([line for line in f.readlines()])
            self.assertEqual(content, expected)
