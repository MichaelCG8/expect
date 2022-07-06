"""
Test conditional expressions

The tests should cover use of redundant symbols - e.g. unnecessary parentheses, line
continuation using "\" etc.
"""

import ast

import pytest

from expect import ExpectParse
from .shared import modify_string


# TODO: Test with match.


class TestConditionalExpression:
    @staticmethod
    def test_condition_literal_none():
        in_str = """
a, b = expect None else (0, 0)
"""
        expected_str = """
a, b = ret if (ret := None) is not None else (0, 0)
"""
        modified_str = modify_string(in_str)
        assert modified_str.strip("\r\n") == expected_str.strip("\r\n")
        assert ast.dump(ast.parse(modified_str)) == ast.dump(ast.parse(expected_str))

    @staticmethod
    def test_condition_literal_truthy():
        in_str = """
a, b = expect 1 else (0, 0)
"""
        expected_str = """
a, b = ret if (ret := 1) is not None else (0, 0)
"""
        modified_str = modify_string(in_str)
        assert modified_str.strip("\r\n") == expected_str.strip("\r\n")
        assert ast.dump(ast.parse(modified_str)) == ast.dump(ast.parse(expected_str))

    @staticmethod
    def test_condition_literal_falsy():
        in_str = """
a, b = expect 0 else (0, 0)
"""
        expected_str = """
a, b = ret if (ret := 0) is not None else (0, 0)
"""
        modified_str = modify_string(in_str)
        assert modified_str.strip("\r\n") == expected_str.strip("\r\n")
        assert ast.dump(ast.parse(modified_str)) == ast.dump(ast.parse(expected_str))

    @staticmethod
    def test_condition_function():
        in_str = """
a, b = expect func_2_tuple() else (0, 0)
"""
        expected_str = """
a, b = ret if (ret := func_2_tuple()) is not None else (0, 0)
"""
        modified_str = modify_string(in_str)
        assert modified_str.strip("\r\n") == expected_str.strip("\r\n")
        assert ast.dump(ast.parse(modified_str)) == ast.dump(ast.parse(expected_str))

    @staticmethod
    def test_line_continuation():
        in_str = """
a, b = expect \
    func_2_tuple() else (0, 0)
"""
        expected_str = """
a, b = ret if (ret := \
    func_2_tuple()) is not None else (0, 0)
"""
        modified_str = modify_string(in_str)
        assert modified_str.strip("\r\n") == expected_str.strip("\r\n")
        assert ast.dump(ast.parse(modified_str)) == ast.dump(ast.parse(expected_str))

    @staticmethod
    def test_wrapping_parentheses():
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
        modified_str = modify_string(in_str)
        assert modified_str.strip("\r\n") == expected_str.strip("\r\n")
        assert ast.dump(ast.parse(modified_str)) == ast.dump(ast.parse(expected_str))

    @staticmethod
    def test_unexpected_newline_raises():
        in_str = """
a, b = expect
    func_2_tuple() else (0, 0)
"""
        with pytest.raises(ExpectParse) as exc_info:
            modify_string(in_str)
        assert (
            str(exc_info.value)
            == "Encountered NEWLINE token while in expect statement."
        )

    @staticmethod
    def test_internal_parentheses():
        in_str = """
a, b = expect (func_2_tuple()) else (0, 0)
"""
        expected_str = """
a, b = ret if (ret := (func_2_tuple())) is not None else (0, 0)
"""
        modified_str = modify_string(in_str)
        assert modified_str.strip("\r\n") == expected_str.strip("\r\n")
        assert ast.dump(ast.parse(modified_str)) == ast.dump(ast.parse(expected_str))

    @staticmethod
    def test_condition_is_conditional_expression():
        in_str = """
a, b = expect (1, 1) if something else None else (0, 0)
"""
        expected_str = """
a, b = ret if (ret := (1, 1) if something else None) is not None else (0, 0)
"""
        modified_str = modify_string(in_str)
        assert modified_str.strip("\r\n") == expected_str.strip("\r\n")
        assert ast.dump(ast.parse(modified_str)) == ast.dump(ast.parse(expected_str))

    @staticmethod
    def test_condition_is_chained_conditional_expression():
        in_str = """
a, b = expect (1, 1) if something else None if something_else else None else (0, 0)
"""
        expected_str = """
a, b = ret if (ret := (1, 1) if something else None if something_else else None) is not None else (0, 0)
"""
        modified_str = modify_string(in_str)
        assert modified_str.strip("\r\n") == expected_str.strip("\r\n")
        assert ast.dump(ast.parse(modified_str)) == ast.dump(ast.parse(expected_str))

    # TODO: No else should raise UnmetExpectation when the condition is None
    #     @staticmethod
    #     def test_no_else():
    #         in_str = """
    # a, b = expect func_2_tuple()
    # """

    @staticmethod
    def test_nested_expect():
        in_str = """
a, b = expect expect func_2_tuple() else (0, 0) else (1, 1)
"""

        # first step:
        # a, b = ret if (ret := expect func_2_tuple() else (0, 0)) is not None else (1, 1)
        expected_str = """
a, b = ret if (ret := ret if (ret := func_2_tuple()) is not None else (0, 0)) is not None else (1, 1)
"""
        modified_str = modify_string(in_str)
        assert modified_str.strip("\r\n") == expected_str.strip("\r\n")
        assert ast.dump(ast.parse(modified_str)) == ast.dump(ast.parse(expected_str))

        in_str = """
a, b = expect (expect func_2_tuple() else (0, 0)) else (1, 1)
"""
        expected_str = """
a, b = ret if (ret := (ret if (ret := func_2_tuple()) is not None else (0, 0))) is not None else (1, 1)
"""
        modified_str = modify_string(in_str)
        assert modified_str.strip("\r\n") == expected_str.strip("\r\n")
        assert ast.dump(ast.parse(modified_str)) == ast.dump(ast.parse(expected_str))

        in_str = """
a, b = (expect expect func_2_tuple() else (0, 0) else (1, 1))
"""
        expected_str = """
a, b = (ret if (ret := ret if (ret := func_2_tuple()) is not None else (0, 0)) is not None else (1, 1))
"""
        modified_str = modify_string(in_str)
        assert modified_str.strip("\r\n") == expected_str.strip("\r\n")
        assert ast.dump(ast.parse(modified_str)) == ast.dump(ast.parse(expected_str))

