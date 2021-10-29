import sys
import argparse
from argparse import ArgumentParser

from command_reminder.operations.dto import InitOperationDataDto
from command_reminder.config.config import DEFAULT_REPOSITORY_REPO

from command_reminder.cli.initializer import AppContext


class Operations:
    INIT = "init"


def parse_args(raw_args) -> None:
    app_context = AppContext()
    parser = define_parser()
    args = parser.parse_args(raw_args)
    operation = args.operation

    if operation == Operations.INIT:
        app_context.compound_processor.process(InitOperationDataDto(args.repo, app_context.config.path))


def define_parser():
    parser = argparse.ArgumentParser(description='Command Reminder CLI')
    subparsers = parser.add_subparsers(help="Command Reminder command to execute", dest="operation")
    init_parser = subparsers.add_parser(Operations.INIT, description="Initializes command-reminder project")
    _parse_init_subparser(init_parser)
    return parser


def _parse_init_subparser(parser: ArgumentParser) -> None:
    parser.add_argument('-r', '--repo', type=str, default=DEFAULT_REPOSITORY_REPO,
                        help=f'Repository to which saving commands. If empty default "{DEFAULT_REPOSITORY_REPO}" will be used')


if __name__ == '__main__':
    sys.argv[0] = "command-reminder"
    parse_args(sys.argv[1:])
