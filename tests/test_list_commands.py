from command_reminder.cli import parser
from tests.common import BaseTestCase, assert_stdout
from tests.helpers import with_mocked_environment


@with_mocked_environment
class ListTestCase(BaseTestCase):
    def test_should_list_empty_commands(self):
        # given
        parser.parse_args(['init'])

        # expect
        with assert_stdout() as stdout:
            parser.parse_args(['list'])
            self.assertEqual(len(stdout.output), 0)

    def test_should_filter_commands_by_tags(self):
        # given
        parser.parse_args(['init'])

        parser.parse_args(['record', '--name', 'mongo', '--command', 'mongo', '--tags', '#onduty #mongo'])
        parser.parse_args(['record', '--name', 'cassandra', '--command', 'cassandra', '--tags', '#onduty #cassandra'])

        # when
        with assert_stdout() as stdout:
            parser.parse_args(['list', '--tags', '#onduty'])
            self.assertEqual(len(stdout.output), 2)
            self.assertOutputContains(stdout.output, 'mongo: mongo')
            self.assertOutputContains(stdout.output, 'cassandra: cassandra')

        # when
        with assert_stdout() as stdout:
            parser.parse_args(['list', '--tags', '#mongo'])
            self.assertEqual(len(stdout.output), 1)
            self.assertOutputContains(stdout.output, 'mongo: mongo')

    def test_allow_use_tags_with_comma(self):
        # given
        parser.parse_args(['init'])

        parser.parse_args(['record', '--name', 'mongo', '--command', 'mongo', '--tags', '#onduty,#mongo'])

        with assert_stdout() as stdout:
            # when
            parser.parse_args(['list', '--tags', '#onduty'])

            # then
            self.assertEqual(len(stdout.output), 1)
            self.assertOutputContains(stdout.output, 'mongo: mongo')

        with assert_stdout() as stdout:
            # when
            parser.parse_args(['list', '--tags', '#onduty,        #mongo'])

            # then
            self.assertEqual(len(stdout.output), 1)
            self.assertOutputContains(stdout.output, 'mongo: mongo')

    def test_should_list_all_commands_when_no_tags_given(self):
        # given
        parser.parse_args(['init'])
        parser.parse_args(['record', '--name', 'mongo1', '--command', 'mongo', '--tags', '#onduty,#mongo'])
        parser.parse_args(['record', '--name', 'mongo2', '--command', 'mongo'])

        with assert_stdout() as stdout:
            # when
            parser.parse_args(['list'])

            # then
            self.assertEqual(len(stdout.output), 2)
            self.assertOutputContains(stdout.output, 'mongo1: mongo')
            self.assertOutputContains(stdout.output, 'mongo2: mongo')
