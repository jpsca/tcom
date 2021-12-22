import re
from typing import List
from xml.sax.saxutils import quoteattr


def to_camel_case(name: str) -> str:
    """Convert name to CamelCase

    Examples:

        >>> to_camel_case("device_type")
        'DeviceType'
        >>> to_camel_case("FooBar")
        'FooBar'

    """
    name = re.sub(r"[^A-Z^a-z^0-9^]+", r"_", name)
    return re.sub(r"(?:^|_)(.)", lambda m: m.group(1).upper(), name)


def to_snake_case(name: str) -> str:
    """Converts a "CamelCased" class name into its "snake_cased" version.

    Examples:

        >>> to_snake_case("LoremIpsum")
        'lorem_ipsum'
        >>> to_snake_case("lorem_ipsum")
        'lorem_ipsum'
        >>> to_snake_case("Singleword")
        'singleword'

    """
    name = re.sub(r"[^A-Z^a-z^0-9^]+", r"_", name)
    name = re.sub(r"([A-Z]+)([A-Z][a-z])", r"\1_\2", name)
    name = re.sub(r"([a-z\d])([A-Z])", r"\1_\2", name)
    return name.lower()


def split(ssl: str) -> List[str]:
    return re.split(r"\s+", ssl.strip())


def dedup(lst: List) -> List:
    return list(dict.fromkeys(lst))


def dedup_classes(ssl: str) -> str:
    return " ".join(dedup(split(ssl))).strip()


def get_html_attrs(attrs) -> str:
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
