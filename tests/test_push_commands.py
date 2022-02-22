import os
from unittest import mock
from unittest.mock import call

from command_reminder.operations.common.exceptions import InvalidArgumentException

from command_reminder.config.config import REPOSITORIES_DIR_NAME, MAIN_REPOSITORY_DIR_NAME

from command_reminder.cli import parser
from tests.common import BaseTestCase
from tests.helpers import with_mocked_environment, TEST_TMP_DIR_PATH


@with_mocked_environment
class PullExternalRepositoryTestCase(BaseTestCase):
    @mock.patch('command_reminder.cli.initializer.GitRepository')
    def test_should_push_command(self, git_mock):
        # given
        parser.parse_args(['init', '--repo', 'https://github.com/faderskd/common-commands'])

        # when
        parser.parse_args(['push'])

        # then
        main_dir = os.path.join(TEST_TMP_DIR_PATH, REPOSITORIES_DIR_NAME, MAIN_REPOSITORY_DIR_NAME)
        git_mock().push_changes_to_remote.assert_has_calls([call(main_dir)])

    def test_should_throw_exception_when_pushing_without_init_with_git_repository(self):
        # given
        parser.parse_args(['init'])

        with self.assertRaisesRegex(InvalidArgumentException, 'is not a git repo'):
            # when
            parser.parse_args(['push'])
