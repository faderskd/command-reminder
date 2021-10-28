import sys
import argparse
from argparse import ArgumentParser

from command_reminder.cli.initializer import compound_processor
from command_reminder.cmd_processors.dto import InitOperationDto

DEFAULT_REPOSITORY_REPO = '~/.command-reminder/repository'


class Operations:
    INIT = "init"


def get_compound_processor():
    return compound_processor


def parse_args(raw_args) -> None:
    parser = argparse.ArgumentParser(description='Command Reminder CLI')
    subparsers = parser.add_subparsers(help="Command Reminder command to execute", dest="operation")
    init_parser = subparsers.add_parser(Operations.INIT, description="Initializes command-reminder project")
    _parse_init_subparser(init_parser)
    args = parser.parse_args(raw_args)

    operation = args.operation

    if operation == Operations.INIT:
        get_compound_processor().process(InitOperationDto(args.repo))


def _parse_init_subparser(parser: ArgumentParser) -> None:
    parser.add_argument('-r', '--repo', type=str, default=DEFAULT_REPOSITORY_REPO,
                        help=f'Repository to which saving commands. If empty default "{DEFAULT_REPOSITORY_REPO}" will be used')


if __name__ == '__main__':
    sys.argv[0] = "command-reminder"
    parse_args(sys.argv[1:])
