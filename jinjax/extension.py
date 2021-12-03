import re
from typing import List, Optional, Tuple

from jinja2 import Environment
from jinja2.ext import Extension


START_CALL = "{% call <TAG>.new(<ATTRS>) -%}"
END_CALL = "{%- endcall %}"
INLINE_CALL = "{{ <TAG>.new(<ATTRS>) }}"

VAR_START = "VAR_START"
VAR_END = "VAR_END"

rx_open_tag = re.compile(r"<\s*[A-Z][0-9A-Za-z]*[^\>]*>")
rx_close_tag = re.compile(r"</\s*[A-Z][0-9A-Za-z]*\s*>")
re_attr = rf"""
(?P<name>[a-zA-Z][0-9a-zA-Z]*)
(?:\s*=\s*
    (?P<value>(?:".*"|{VAR_START}.*{VAR_END}))
)?
"""


class JinjaX(Extension):
    def __init__(self, environment: Environment) -> None:
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
        name: Optional[str] = None,
        filename: Optional[str] = None,
    ) -> str:
        source = rx_open_tag.sub(self._process_tag, source)
        source = rx_close_tag.sub(END_CALL, source)
        return source

    def _process_tag(self, match: re.Match) -> str:
        ht = match.group()
        tag, attrs_list = self._extract_tag(ht)
        return self._build_call(tag, attrs_list, inline=ht.endswith("/>"))

    def _extract_tag(self, ht: str) -> Tuple[str, List[Tuple[str, str]]]:
        tag, *raw = ht.strip("<> \r\n/").split(" ", 1)
        tag = tag.strip()
        attrs_list = []
        if raw:
            attrs_list = self.rx_attr.findall(raw[0])
        return tag, attrs_list

    def _build_call(
        self,
        tag: str,
        attrs_list: List[Tuple[str, str]],
        inline: bool = False,
    ) -> str:
        attrs = []
        for name, value in attrs_list:
            name = name.strip()
            if not value:
                attrs.append(f"{name}=True")
            elif value.startswith(self.var_start):
                value = value[len(self.var_start):-len(self.var_end)]
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