#     @staticmethod
#     def test_nested_expect_with_parentheses_raises():
#         in_str = """
# a, b = expect (expect func_2_tuple() else (0, 0)) else (1, 1)
# """
#         # Equivalent intermediate string
#         # """
#         # a, b = ret if (ret := expect func_2_tuple() else (0, 0)) is not None else (1, 1)
#         # """
#         with pytest.raises(ExpectParse) as exc_info:
#             modify_string(in_str)
#         assert (
#             str(exc_info.value) == "The result of expect cannot be used as a condition."
#         )

#     @staticmethod
#     def test_nested_expect_with_multiple_parentheses_raises():
#         in_str = """
# a, b = expect ((expect func_2_tuple() else (0, 0))) else (1, 1)
# """
#         # Equivalent intermediate string
#         # """
#         # a, b = ret if (ret := expect func_2_tuple() else (0, 0)) is not None else (1, 1)
#         # """
#         with pytest.raises(ExpectParse) as exc_info:
#             modify_string(in_str)
#         assert (
#             str(exc_info.value) == "The result of expect cannot be used as a condition."
#         )

    @staticmethod
    def test_expect_as_condition():
        in_str = """
if expect f() else True:
    pass
"""
        expected_str = """
if ret if (ret := f()) is not None else True:
    pass
"""
        modified_str = modify_string(in_str)
        assert modified_str.strip("\r\n") == expected_str.strip("\r\n")
        assert ast.dump(ast.parse(modified_str)) == ast.dump(ast.parse(expected_str))

        in_str = """
if (expect f() else True):
    pass
"""
        expected_str = """
if (ret if (ret := f()) is not None else True):
    pass
"""
        modified_str = modify_string(in_str)
        assert modified_str.strip("\r\n") == expected_str.strip("\r\n")
        assert ast.dump(ast.parse(modified_str)) == ast.dump(ast.parse(expected_str))
        in_str = """
if expect (f()) else True:
    pass
"""
        expected_str = """
if ret if (ret := (f())) is not None else True:
    pass
"""
        modified_str = modify_string(in_str)
        assert modified_str.strip("\r\n") == expected_str.strip("\r\n")
        assert ast.dump(ast.parse(modified_str)) == ast.dump(ast.parse(expected_str))

