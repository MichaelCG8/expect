"""
Test the importing machinery.

The tests should cover use of redundant symbols - e.g. unnecessary parentheses, line
continuation using "\" etc.
"""

from io import BytesIO
from tokenize import tokenize
from types import ModuleType

from expect.importer import _modify_tokens, _tokens_to_module


# TODO: Import a standard library file using expect_import and check that the module
#       matches the normal import.


DUMMY_MODULE_SOURCE = """
from typing import Optional, Tuple


def func() -> Optional[Tuple[int, int]]:
    return 1, 2


def func_n() -> Optional[Tuple[int, int]]:
    return None


def main():
    a, b = expect func() else (0, 0)
    return a, b
"""


def _src2mod(src: str) -> ModuleType:
    """Convert a source string to a module."""
    dummy_source_obj = BytesIO(src.strip("\r\n").encode("utf-8"))
    dummy_source_tokens = tokenize(dummy_source_obj.readline)
    dummy_module = _tokens_to_module(dummy_source_tokens, "dummy_module")
    return dummy_module


# TODO: Test more constructs.
def test_importer():
    dummy_module = _src2mod(DUMMY_MODULE_SOURCE)
    assert dummy_module.main() == (1, 2)  # pylint: disable=no-member
