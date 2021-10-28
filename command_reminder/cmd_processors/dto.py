from dataclasses import dataclass


class Operation: ...


@dataclass
class InitOperationDto(Operation):
    repo: str