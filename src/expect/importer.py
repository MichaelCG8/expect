import importlib
import sys
from tokenize import tokenize, untokenize, TokenInfo, NAME, NEWLINE, OP
from types import ModuleType
from typing import Tuple


def _add_offset(token: TokenInfo, offset: int) -> TokenInfo:
    new_start = (token.start[0], token.start[1] + offset)
    new_end = (token.end[0], token.end[1] + offset)
    return TokenInfo(token.type, token.string, new_start, new_end, token.line)


def _pad_pos(pos: Tuple[int, int], offset: int) -> Tuple[int, int]:
    return pos[0], pos[1] + offset


# TODO: Current status:
#       supports `a, b = expect func() else (0, 0)` so long as func is not replaced by something with multiple `)`
def expect_import(module_name: str) -> ModuleType:
    # First, try to import the module without parsing except clauses.
    # If this succeeds, except is not used and the module can be returned immediately.
    # If this fails, get the path of the module and parse the except clauses.
    try:
        module = importlib.import_module(module_name)  # TODO: Read up on how import_module works.
        return module
    except SyntaxError as e:
        module_path = e.filename

    with open(module_path, "rb") as f:
        tokens = tokenize(f.readline)

    module = _tokens_to_module(tokens, module_name)
    sys.modules[module_name] = module

    return module


def _tokens_to_module(tokens, module_name: str):
    edited_str = _modify_tokens(tokens)
    module = ModuleType(module_name)
    exec(edited_str, module.__dict__)
    return module


def _modify_tokens(tokens):
    edited_tokens = []

    in_expect = False
    offset = 0
    for token in tokens:
        if token.type == NAME and token.string == "expect":
            pre = [
                TokenInfo(NAME, "ret", token.start, _pad_pos(token.start, 3), token.line),
                TokenInfo(NAME, "if", _pad_pos(token.start, 4), _pad_pos(token.start, 6), token.line),
                TokenInfo(OP, "(", _pad_pos(token.start, 7), _pad_pos(token.start, 8), token.line),
                TokenInfo(NAME, "ret", _pad_pos(token.start, 8), _pad_pos(token.start, 11), token.line),
                TokenInfo(OP, ":=", _pad_pos(token.start, 12), _pad_pos(token.start, 14), token.line),
            ]
            offset += 8
            edited_tokens.extend(pre)
            in_expect = True
        elif in_expect and token.type == OP and token.string == ")":
            edited_tokens.append(_add_offset(token, offset))
            edited_tokens.append(_add_offset(TokenInfo(OP, ")", token.end, _pad_pos(token.end, 1), token.line), offset))
            edited_tokens.append(_add_offset(TokenInfo(NAME, "is", _pad_pos(token.end, 2), _pad_pos(token.end, 4), token.line), offset))
            edited_tokens.append(_add_offset(TokenInfo(NAME, "not", _pad_pos(token.end, 5), _pad_pos(token.end, 8), token.line), offset))
            edited_tokens.append(_add_offset(TokenInfo(NAME, "None", _pad_pos(token.end, 9), _pad_pos(token.end, 13), token.line), offset))
            offset += 13
            in_expect = False
        else:
            edited_tokens.append(_add_offset(token, offset))
            if token.type == NEWLINE:
                offset = 0

    return untokenize(edited_tokens).decode("utf-8")
