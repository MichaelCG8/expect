# expect
`expect` allows clean handling of Optional return types.
The purpose of the package is to experiment with the idea of adding an expect-else clause to Python.
The intention is to call a function and take some action if the return type is not `None` (the expected result), 
and some other action if the return type is `None`.

## Example usage

    def func() -> Optional[Tuple[int, int]]:
	    return 1, 2

### In conditional expressions

    a, b = expect func() else (0, 0)

equivalent to:

    ret = func()
    a, b = ret if ret is not None else (0, 0)

or, with Python >= 3.8:

    a, b = ret if (ret := func()) is not None else (0, 0)

### Complex blocks

    a, b = expect func else:
        print("func() returned None!")
        other_stuff()
        # a, b = something_else
        # return some_value

equivalent to:

    ret = func()
    if ret is not None:
        a, b = ret
    else:
        print("func() returned None!")
        other_stuff()
        # a, b = something_else
        # return some_value

or, with Python >= 3.8:

    if (ret := func()) is not None:
        a, b = ret
    else:
        print("func() returned None!")
        other_stuff()
        # a, b = something_else
        # return some_value


### Use with a return statement

    a, b = expect func() else:
        return

equivalent to:
    
    ret = func()
    if ret is not None:
        a, b = ret
    else:
        return

or, with Python >= 3.8:

    if (ret := func()) is not None:
        a, b = ret
    else:
        return

## Roadmap

### Complex block syntax

An alternative to:

    a, b = expect func() else:
        stuff()

that is currently under consideration is:

    a, b = expect func()
    else:
        stuff()

It is possible that both will be supported at some point.

### None propagation

A helper construct `prop` or `expect.prop` could be used to propagate return values:

    a, b = expect.prop func()

equivalent to:

    a, b = expect.prop func() else:
        return

