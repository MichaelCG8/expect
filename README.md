# expect

| Symbol                   | Meaning               |
|--------------------------|-----------------------|
| :heavy_check_mark:       | Implemented           |
| :hourglass_flowing_sand: | Partially implemented |
| :x:                      | Not yet implemented   |

`expect` allows clean handling of `Optional` return types.
The purpose of the package is to experiment with the idea of adding an `expect-else`
clause to Python.
The intention is to call a function and take some action if the return type is not
`None` (the expected result), and some fallback/special-case action if the return type
is `None`.

For now, only Python >= 3.8 is supported, due to usages of `expect` being internally
replaced by code using the walrus operator.
## Example usage

    def func_2_tuple() -> Optional[Tuple[int, int]]:
	    return 1, 2

    def func_none() -> Optional[Tuple[int, int]]:
        return None

### In conditional expressions :hourglass_flowing_sand:<!--Partially implemented-->

    a, b = expect func_2_tuple() else (0, 0)

    # Equivalent Python < 3.8:
    ret = func_2_tuple()
    a, b = ret if ret is not None else (0, 0)

    # Equivalent Python >= 3.8:
    a, b = ret if (ret := func_2_tuple()) is not None else (0, 0)

This also works where a conditional expression is the `expect` condition.

    a, b = expect (1, 1) if something else None else (0, 0)

    # Equivalent Python < 3.8:
    ret = (1, 1) if something else None
    a, b = ret if ret is not None else (0, 0)

    # Equivalent Python >= 3.8:
    a, b = ret if (ret := (1, 1) if something else None) is not None else (0, 0)

### Complex blocks :x:<!--Not implemented-->

    a, b = expect func_2_tuple else:
        print("func_2_tuple() returned None!")
        other_stuff()
        # a, b = something_else
        # return some_value

    # Equivalent Python < 3.8:
    ret = func_2_tuple()
    if ret is not None:
        a, b = ret
    else:
        print("func_2_tuple() returned None!")
        other_stuff()
        # a, b = something_else
        # return some_value

    # Equivalent Python >= 3.8:
    if (ret := func_2_tuple()) is not None:
        a, b = ret
    else:
        print("func_2_tuple() returned None!")
        other_stuff()
        # a, b = something_else
        # return some_value


### Use with a return statement :x:<!--Not implemented-->

    a, b = expect func_2_tuple() else:
        return

    # Equivalent Python < 3.8:
    ret = func_2_tuple()
    if ret is not None:
        a, b = ret
    else:
        return

    # Equivalent Python >= 3.8:
    if (ret := func_2_tuple()) is not None:
        a, b = ret
    else:
        return

## No else :x:<!--Not implemented-->

Without an else, an `UnmetExpectation` is raised.

    a, b = expect func_none()

## `expect` as a condition

The result of `expect` can be used as a condition.

For example, as the condition of an `if` or `while` of the form:

    if expect func() else 1:
        ...

    while expect func():
        ...

Similarly, an `expect` can form the condition of another `expect`,
although the code is not very readable and so is not recommended.

    a, b = expect expect func_2_tuple() else (0, 0) else (1, 1)

    # Equivalent Python < 3.8
    ret1 = expect func_2_tuple() else (0, 0)
    a, b = ret1 if ret1 is not None else (1, 1)

    ret2 = func_2_tuple()
    ret1 = ret2 if ret2 is not None else (0, 0)
    a, b = ret1 if ret1 is not None else (1, 1)


    # Equivalent Python >= 3.8
    a, b = ret1 if (ret1 := expect func_2_tuple() else (0, 0)) else (1, 1)
    a, b = ret1 if (ret1 := ret2 if (ret2 := func_2_tuple()) else (0, 0)) else (1, 1)

## Roadmap

### Complex block syntax :x:<!--Not implemented-->

An alternative to:

    a, b = expect func_2_tuple() else:
        stuff()

that is currently under consideration is:

    a, b = expect func_2_tuple()
    else:
        stuff()

It is possible that both will be supported at some point.

### None propagation :x:<!--Not implemented-->

A helper construct `prop` or `expect.prop` could be used to propagate return values:

    a, b = expect.prop func_2_tuple()

    # Equivalent Python < 3.8:
    a, b = expect.prop func_2_tuple() else:
        return

## Design

For the initial exploration a file using `expect` must be loaded from another scope
using an `expect` importer function.
A single file can be loaded in this way. A package or submodule consisting of multiple
files is a task in the backlog.
Later versions aim to have this mechanism embedded in the file that contains code using
`expect` so that code importing this can be unaware of `expect`'s use.

The initial process is:

1. A call to the `expect` importer is made using `expect.expect_import()`.
2. The importer identifies the target module in the file system and reads its contents
   into a string.
3. The string is tokenized.
4. The `expect` usages are replaced by valid python.
5. The token stream is converted back to a string.
6. A new module object is created and the string is executed in that module's namespace.
7. The module is returned to the importing scope.

### TODO

- Improve the quality of the repository.

  https://dev.to/eludadev/take-your-github-repository-to-the-next-level-17ge

  https://pythonbytes.fm/episodes/show/281/ohmyzsh-ohmyposh-mcfly-pls-nerdfonts-wow
- Implement all syntaxes and make robust to different whitespace, parentheses, etc.
- Test heavily.
- Profile difference in module load time.
- Record the positions of the `expect` tokens and their replacements.
  Convert the modified string code to an AST and manipulate so that the original
  positions are reported in the event of an exception. Note that Python's 'ast' module
  cannot parse code using `expect` since it is invalid syntax.
- Can the AST be manipulated so that in the event of an Exception the traceback presents
  the code using `expect`?
