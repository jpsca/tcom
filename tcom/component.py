import re
from typing import Any

import tomlkit
import uuid

from .exceptions import InvalidFrontMatter, MissingRequiredAttr


FRONT_MATTER_START = "{#"
FRONT_MATTER_END = "#}"
CSS_KEY = "css"
JS_KEY = "js"

RX_REQUIRED = re.compile(r"=\s*(?:\.\.\.|…)(\s+\n?)")


class Component:
    __slots__ = ("args", "css", "js", "name", "required")

    def __init__(self, *, name: str, url_prefix: str, source: str) -> None:
        self.name = name

        placeholder = f"required-{uuid.uuid4().hex}"
        fmdict = self.load_front_matter(source, placeholder)

        css = []
        for url in fmdict.pop(CSS_KEY, []):
            url = url.strip("/")
            css.append(f"{url_prefix}{url}")
        self.css = css

        js = []
        for url in fmdict.pop(JS_KEY, []):
            url = url.strip("/")
            js.append(f"{url_prefix}{url}")
        self.js = js

        args = {}
        required = set()
        for name, default in fmdict.items():
            if default == placeholder:
                required.add(name)
            else:
                args[name] = default

        self.args = args
        self.required = required

    def load_front_matter(self, source: str, placeholder: str) -> "dict[str, Any]":
        if not source.startswith(FRONT_MATTER_START):
            return {}
        front_matter = source.split(FRONT_MATTER_END, 1)[0]
        front_matter = (
            front_matter[2:]
            .strip("-")
            .replace(" False\n", " false\n")
            .replace(" True\n", " true\n")
        )
        front_matter = RX_REQUIRED.sub(f"= '{placeholder}'\\1", front_matter)
        try:
            return tomlkit.parse(front_matter)
        except tomlkit.exceptions.TOMLKitError as err:
            raise InvalidFrontMatter(self.name, *err.args)

    def filter_args(
        self, kw: "dict[str, Any]"
    ) -> "tuple[dict[str, Any], dict[str, Any]]":
        props = {}

        for attr in self.required:
            if attr not in kw:
                raise MissingRequiredAttr(self.name, attr)
            props[attr] = kw.pop(attr)

        for attr, default_value in self.args.items():
            props[attr] = kw.pop(attr, default_value)
        extra = kw.copy()
        return props, extra

    def __repr__(self) -> str:
        return f'<Component "{self.name}">'
