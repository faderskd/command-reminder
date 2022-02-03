import typing
from dataclasses import dataclass


class OperationData: ...


@dataclass
class InitOperationDto(OperationData):
    repo: str


@dataclass
class RecordCommandOperationDto(OperationData):
    command: str
    name: str
    tags: typing.List[str]


@dataclass
class ListOperationDto(OperationData):
    tags: typing.List[str]
    pretty: bool


@dataclass
class FoundCommandsDto:
    command: str
    name: str


@dataclass
class LoadCommandsListDto:
    commands: typing.List[str]


@dataclass
class RemoveCommandDto:
    command_name: str


@dataclass
class PullExternalRepositoryDto:
    repo: str
