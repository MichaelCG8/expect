from io import BytesIO
from tokenize import tokenize, untokenize

from expect.importer import _modify_tokens


def modify_string(src: str) -> str:
    """Modify a source string"""
    dummy_file_obj = BytesIO(src.strip("\r\n").encode("utf-8"))
    modified_tokens = _modify_tokens(tokenize(dummy_file_obj.readline))
    modified_str = untokenize(modified_tokens).decode("utf-8")
    return modified_str
