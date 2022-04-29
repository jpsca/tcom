import re
from typing import Any
from xml.sax.saxutils import quoteattr


def split(ssl: str) -> "list[str]":
    return re.split(r"\s+", ssl.strip())


def dedup(lst: "list") -> "list":
    return list(dict.fromkeys(lst))


def dedup_classes(ssl: str) -> str:
    return " ".join(dedup(split(ssl))).strip()


def get_html_attrs(attrs: "dict[str, Any]") -> str:
    """Generate HTML attributes from the provided attributes.

    - To provide consistent output, the attributes and properties are sorted by name
      and rendered like this: `<sorted attributes> + <sorted properties>`.
    - All underscores are translated to regular dashes.
    - Set properties with a `True` value.
        >>> get_html_attrs({
        ...     "id": "text1",
        ...     "class": "myclass",
        ...     "data_id": 1,
        ...     "checked": True,
        ... })
        'class="myclass" data-id="1" id="text1" checked'

    """
    attributes_list = []
    properties_list = []

    for key, value in attrs.items():
        key = key.replace("_", "-")
        if value is True:
            properties_list.append(key)
        elif value not in (False, None):
            value = quoteattr(str(value))
            attributes_list.append("{}={}".format(key, value))

    attributes_list.sort()
    properties_list.sort()
    attributes_list.extend(properties_list)
    return " ".join(attributes_list)
