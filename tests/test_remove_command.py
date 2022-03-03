import os


from command_reminder.cli import parser
from command_reminder.config.config import REPOSITORIES_DIR_NAME, MAIN_REPOSITORY_DIR_NAME, FISH_FUNCTIONS_DIR_NAME
from command_reminder.exceptions import InvalidArgumentException
from tests.common import BaseTestCase, assert_stdout
from tests.helpers import with_mocked_environment, TEST_TMP_DIR_PATH


@with_mocked_environment
class RemoveCommandTestCase(BaseTestCase):
    def test_should_remove_command(self):
        # given
        parser.parse_args(['init'])
        parser.parse_args(['record', '--name', 'mongo', '--command', 'mongo', '--tags', '#mongo'])
        parser.parse_args(
            ['record', '--name', 'hermes', '--command', 'curl -X POST https://hermes.domain', '--tags',
             '#onduty,#hermes'])

        with assert_stdout() as stdout:
            parser.parse_args(['list'])
            self.assertEqual(len(stdout.output), 2)

        self.assertTrue(os.path.exists(
            f'/{TEST_TMP_DIR_PATH}/{REPOSITORIES_DIR_NAME}/{MAIN_REPOSITORY_DIR_NAME}/{FISH_FUNCTIONS_DIR_NAME}/hermes.fish'))

        # when
        parser.parse_args(['rm', '--command', 'hermes'])

        # then
        with assert_stdout() as stdout:
            parser.parse_args(['list'])
            self.assertEqual(len(stdout.output), 1)
            self.assertOutputContains(stdout.output, 'mongo')

        # and
        self.assertFalse(os.path.exists(
            f'/{TEST_TMP_DIR_PATH}/{REPOSITORIES_DIR_NAME}/{MAIN_REPOSITORY_DIR_NAME}/{FISH_FUNCTIONS_DIR_NAME}/hermes.fish'))

        # and
        with assert_stdout() as stdout:
            parser.parse_args(['tags'])
            self.assertEqual(len(stdout.output), 1)
            self.assertOutputContains(stdout.output, '#mongo')

    def test_should_raise_if_command_does_not_exists(self):
        # given
        parser.parse_args(['init'])

        # expect
        with self.assertRaisesRegex(InvalidArgumentException, 'Command notExisting does not exist'):
            parser.parse_args(['rm', '--command', 'notExisting'])
