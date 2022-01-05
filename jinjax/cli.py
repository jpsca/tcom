#!/usr/bin/env python
"""
JinjaX CLI

Usage: jinjax new <ComponentName>

This will create an empty component in the current folder.
"""
import sys
import textwrap
from pathlib import Path
from typing import Any, Callable, Dict, List, Tuple

from .utils import to_camel_case, to_snake_case


def run() -> None:  # pragma: no cover
    _, *sargs = sys.argv
    if not sargs:
        return show_help()

    cmd = sargs[0]
    sargs = sargs[1:]
    if cmd == "help":
        return show_help()

    func = COMMANDS.get(cmd)
    if not func:
        return show_help()

    args, kwargs = parse_args(sargs)

    if kwargs.get("help") is True:
        return show_cmd_help(func)

    func(*args, **kwargs)


def parse_args(sargs: List[str]) -> Tuple[List[str], Dict[str, Any]]:
    """A limited but flexible argument parser

    Can:
    - Parse positional named arguments (like `--a 1`) and flags (like `--quiet`).

    Cannot:
    - Cannot parse repeated arguments, like  `--a 1 --a 2`
    - Doesn't support False flags like `--no-quiet`
    - Cannot typecast values, everything is a string, except for flags

    Examples:

    >>> parse_args(["a", "--foo", "bar", "b", "--lorem", "ipsum", "--flag"])
    (['a', 'b'], {'foo': 'bar', 'lorem': 'ipsum', 'flag': True})

    >>> parse_args(["a", "b", "c"])
    (['a', 'b', 'c'], {})

    >>> parse_args(["--flag", "--name", "meh"])
    ([], {'flag': True, 'name': 'meh'})

    >>> parse_args(["--a", "1", "--a", "2"])
    ([], {'a': '2'})

    """
    args: List[str] = []
    kwargs: Dict[str, Any] = {}
    named = None

    for part in sargs:
        if part.startswith("--"):
            if named:
                kwargs[named] = True
            named = part.lstrip("-")
            continue
        if named:
            kwargs[named] = part
            named = None
        else:
            args.append(part)

    if named:
        kwargs[named] = True

    return args, kwargs


def show_help() -> None:  # pragma: no cover
    """Show the global help."""
    doc = __doc__ or ""
    doc = textwrap.dedent(doc.lstrip())
    print(doc)


def show_cmd_help(func: Callable) -> None:  # pragma: no cover
    """Show the help of a command."""
    doc = func.__doc__ or ""
    doc = textwrap.dedent(f"\n    {doc.lstrip()}")
    print(doc)


INIT_TMPL = """from jinjax import Component


class CNAME(Component):
    # uses = {...}
    # css = [...]
    # js = [...]
    pass
"""


def new(name: str, path: str = ".") -> None:
    """
    Usage: jinjax new <ComponentName> [--path .]

    Create an empty component in the current folder.
    You can optionally define the root path of the components
    with the `--path PATH` option.
    """
    class_name = to_camel_case(name)
    snake_name = to_snake_case(class_name)
    root = Path(f"{path}/{snake_name}")

    root.mkdir(parents=False, exist_ok=False)

    init_file = (root / "__init__.py")
    print("✨", init_file)
    init_file.touch(exist_ok=False)
    code = INIT_TMPL.replace("CNAME", class_name)
    init_file.write_text(code)

    tmpl_file = (root / f"{class_name}.html.jinja")
    print("✨", tmpl_file)
    tmpl_file.touch(exist_ok=False)


COMMANDS: Dict[str, Callable] = {
    "new": new
}
