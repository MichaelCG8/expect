import ast

from .shared import modify_string


class TestComplexBlock:
    pass


#     @staticmethod
#     def test_complex_block_calls_function():
#         in_str = """
# a, b = expect func_2_tuple else:
#     fallback()
# """
#         expected_str = """
# if (ret := func_2_tuple()) is not None:
#     a, b = ret
# else:
#     fallback()
# """
#         modified_str = modify_string(in_str)
#         assert modified_str.strip("\r\n") == expected_str.strip("\r\n")
#         assert ast.dump(ast.parse(modified_str)) == ast.dump(ast.parse(expected_str))
#
#     @staticmethod
#     def test_complex_block_returns():
#         in_str = """
# a, b = expect func_2_tuple else:
#     return
# """
#         expected_str = """
# if (ret := func_2_tuple()) is not None:
#     a, b = ret
# else:
#     return
# """
#         modified_str = modify_string(in_str)
#         assert modified_str.strip("\r\n") == expected_str.strip("\r\n")
#         assert ast.dump(ast.parse(modified_str)) == ast.dump(ast.parse(expected_str))
