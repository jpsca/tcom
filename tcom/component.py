import re
from keyword import iskeyword
from typing import Any

from .exceptions import InvalidProp, MissingRequiredAttr
r'^'

RX_PROPS_START = re.compile(r"{#-?\s*def\s+")
RX_PROP = re.compile(r"(\w+(?:,|=.+?,)?)", re.UNICODE)
RX_CSS_START = re.compile(r"{#-?\s*css\s+")
RX_JS_START = re.compile(r"{#-?\s*js\s+")
RX_META_END = re.compile(r"\s*-?#}")
RX_COMMA = re.compile(r"\s*,\s*")

ALLOWED_NAMES_IN_EXPRESSION_VALUES = {
    "len": len,
    "max": max,
    "min": min,
    "pow": pow,
    "sum": sum,
}


def eval_expression(input_string):
    code = compile(input_string, "<string>", "eval")
    for name in code.co_names:
        if name not in ALLOWED_NAMES_IN_EXPRESSION_VALUES:
            raise InvalidProp(f"Use of {name} not allowed")
    return eval(code, {"__builtins__": {}}, ALLOWED_NAMES_IN_EXPRESSION_VALUES)


def is_valid_variable_name(name):
    return name.isidentifier() and not iskeyword(name)


class Component:
    def __init__(self, *, name: str, source: str, url_prefix: str = "") -> None:
        self.name = name
        self.url_prefix = url_prefix
        self.required: "list[str]" = []
        self.optional: "dict[str, Any]" = {}
        self.css: "list[str]" = []
        self.js: "list[str]" = []
        self.parse_props(source)
        self.parse_css(source)
        self.parse_js(source)

    def parse_props(self, source: str) -> None:
        expr = self.load_metadata(source, RX_PROPS_START)
        if not expr:
            return
        required, optional = self.parse_props_expr(expr)
        self.required = required
        self.optional = optional

    def parse_css(self, source: str) -> None:
        css_expr = self.load_metadata(source, RX_CSS_START)
        if not css_expr:
            return
        self.css = self.parse_files_expr(css_expr)

    def parse_js(self, source: str) -> None:
        js_expr = self.load_metadata(source, RX_JS_START)
        if not js_expr:
            return
        self.js = self.parse_files_expr(js_expr)

    def load_metadata(self, source: str, rx_start: re.Pattern) -> str:
        start = rx_start.search(source)
        if not start:
            return ""
        end = RX_META_END.search(source, pos=start.end())
        if not end:
            raise InvalidProp(self.name)
        return source[start.end() : end.start()].strip()

    def parse_props_expr(self, expr: str) -> "tuple[list[str], dict[str, Any]]":
        required = []
        optional = {}

        expr = f"{expr},"  # To match the last prop with the regexp
        for key in RX_PROP.findall(expr):
            key = key.strip(",")

            if "=" in key:
                key, value = key.split("=")
                key = key.strip()
                if not is_valid_variable_name(key):
                    raise InvalidProp(
                        self.name, f"`{key}` is not a valid attribute name"
                    )

                value = value.strip()
                # Jinja allows using lowercase booleans, so we do
                # it too for consistency
                if value == "false":
                    value = "False"
                elif value == "true":
                    value = "True"

                optional[key] = eval_expression(value)
            else:
                key = key.strip()
                if not is_valid_variable_name(key):
                    raise InvalidProp(
                        self.name, f"`{key}` is not a valid attribute name"
                    )
                if optional:
                    raise InvalidProp(
                        self.name, "Required argument follows optional argument"
                    )
                if key in required:
                    raise InvalidProp(self.name, "Duplicated argument")

                required.append(key)

        return required, optional

    def parse_files_expr(self, expr: str) -> "list[str]":
        files = []
        for url in RX_COMMA.split(expr):
            url = url.strip("\"'/")
            if url:
                files.append(f"{self.url_prefix}{url}")
        return files

    def filter_args(
        self, kw: "dict[str, Any]"
    ) -> "tuple[dict[str, Any], dict[str, Any]]":
        props = {}

        for key in self.required:
            if key not in kw:
                raise MissingRequiredAttr(self.name, key)
            props[key] = kw.pop(key)

        for key, default_value in self.optional.items():
            props[key] = kw.pop(key, default_value)
        extra = kw.copy()
        return props, extra

    def __repr__(self) -> str:
        return f'<Component "{self.name}">'
