#!/usr/bin/env python
"""
JinjaX CLI

Usage: jinjax new <ComponentName>

This will create an empty component in the current folder.
"""
import sys
import textwrap
from pathlib import Path

from .utils import to_camel_case, to_snake_case


def run() -> None:  # pragma: no cover
    _, *args = sys.argv
    if not args:
        return show_help()

    cmd = args[0]
    args = args[1:]
    if cmd == "help":
        return show_help()

    func = COMMANDS.get(cmd)
    if not func:
        return show_help()
    if args and args[-1] == "--help":
        return show_cmd_help(func)

    func(*args)


def show_help() -> None:  # pragma: no cover
    doc = textwrap.dedent(__doc__)
    print(textwrap.indent(doc, "  "))


def show_cmd_help(func) -> None:  # pragma: no cover
    doc = textwrap.dedent(func.__doc__)
    print(textwrap.indent(doc, "  "))


INIT_TMPL = """from jinjax import Component


class CN(Component):
    # uses = {...}
    # css = {...}
    # js = {...}
    pass
"""


def new(name) -> None:
    """Usage: jinjax new <ComponentName>

    Create an empty component in the current folder.
    """
    class_name = to_camel_case(name)
    snake_name = to_snake_case(class_name)
    root = Path(f"./{snake_name}")

    root.mkdir(parents=False, exist_ok=False)

    init_file = (root / "__init__.py")
    print("✨", init_file)
    init_file.touch(exist_ok=False)
    code = INIT_TMPL.replace("CN", class_name)
    init_file.write_text(code)

    tmpl_file = (root / f"{class_name}.html.jinja")
    print("✨", tmpl_file)
    tmpl_file.touch(exist_ok=False)


COMMANDS = {
    "new": new
}
