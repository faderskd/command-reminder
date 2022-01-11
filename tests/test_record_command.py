import os

from command_reminder.cli import parser
from command_reminder.config.config import COMMAND_REMINDER_DIR_ENV, REPOSITORIES_DIR_NAME, \
    MAIN_REPOSITORY_DIR_NAME, COMMANDS_FILE_NAME, FISH_FUNCTIONS_DIR_NAME
from tests.common import BaseTestCase, assert_stdout
from tests.helpers import with_mocked_environment


@with_mocked_environment
class RecordTestCase(BaseTestCase):
    def test_should_record_command(self):
        # given
        parser.parse_args(['init'])

        # when
        parser.parse_args(
            ['record', '--name', 'mongo_login', '--command', 'mongo dburl/dbname --username abc --password pass'])

        # then
        self.assertTrue(os.path.exists(os.path.join(os.environ[COMMAND_REMINDER_DIR_ENV],
                                                    REPOSITORIES_DIR_NAME, MAIN_REPOSITORY_DIR_NAME,
                                                    COMMANDS_FILE_NAME)))

        with assert_stdout() as stdout:
            parser.parse_args(['list'])
            self.assertOutputContains(stdout.output, 'mongo_login: mongo dburl/dbname --username abc --password pass')

    def test_should_create_fish_function_joined_by_underscores(self):
        # given
        parser.parse_args(['init'])

        # when
        parser.parse_args(
            ['record', '--name', 'mongo login', '--command', 'mongo dburl/dbname --username abc --password pass'])

        # then
        function_file = os.path.join(os.environ[COMMAND_REMINDER_DIR_ENV], REPOSITORIES_DIR_NAME,
                                     MAIN_REPOSITORY_DIR_NAME,
                                     FISH_FUNCTIONS_DIR_NAME, 'mongo_login.fish')
        self.assertTrue(os.path.exists(function_file))

        # and
        self.assertFileContent(function_file, '''
function mongo_login
    set color blue; echo 'mongo dburl/dbname --username abc --password pass'
end''')
