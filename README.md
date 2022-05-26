# expect
`expect` allows clean handling of Optional return types.
The purpose of the package is to experiment with the idea of adding an expect-else clause to Python.
The intention is to call a function and take some action if the return type is not `None` (the expected result), 
and some other action if the return type is `None`.

## Example usage

    def func_2_tuple() -> Optional[Tuple[int, int]]:
	    return 1, 2

    def func_none() -> Optional[Tuple[int, int]]:
        return None

### In conditional expressions

    a, b = expect func_2_tuple() else (0, 0)

equivalent to:

    ret = func_2_tuple()
    a, b = ret if ret is not None else (0, 0)

or, with Python >= 3.8:

    a, b = ret if (ret := func_2_tuple()) is not None else (0, 0)

### Complex blocks

    a, b = expect func_2_tuple else:
        print("func_2_tuple() returned None!")
        other_stuff()
        # a, b = something_else
        # return some_value

equivalent to:

    ret = func_2_tuple()
    if ret is not None:
        a, b = ret
    else:
        print("func_2_tuple() returned None!")
        other_stuff()
        # a, b = something_else
        # return some_value

or, with Python >= 3.8:

    if (ret := func_2_tuple()) is not None:
        a, b = ret
    else:
        print("func_2_tuple() returned None!")
        other_stuff()
        # a, b = something_else
        # return some_value


### Use with a return statement

    a, b = expect func_2_tuple() else:
        return

equivalent to:
    
    ret = func_2_tuple()
    if ret is not None:
        a, b = ret
    else:
        return

or, with Python >= 3.8:

    if (ret := func_2_tuple()) is not None:
        a, b = ret
    else:
        return

## No else

Without an else, an `UnmetExpectation` is raised.

    a, b = expect func_none()

## Roadmap

### Complex block syntax

An alternative to:

    a, b = expect func_2_tuple() else:
        stuff()

that is currently under consideration is:

    a, b = expect func_2_tuple()
    else:
        stuff()

It is possible that both will be supported at some point.

### None propagation

A helper construct `prop` or `expect.prop` could be used to propagate return values:

    a, b = expect.prop func_2_tuple()

equivalent to:

    a, b = expect.prop func_2_tuple() else:
        return

## TODO

- Improve the quality of the repository.

  https://dev.to/eludadev/take-your-github-repository-to-the-next-level-17ge

  https://pythonbytes.fm/episodes/show/281/ohmyzsh-ohmyposh-mcfly-pls-nerdfonts-wow
- Implement all syntaxes and make robust to different whitespace, parentheses, etc.
- Test heavily.
- Profile difference in module load time.

