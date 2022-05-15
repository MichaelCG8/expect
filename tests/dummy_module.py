from typing import Optional, Tuple


def func() -> Optional[Tuple[int, int]]:
    return 1, 2


def func_n() -> Optional[Tuple[int, int]]:
    return None


def main():
    # noinspection PyUnresolvedReferences
    a, b = expect func() else (0, 0)
    return a, b