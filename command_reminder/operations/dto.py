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


@dataclass
class FoundCommandsDto:
    command: str
    name: str
