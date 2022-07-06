"""
The importer machinery.

This module locates imported objects, converts uses of `expect` and generates a module
using that modified code.
"""

import importlib
import sys
from tokenize import tokenize, untokenize, TokenInfo, NAME, NEWLINE, OP
from types import ModuleType
from typing import Generator, List, Tuple


class ExpectParse(Exception):
    pass


def _add_offset(token: TokenInfo, offset: int) -> TokenInfo:
    """Shift a token's start and end location in a row by `offset`"""
    new_start = _pad_pos(token.start, offset)
    new_end = _pad_pos(token.end, offset)
    # noinspection PyArgumentList
    return TokenInfo(token.type, token.string, new_start, new_end, token.line)


def _pad_pos(pos: Tuple[int, int], offset: int) -> Tuple[int, int]:
    """Pad a (row, col) tuple by `offset` columns"""
    return pos[0], pos[1] + offset


def expect_import(module_name: str) -> ModuleType:
    """Load the named module, convert `expect` usages and return it."""
    # First, try to import the module without parsing except clauses.
    # If this succeeds, except is not used and the module can be returned immediately.
    # If this fails, get the path of the module and parse the except clauses.
    try:
        module = importlib.import_module(
            module_name
        )  # TODO: Read up on how import_module works.
        return module
    except SyntaxError as exc:
        module_path = exc.filename

    with open(module_path, "rb") as f:
        tokens = tokenize(f.readline)

    module = _tokens_to_module(tokens, module_name)
    sys.modules[module_name] = module

    return module


def _tokens_to_module(
    tokens: Generator[TokenInfo, None, None], module_name: str
) -> ModuleType:
    """Convert a token stream using `expect` to a module and return it."""
    modified_tokens = _modify_tokens(tokens)
    modified_str = untokenize(modified_tokens).decode("utf-8")
    module = ModuleType(module_name)
    exec(modified_str, module.__dict__)  # pylint: disable=exec-used
    return module


def _modify_tokens(tokens: Generator[TokenInfo, None, None]) -> List[TokenInfo]:
    """Modify a token stream to replace `except` with valid Python."""
    modified_tokens = []

    expect_nesting_level = 0
    offset = 0
    last_row = 0
    conditional_statement_nesting = 0
    nesting = []
    for token in tokens:
        if token.start[0] != last_row:
            offset = 0
            last_row = token.start[0]

        if token.type == NAME and token.string == "expect":
            # noinspection PyArgumentList
            pre = [
                TokenInfo(
                    NAME, "ret", token.start, _pad_pos(token.start, 3), token.line
                ),
                TokenInfo(
                    NAME,
                    "if",
                    _pad_pos(token.start, 4),
                    _pad_pos(token.start, 6),
                    token.line,
                ),
                TokenInfo(
                    OP,
                    "(",
                    _pad_pos(token.start, 7),
                    _pad_pos(token.start, 8),
                    token.line,
                ),
                TokenInfo(
                    NAME,
                    "ret",
                    _pad_pos(token.start, 8),
                    _pad_pos(token.start, 11),
                    token.line,
                ),
                TokenInfo(
                    OP,
                    ":=",
                    _pad_pos(token.start, 12),
                    _pad_pos(token.start, 14),
                    token.line,
                ),
            ]
            pre = [_add_offset(token, offset) for token in pre]
            modified_tokens.extend(pre)
            offset += 8
            nesting.append("expect")

        elif nesting and token.type == NEWLINE:
            raise ExpectParse("Encountered NEWLINE token while nested.")
        elif nesting and token.type == NAME and token.string == "if":
            nesting.append("conditional_statement")
            modified_tokens.append(_add_offset(token, offset))
        elif nesting and token.type == NAME and token.string == "else":
            if nesting[-1] == "conditional_statement":
                modified_tokens.append(_add_offset(token, offset))
            else:
                # noinspection PyArgumentList
                post = [
                    _add_offset(
                        TokenInfo(
                            OP,
                            ")",
                            _pad_pos(token.start, -1),
                            _pad_pos(token.start, 0),
                            token.line,
                        ),
                        offset,
                    ),
                    _add_offset(
                        TokenInfo(
                            NAME,
                            "is",
                            _pad_pos(token.start, 1),
                            _pad_pos(token.start, 3),
                            token.line,
                        ),
                        offset,
                    ),
                    _add_offset(
                        TokenInfo(
                            NAME,
                            "not",
                            _pad_pos(token.start, 4),
                            _pad_pos(token.start, 7),
                            token.line,
                        ),
                        offset,
                    ),
                    _add_offset(
                        TokenInfo(
                            NAME,
                            "None",
                            _pad_pos(token.start, 8),
                            _pad_pos(token.start, 12),
                            token.line,
                        ),
                        offset,
                    ),
                ]
                modified_tokens.extend(post)
                offset += 13
                modified_tokens.append(_add_offset(token, offset)),
            nesting.pop()
        else:
            modified_tokens.append(_add_offset(token, offset))

    return modified_tokens
