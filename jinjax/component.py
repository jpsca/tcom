import inspect
from pathlib import Path
from typing import (
    Any,
    Callable,
    Dict,
    List,
    Optional,
    Sequence,
    Set,
    Tuple,
    Type,
    Union,
)

from jinja2 import Environment, FileSystemLoader
from jinja2.ext import Extension

from .extension import JinjaX
from .utils import dedup_classes, get_html_attrs


TComponent = Type["Component"]


def collect_components(
    components: Set[TComponent], collected: Set[TComponent]
) -> Set[TComponent]:
    collected = collected.union(components)
    for comp in components:
        if comp.uses:
            collected = collect_components(comp.uses, collected)
    return collected


def collect_assets(components: Set[TComponent]) -> Tuple[List[str], List[str]]:
    css: List[str] = []
    js: List[str] = []
    for comp in components:
        if comp.css:
            css.extend(comp.css)
        if comp.js:
            js.extend(comp.js)
    return css, js


class required:
    pass


class MissingRequiredAttribute(Exception):
    pass


NON_ATTRS_NAMES = ("uses", "js", "css", "init", "props", "render")


class Component:
    __name__ = "Component"
    uses: Set[TComponent] = set()
    js: Tuple[str, ...] = tuple()
    css: Tuple[str, ...] = tuple()

    _extensions: Sequence[Union[str, Type[Extension]]] = []
    _globals: Dict[str, Any] = {}
    _filters: Dict[str, Any] = {}
    _tests: Dict[str, Any] = {}

    classes: str = ""

    @classmethod
    def _new(cls, caller: Optional[Callable] = None, **kw) -> str:
        kw["content"] = caller() if caller else ""
        obj = cls(**kw)
        return obj._render()

    @property
    def props(self) -> Dict[str, Any]:
        return {
            name: getattr(self, name)
            for name in self.__dir__()
            if not name.startswith("_") and name not in NON_ATTRS_NAMES
        }

    def __init__(self, **kwargs) -> None:
        name = self.__class__.__name__

        # Make sure this is a set, but also
        # fix the mistake to create an empty set like `{}`
        self.uses = set(self.uses) if self.uses else set()

        # Make sure these are tuples
        self.js = tuple(self.js) if self.js else tuple()
        self.css = tuple(self.css) if self.css else tuple()

        self.content = kwargs.pop("content", "")
        self._collect_props(kwargs)
        self._check_required_props()
        self._check_props_types()
        self._build_jinja_env()

        self._template_name = f"{name}.html.jinja"
        self.classes = dedup_classes(f"{self.classes} {name}")
        print(">>> CLASSES 1: ", self.classes)
        self.init()

    def _collect_props(self, kw: Dict[str, Any]) -> None:
        props = [
            name
            for name in list(self.__dir__()) + list(self.__annotations__.keys())
            if (
                not name.startswith("_")
                and name not in NON_ATTRS_NAMES
                and not inspect.ismethod(getattr(self, name, None))
            )
        ]
        attrs = {}
        for name, value in kw.items():
            if name in props:
                setattr(self, name, value)
            else:
                attrs[name] = value
        self.attrs = attrs

    def _check_required_props(self) -> None:
        props = self.props

        for name, value in props.items():
            if value is required:
                raise MissingRequiredAttribute(name)

        for name in self.__annotations__.keys():
            if name.startswith("_") or name in NON_ATTRS_NAMES:
                continue
            if name not in props:
                raise MissingRequiredAttribute(name)

    def _check_props_types(self) -> None:
        # TODO: type check kw if types are available
        # in self.__annotations__
        pass

    def _build_jinja_env(self) -> None:
        here = Path(inspect.getfile(self.__class__)).parent

        self._jinja_env = Environment(
            loader=FileSystemLoader(here),
            extensions=list(Component._extensions) + [JinjaX],
        )
        self._jinja_env.globals.update(Component._globals)
        self._jinja_env.filters.update(Component._filters)
        self._jinja_env.tests.update(Component._tests)

    def init(self) -> None:
        pass

    def render(self) -> str:
        components = collect_components(self.uses, {self.__class__})
        css, js = collect_assets(components)
        Component._globals["css"] = css
        Component._globals["js"] = js
        self._jinja_env.globals["css"] = css
        self._jinja_env.globals["js"] = js
        return self._render()

    def _render(self) -> str:
        props = self.props
        self.attrs["class"] = dedup_classes(self.classes)
        props["html_attrs"] = get_html_attrs(self.attrs)
        props.update({comp.__name__: comp for comp in self.uses})

        try:
            tmpl = self._jinja_env.get_template(self._template_name)
        except Exception:
            print("*** Pre-processed source: ***")
            print(self._jinja_env.getattr("_preprocessed_source", ""))
            print("*" * 10)
            raise
        return tmpl.render(**props)