# TODO
#     @staticmethod
#     def test_expect_no_else_as_condition():
#         in_str = """
# if expect f():
#     pass
# """
#         expected_str = """
#     if (ret := f()) is None:
#         raise UnmetException
#     if ret:
#         pass
# """
#         modified_str = modify_string(in_str)
#         assert modified_str.strip("\r\n") == expected_str.strip("\r\n")
#         assert ast.dump(ast.parse(modified_str)) == ast.dump(ast.parse(expected_str))

    @staticmethod
    def test_expect_as_walrus_condition():
        # TODO: Is it necessary for the outer parentheses?
        in_str = """
if (a := expect f() else True):
    pass
"""
        expected_str = """
if (a := ret if (ret := f()) is not None else True):
    pass
"""
        modified_str = modify_string(in_str)
        assert modified_str.strip("\r\n") == expected_str.strip("\r\n")
        assert ast.dump(ast.parse(modified_str)) == ast.dump(ast.parse(expected_str))

        in_str = """
if ((a := expect f() else True)):
    pass
"""
        expected_str = """
if ((a := ret if (ret := f()) is not None else True)):
    pass
"""
        modified_str = modify_string(in_str)
        assert modified_str.strip("\r\n") == expected_str.strip("\r\n")
        assert ast.dump(ast.parse(modified_str)) == ast.dump(ast.parse(expected_str))
        in_str = """
if (a := expect (f()) else True):
    pass
"""
        expected_str = """
if (a := ret if (ret := (f())) is not None else True):
    pass
"""
        modified_str = modify_string(in_str)
        assert modified_str.strip("\r\n") == expected_str.strip("\r\n")
        assert ast.dump(ast.parse(modified_str)) == ast.dump(ast.parse(expected_str))

        in_str = """
if (a := (expect f() else True)):
    pass
"""
        expected_str = """
if (a := (ret if (ret := f()) is not None else True)):
    pass
"""
        modified_str = modify_string(in_str)
        assert modified_str.strip("\r\n") == expected_str.strip("\r\n")
        assert ast.dump(ast.parse(modified_str)) == ast.dump(ast.parse(expected_str))

