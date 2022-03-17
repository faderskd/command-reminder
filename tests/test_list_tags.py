from command_reminder.cli import parser
from tests.common import BaseTestCase, assert_stdout
from tests.helpers import with_mocked_environment



@with_mocked_environment
class ListTagsTestCase(BaseTestCase):
    def test_should_return_empty_tags_list(self):
        # given
        parser.parse_args(['init'])

        with assert_stdout() as stdout:
            # when
            parser.parse_args(['tags'])

            # then
            self.assertEqual(len(stdout.output), 0)

    def test_should_return_tags_list(self):
        # given
        parser.parse_args(['init'])
        parser.parse_args(['record', '--name', 'mongo', '--command', 'mongo', '--tags', '#onduty,#mongo'])
        parser.parse_args(
            ['record', '--name', 'hermes', '--command', 'curl -X POST https://hermes.domain', '--tags', '#onduty '])

        with assert_stdout() as stdout:
            # when

            parser.parse_args(['tags'])

            # then
            self.assertEqual(len(stdout.output), 2)
            self.assertOutputContains(stdout.output, '#onduty')
            self.assertOutputContains(stdout.output, '#mongo')
