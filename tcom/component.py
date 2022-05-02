from typing import TYPE_CHECKING

import tomlkit

from .exceptions import InvalidFrontMatter, MissingRequiredAttr

if TYPE_CHECKING:
    from pathlib import Path
    from typing import Any


FRONT_MATTER_START = "{#"
FRONT_MATTER_END = "#}"
CSS_KEY = "css"
JS_KEY = "js"
REQUIRED_VALUE = "..."


class Component:
    __slots__ = (
        "args",
        "css",
        "js",
        "name",
        "path",
        "prefix",
        "relpath",
        "required",
    )

    def __init__(
        self,
        *,
        name: str,
        path: "Path",
        relpath: str,
        content: str = "",
        prefix: str = "",
    ) -> None:
        self.name = name
        self.path = path
        self.relpath = relpath
        fmdict = self.load_front_matter(content)

        prefix = prefix.strip(".").strip("/")
        if prefix:
            prefix += "/"
        self.prefix = prefix

        css = []
        for url in fmdict.pop(CSS_KEY, []):
            if not url.startswith("/"):
                url = f"{prefix}{url.strip('/')}"
            css.append(url.strip("/"))
        self.css = css

        js = []
        for url in fmdict.pop(JS_KEY, []):
            if not url.startswith("/"):
                url = f"{prefix}{url.strip('/')}"
            js.append(url.strip("/"))
        self.js = js

        args = {}
        required = set()
        for name, default in fmdict.items():
            if default == REQUIRED_VALUE:
                required.add(name)
            else:
                args[name] = default

        self.args = args
        self.required = required

    def load_front_matter(self, content: str) -> "dict[str, Any]":
        if not content.startswith(FRONT_MATTER_START):
            return {}
        front_matter = content.split(FRONT_MATTER_END, 1)[0]
        front_matter = (
            front_matter[2:]
            .strip("-")
            .replace(" False\n", " false\n")
            .replace(" True\n", " true\n")
        )
        try:
            return tomlkit.parse(front_matter)
        except tomlkit.exceptions.TOMLKitError as err:
            raise InvalidFrontMatter(self.name, *err.args)

    def filter_args(
        self, kw: "dict[str, Any]"
    ) -> "tuple[dict[str, Any], dict[str, Any]]":
        props = {}

        for name in self.required:
            if name not in kw:
                raise MissingRequiredAttr(self.name, name)
            props[name] = kw.pop(name)

        for name, default_value in self.args.items():
            props[name] = kw.pop(name, default_value)

        extra = kw.copy()
        return props, extra

    def get_source(self) -> str:
        return self.path.read_text()

    def __repr__(self) -> str:
        return f'<Component "{self.relpath}">'
