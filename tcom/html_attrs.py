import re
from typing import Any, Optional
from xml.sax.saxutils import quoteattr


CLASS_KEY = "class"
CLASS_ALT_KEY = "classes"


def split(ssl: str) -> "list[str]":
    return re.split(r"\s+", ssl.strip())


class HTMLAttrs:
    def __init__(self, attrs) -> None:
        attributes: "dict[str, str]" = {}
        properties: "set[str]" = set()

        class_names = split(" ".join([
            attrs.pop(CLASS_KEY, ""),
            attrs.get(CLASS_ALT_KEY, ""),
        ]))
        self.__classes = {name for name in class_names if name}

        for name, value in attrs.items():
            name = name.replace("_", "-")
            if value is True:
                properties.add(name)
            elif value not in (False, None):
                attributes[name] = str(value)

        self.__attributes = attributes
        self.__properties = properties

    @property
    def classes(self):
        return " ".join(sorted(list(self.__classes)))

    @property
    def as_dict(self):
        attributes = self.__attributes.copy()
        classes = self.classes
        if classes:
            attributes[CLASS_KEY] = classes

        out = dict(sorted(attributes.items()))
        for name in sorted(list(self.__properties)):
            out[name] = True
        return out

    def add(self, name: str, value: "Any" = True) -> None:
        """
        Adds an attribute or sets a property.
        Pass a name and a value to set an attribute.
        Omit the value or use `True` as value to set a property instead
        """
        if name == "class":
            return self.add_class(value)

        name = name.replace("_", "-")
        if value is True:
            self.__properties.add(name)
        else:
            self.__attributes[name] = value

    def remove(self, name: str) -> None:
        """
        Removes an attribute or property."""
        name = name.replace("_", "-")
        if name in self.__attributes:
            del self.__attributes[name]
        if name in self.__properties:
            self.__properties.remove(name)

    def add_class(self, *names: str) -> None:
        """
        """
        for name in names:
            for name_ in split(name):
                self.__classes.add(name_)

    add_classes = add_class

    def remove_class(self, *names: str) -> None:
        """
        """
        for name in names:
            self.__classes.remove(name)

    remove_classes = remove_class

    def setdefault(self, name: str, value: "Any" = True) -> None:
        """
        Adds an attribute or sets a property, but only if it's not
        already present. Pass a name and a value to set an attribute.
        Omit the value or use `True` as value to set a
        property instead."""
        name = name.replace("_", "-")
        if value is True:
            self.__properties.add(name)
        elif name not in self.__attributes:
            self.__attributes[name] = value

    def update(self, dd: "Optional[dict]" = None, **kw) -> None:
        """
        Updates several attributes/properties with the values
        of `dd` and `kw` dicts.
        """
        dd = dd or {}
        dd.update(kw)
        name: "Any"
        value: "Any"
        for name, value in dd.items():
            self.add(name, value)

    def get(self, name: str, default: "Any" = None) -> "Any":
        """
        Returns the value of the attribute or property,
        or the default value if it doesn't exists."""
        name = name.replace("_", "-")
        if name in self.__attributes:
            return self.__attributes[name]
        if name in self.__properties:
            return True
        return default

    def render(self) -> str:
        """
        Renders the attributes and properties as a string.
        To provide consistent output, the attributes and properties
        are sorted by name and rendered like this:
        `<sorted attributes> + <sorted properties>`.
        """
        attributes = self.__attributes.copy()

        classes = self.classes
        if classes:
            attributes[CLASS_KEY] = classes

        attributes = dict(sorted(attributes.items()))
        properties = sorted(list(self.__properties))

        html_attrs = [
            f"{name}={quoteattr(str(value))}"
            for name, value in attributes.items()
        ]
        html_attrs.extend(properties)

        return " ".join(html_attrs)
