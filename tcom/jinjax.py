import re
from typing import TYPE_CHECKING

from jinja2.ext import Extension

if TYPE_CHECKING:
    from typing import Optional
    from jinja2 import Environment


RENDER_CMD = "__render"
START_CALL = '{% call <CMD>("<TAG>", <ATTRS>) -%}'
START_CALL = START_CALL.replace("<CMD>", RENDER_CMD)
END_CALL = "{%- endcall %}"
INLINE_CALL = '{{ <CMD>("<TAG>", <ATTRS>) }}'
INLINE_CALL = INLINE_CALL.replace("<CMD>", RENDER_CMD)

VAR_START = "VAR_START"
VAR_END = "VAR_END"
DEBUG_ATTR_NAME = "__source"

re_tag_name = r"([0-9A-Za-z_-]+\.)*[A-Z][0-9A-Za-z_-]*"
re_raw_attrs = r"[^\>]*"
re_open_tag = fr"<\s*{re_tag_name}{re_raw_attrs}>"
rx_open_tag = re.compile(re_open_tag, re.VERBOSE)

re_close_tag = fr"</\s*{re_tag_name}\s*>"
rx_close_tag = re.compile(re_close_tag, re.VERBOSE)

re_attr_name = r"(?P<name>[a-zA-Z_][0-9a-zA-Z_]*)"
re_equal = r"\s*=\s*"

re_attr = rf"""
{re_attr_name}
(?:
    {re_equal}
    (?P<value>".*?"|'.*?'|{VAR_START}.*?{VAR_END})
)?
"""


class JinjaX(Extension):
    def __init__(self, environment: "Environment") -> None:
        super().__init__(environment)

        self.var_start = environment.variable_start_string
        self.var_end = environment.variable_end_string
        _re_attr = (
            re_attr
            .replace(VAR_START, re.escape(self.var_start))
            .replace(VAR_END, re.escape(self.var_end))
        )
        self.rx_attr = re.compile(_re_attr, re.VERBOSE)

    def preprocess(
        self,
        source: str,
        name: "Optional[str]" = None,
        filename: "Optional[str]" = None,
    ) -> str:
        source = rx_open_tag.sub(self._process_tag, source)
        source = rx_close_tag.sub(END_CALL, source)
        setattr(self.environment, DEBUG_ATTR_NAME, source)  # type: ignore
        return source

    def _process_tag(self, match: "re.Match") -> str:
        ht = match.group()
        tag, attrs_list = self._extract_tag(ht)
        return self._build_call(tag, attrs_list, inline=ht.endswith("/>"))

    def _extract_tag(self, ht: str) -> "tuple[str, list[tuple[str, str]]]":
        ht = ht.strip("<> \r\n/")
        tag, *raw = re.split(r"\s+", ht, maxsplit=1)
        tag = tag.strip()
        attrs_list = []
        if raw:
            _raw = raw[0].replace("\n", " ").strip()
            if _raw:
                attrs_list = self.rx_attr.findall(_raw)
        return tag, attrs_list

    def _build_call(
        self,
        tag: str,
        attrs_list: "list[tuple[str, str]]",
        inline: bool = False,
    ) -> str:
        attrs = []
        for name, value in attrs_list:
            name = name.strip()
            if not value:
                attrs.append(f"{name}=True")
            elif value.startswith(self.var_start):
                value = value[len(self.var_start) : -len(self.var_end)]
                attrs.append(f"{name}={value.strip()}")
            else:
                attrs.append(f"{name}={value.strip()}")

        if inline:
            return INLINE_CALL \
                .replace("<TAG>", tag) \
                .replace("<ATTRS>", ", ".join(attrs))

        return START_CALL \
            .replace("<TAG>", tag) \
            .replace("<ATTRS>", ", ".join(attrs))
