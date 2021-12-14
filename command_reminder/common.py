from datetime import datetime


class InvalidArgumentException(ValueError):
    pass


def get_timestamp() -> int:
    return int(datetime.now().timestamp())