# TODO
#     @staticmethod
#     def test_expect_no_else_as_walrus_condition():
#         in_str = """
# if a := expect f():
#     pass
# """
#         expected_str = """
#     if (ret := f()) is None:
#         raise UnmetException
#     if a := ret:
#         pass
# """
#         modified_str = modify_string(in_str)
#         assert modified_str.strip("\r\n") == expected_str.strip("\r\n")
#         assert ast.dump(ast.parse(modified_str)) == ast.dump(ast.parse(expected_str))

    @staticmethod
    def test_expect_in_generator_as_condition():
        in_str = """
if (expect f() else 1 for _ in range(n)):
    pass
"""
        expected_str = """
if (ret if (ret := f()) is not None else 1 for _ in range(n)):
    pass
"""
        modified_str = modify_string(in_str)
        assert modified_str.strip("\r\n") == expected_str.strip("\r\n")
        assert ast.dump(ast.parse(modified_str)) == ast.dump(ast.parse(expected_str))

    @staticmethod
    def test_expect_in_generator_as_condition_with_parentheses():
        in_str = """
if ((expect f() else 1 for _ in range(n))):
    pass
"""
        expected_str = """
if ((ret if (ret := f()) is not None else 1 for _ in range(n))):
    pass
"""
        modified_str = modify_string(in_str)
        assert modified_str.strip("\r\n") == expected_str.strip("\r\n")
        assert ast.dump(ast.parse(modified_str)) == ast.dump(ast.parse(expected_str))

        in_str = """
if ((expect f() else 1) for _ in range(n)):
    pass
"""
        expected_str = """
if ((ret if (ret := f()) is not None else 1) for _ in range(n)):
    pass
"""
        modified_str = modify_string(in_str)
        assert modified_str.strip("\r\n") == expected_str.strip("\r\n")
        assert ast.dump(ast.parse(modified_str)) == ast.dump(ast.parse(expected_str))

    @staticmethod
    def test_expect_in_tuple_as_condition():
        in_str = """
if (expect f() else 1,):
    pass
"""
        expected_str = """
if (ret if (ret := f()) is not None else 1,):
    pass
"""
        modified_str = modify_string(in_str)
        assert modified_str.strip("\r\n") == expected_str.strip("\r\n")
        assert ast.dump(ast.parse(modified_str)) == ast.dump(ast.parse(expected_str))

        in_str = """
if (expect f() else 1, expect f() else 1):
    pass
"""
        expected_str = """
if (ret if (ret := f()) is not None else 1, ret if (ret := f()) is not None else 1):
    pass
"""
        modified_str = modify_string(in_str)
        assert modified_str.strip("\r\n") == expected_str.strip("\r\n")
        assert ast.dump(ast.parse(modified_str)) == ast.dump(ast.parse(expected_str))

        in_str = """
if (expect f() else 1,) * n:
    pass
"""
        expected_str = """
if (ret if (ret := f()) is not None else 1,) * n:
    pass
"""
        modified_str = modify_string(in_str)
        assert modified_str.strip("\r\n") == expected_str.strip("\r\n")
        assert ast.dump(ast.parse(modified_str)) == ast.dump(ast.parse(expected_str))

    @staticmethod
    def test_expect_in_tuple_as_condition_with_parentheses():
        in_str = """
if ((expect f() else 1,)):
    pass
"""
        expected_str = """
if ((ret if (ret := f()) is not None else 1,)):
    pass
"""
        modified_str = modify_string(in_str)
        assert modified_str.strip("\r\n") == expected_str.strip("\r\n")
        assert ast.dump(ast.parse(modified_str)) == ast.dump(ast.parse(expected_str))

        in_str = """
if ((expect f() else 1, expect f() else 1)):
    pass
"""
        expected_str = """
if ((ret if (ret := f()) is not None else 1, ret if (ret := f()) is not None else 1)):
    pass
"""
        modified_str = modify_string(in_str)
        assert modified_str.strip("\r\n") == expected_str.strip("\r\n")
        assert ast.dump(ast.parse(modified_str)) == ast.dump(ast.parse(expected_str))

        in_str = """
if ((expect f() else 1), (expect f() else 1)):
    pass
"""
        expected_str = """
if ((ret if (ret := f()) is not None else 1), (ret if (ret := f()) is not None else 1)):
    pass
"""
        modified_str = modify_string(in_str)
        assert modified_str.strip("\r\n") == expected_str.strip("\r\n")
        assert ast.dump(ast.parse(modified_str)) == ast.dump(ast.parse(expected_str))

        in_str = """
if ((expect f() else 1,) * n):
    pass
"""
        expected_str = """
if ((ret if (ret := f()) is not None else 1,) * n):
    pass
"""
        modified_str = modify_string(in_str)
        assert modified_str.strip("\r\n") == expected_str.strip("\r\n")
        assert ast.dump(ast.parse(modified_str)) == ast.dump(ast.parse(expected_str))

        in_str = """
if ((expect f() else 1),) * n:
    pass
"""
        expected_str = """
if ((ret if (ret := f()) is not None else 1),) * n:
    pass
"""
        modified_str = modify_string(in_str)
        assert modified_str.strip("\r\n") == expected_str.strip("\r\n")
        assert ast.dump(ast.parse(modified_str)) == ast.dump(ast.parse(expected_str))

        in_str = """
if ((expect f() else 1,)) * n:
    pass
"""
        expected_str = """
if ((ret if (ret := f()) is not None else 1,)) * n:
    pass
"""
        modified_str = modify_string(in_str)
        assert modified_str.strip("\r\n") == expected_str.strip("\r\n")
        assert ast.dump(ast.parse(modified_str)) == ast.dump(ast.parse(expected_str))
