"""
Test the importing machinery.

The tests should cover use of redundant symbols - e.g. unnecessary parentheses, line
continuation using "\" etc.
"""

import ast
from io import BytesIO
from tokenize import tokenize, untokenize
from types import ModuleType

import pytest

from expect import ExpectParse
from expect.importer import _modify_tokens, _tokens_to_module


# TODO: Import a standard library file using expect_import and check that the module
#       matches the normal import.

# TODO: Test nested expect statements.
#       Will need a counter for expect nesting, rather than an in_expect bool.

DUMMY_MODULE_SOURCE = """
from typing import Optional, Tuple


def func() -> Optional[Tuple[int, int]]:
    return 1, 2


def func_n() -> Optional[Tuple[int, int]]:
    return None


def main():
    # noinspection PyUnresolvedReferences
    a, b = expect func() else (0, 0)
    return a, b
"""


def _src2mod(src: str) -> ModuleType:
    """Convert a source string to a module."""
    dummy_source_obj = BytesIO(src.strip("\r\n").encode("utf-8"))
    dummy_source_tokens = tokenize(dummy_source_obj.readline)
    dummy_module = _tokens_to_module(dummy_source_tokens, "dummy_module")
    return dummy_module


def _modify_string(src: str) -> str:
    """Modify a source string"""
    dummy_file_obj = BytesIO(src.strip("\r\n").encode("utf-8"))
    modified_tokens = _modify_tokens(tokenize(dummy_file_obj.readline))
    modified_str = untokenize(modified_tokens).decode("utf-8")
    return modified_str


def test_importer():
    dummy_module = _src2mod(DUMMY_MODULE_SOURCE)
    assert dummy_module.main() == (1, 2)  # pylint: disable=no-member


class TestStringConversion:
    @staticmethod
    def test_conditional_expression_literal_none():
        in_str = """
a, b = expect None else (0, 0)
"""
        expected_str = """
a, b = ret if (ret := None) is not None else (0, 0)
"""
        modified_str = _modify_string(in_str)
        assert modified_str.strip("\r\n") == expected_str.strip("\r\n")
        assert ast.dump(ast.parse(modified_str)) == ast.dump(ast.parse(expected_str))

    @staticmethod
    def test_conditional_expression_literal_truthy():
        in_str = """
a, b = expect 1 else (0, 0)
"""
        expected_str = """
a, b = ret if (ret := 1) is not None else (0, 0)
"""
        modified_str = _modify_string(in_str)
        assert modified_str.strip("\r\n") == expected_str.strip("\r\n")
        assert ast.dump(ast.parse(modified_str)) == ast.dump(ast.parse(expected_str))

    @staticmethod
    def test_conditional_expression_literal_falsy():
        in_str = """
a, b = expect 0 else (0, 0)
"""
        expected_str = """
a, b = ret if (ret := 0) is not None else (0, 0)
"""
        modified_str = _modify_string(in_str)
        assert modified_str.strip("\r\n") == expected_str.strip("\r\n")
        assert ast.dump(ast.parse(modified_str)) == ast.dump(ast.parse(expected_str))

    @staticmethod
    def test_conditional_expression_function():
        in_str = """
a, b = expect func_2_tuple() else (0, 0)
"""
        expected_str = """
a, b = ret if (ret := func_2_tuple()) is not None else (0, 0)
"""
        modified_str = _modify_string(in_str)
        assert modified_str.strip("\r\n") == expected_str.strip("\r\n")
        assert ast.dump(ast.parse(modified_str)) == ast.dump(ast.parse(expected_str))

    @staticmethod
    def test_conditional_expression_line_continuation():
        in_str = """
a, b = expect \
    func_2_tuple() else (0, 0)
"""
        expected_str = """
a, b = ret if (ret := \
    func_2_tuple()) is not None else (0, 0)
"""
        modified_str = _modify_string(in_str)
        assert modified_str.strip("\r\n") == expected_str.strip("\r\n")
        assert ast.dump(ast.parse(modified_str)) == ast.dump(ast.parse(expected_str))

    @staticmethod
    def test_conditional_expression_wrapping_parentheses():
        in_str = """
a, b = (
    expect
    func_2_tuple() else (0, 0)
)
"""
        expected_str = """
a, b = (
    ret if (ret :=
    func_2_tuple()) is not None else (0, 0)
)
"""
        modified_str = _modify_string(in_str)
        assert modified_str.strip("\r\n") == expected_str.strip("\r\n")
        assert ast.dump(ast.parse(modified_str)) == ast.dump(ast.parse(expected_str))

    @staticmethod
    def test_conditional_expression_unexpected_newline_raises():
        in_str = """
a, b = expect
    func_2_tuple() else (0, 0)
"""
        with pytest.raises(ExpectParse):
            _modify_string(in_str)

    @staticmethod
    def test_conditional_expression_internal_parentheses():
        in_str = """
a, b = (
    expect
    (func_2_tuple()) else (0, 0)
)
"""
        expected_str = """
a, b = (
    ret if (ret :=
    (func_2_tuple())) is not None else (0, 0)
)
"""
        modified_str = _modify_string(in_str)
        assert modified_str.strip("\r\n") == expected_str.strip("\r\n")
        assert ast.dump(ast.parse(modified_str)) == ast.dump(ast.parse(expected_str))
