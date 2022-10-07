import re

from jinja2.ext import Extension


RENDER_CMD = "__render"
START_CALL = '{% call <CMD>("<TAG>", <ATTRS>) -%}'
START_CALL = START_CALL.replace("<CMD>", RENDER_CMD)
END_CALL = "{%- endcall %}"
INLINE_CALL = '{{ <CMD>("<TAG>", <ATTRS>) }}'
INLINE_CALL = INLINE_CALL.replace("<CMD>", RENDER_CMD)

ATTR_START = "{"
ATTR_END = "}"
DEBUG_ATTR_NAME = "__source"

re_tag_name = r"([0-9A-Za-z_-]+\.)*[A-Z][0-9A-Za-z_-]*"
re_raw_attrs = r"[^\>]*"
re_open_tag = fr"<\s*{re_tag_name}{re_raw_attrs}>"
RX_OPEN_TAG = re.compile(re_open_tag, re.VERBOSE)

re_close_tag = fr"</\s*{re_tag_name}\s*>"
RX_CLOSE_TAG = re.compile(re_close_tag, re.VERBOSE)

re_attr_name = r"(?P<name>[a-zA-Z_][0-9a-zA-Z_]*)"
re_equal = r"\s*=\s*"

re_attr = rf"""
{re_attr_name}
(?:
    {re_equal}
    (?P<value>".*?"|'.*?'|\{ATTR_START}.*?\{ATTR_END})
)?
"""
RX_ATTR = re.compile(re_attr, re.VERBOSE)


class JinjaX(Extension):
    def preprocess(self, source: str, *args, **kw) -> str:
        source = RX_OPEN_TAG.sub(self._process_tag, source)
        source = RX_CLOSE_TAG.sub(END_CALL, source)
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
            attrs_list = self._parse_attrs(raw[0])
        return tag, attrs_list

    def _parse_attrs(self, raw: str) -> "list[tuple[str, str]]":
        raw = raw.replace("\n", " ").strip()
        if not raw:
            return []
        return RX_ATTR.findall(raw)

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
            else:
                attrs.append(f"{name}={value.strip(' {}')}")

        if inline:
            return INLINE_CALL \
                .replace("<TAG>", tag) \
                .replace("<ATTRS>", ", ".join(attrs))

        return START_CALL \
            .replace("<TAG>", tag) \
            .replace("<ATTRS>", ", ".join(attrs))
