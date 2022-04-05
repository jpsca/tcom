from typing import Any

import tomlkit

from .exceptions import MissingRequiredAttr


FRONT_MATTER_START = "{#"
FRONT_MATTER_END = "#}"
CSS_KEY = "css"
JS_KEY = "js"
REQUIRED_VALUE = "___"
EXTRA_ATTRS_KEY = "_extra_attrs"


class Component:
    __slots__ = ("relpath", "args", "required", "css", "js")

    def __init__(self, *, relpath: str, content: str = "", prefix: str = "") -> None:
        self.relpath = relpath
        fmdict = self.load_front_matter(content)

        prefix = prefix.strip("/")
        if prefix:
            prefix += "/"
        self.css = set([f"{prefix}{css.strip('/')}" for css in fmdict.pop(CSS_KEY, [])])
        self.js = set([f"{prefix}{js.strip('/')}" for js in fmdict.pop(JS_KEY, [])])

        args = {}
        required = set()
        for name, default in fmdict.items():
            if default == REQUIRED_VALUE:
                required.add(name)
            else:
                args[name] = default

        self.args = args
        self.required = required

    def load_front_matter(self, content: str) -> dict[str, Any]:
        if not content.startswith(FRONT_MATTER_START):
            return {}
        front_matter = content.split(FRONT_MATTER_END, 1)[0]
        front_matter = front_matter[2:].strip("-")
        return tomlkit.parse(front_matter)

    def filter_args(self, kwargs: dict[str, Any]) -> dict[str, Any]:
        props = {}

        for name in self.required:
            if name not in kwargs:
                raise MissingRequiredAttr(name)
            props[name] = kwargs.pop(name)

        for name, default_value in self.args.items():
            props[name] = kwargs.pop(name, default_value)

        props[EXTRA_ATTRS_KEY] = kwargs.copy()
        return props

    def __repr__(self):
        return f'<Component "{self.relpath}">'
