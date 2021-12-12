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

from jinjax.extension import JinjaX


NON_ATTRS_NAMES = ("uses", "init", "attrs", "render")


class Component:
    __name__ = "Component"
    uses: Set[Type["Component"]] = set()

    _extensions: Sequence[Union[str, Type[Extension]]] = []
    _globals: Dict[str, Any] = {}
    _filters: Dict[str, Any] = {}
    _tests: Dict[str, Any] = {}

    @classmethod
    def _new(cls, caller: Optional[Callable] = None, **kw) -> str:
        kw["content"] = caller() if caller else ""
        obj = cls(**kw)
        return obj._render()

    @classmethod
    def _get_root_path(cls) -> Path:
        return Path(inspect.getfile(cls)).parent

    @classmethod
    def _get_css_path(cls) -> Optional[str]:
        here = cls._get_root_path()
        css_path = here / f"{cls.__name__}.css"
        if css_path.exists():
            return f"{here.name}/{cls.__name__}.css"
        return None

    @classmethod
    def _get_js_path(cls) -> Optional[str]:
        here = cls._get_root_path()
        js_path = here / f"{cls.__name__}.js"
        if js_path.exists():
            return f"{here.name}/{cls.__name__}.js"
        return None

    @property
    def attrs(self) -> Dict[str, Any]:
        return {
            name: getattr(self, name)
            for name in self.__dir__()
            if not name.startswith("_") and name not in NON_ATTRS_NAMES
        }

    def __init__(self, **kw) -> None:
        # Make sure this is a set, but also
        # fix the mistake to create an empty set like `{}`
        self.uses = set(self.uses) if self.uses else set()

        self.content = kw.pop("content", "")
        self._template_name = f"{self.__class__.__name__}.jinja"

        self._collect_attrs(kw)
        self._check_required_attrs()
        self._check_attrs_types()
        self._build_jinja_env()

        self.init()

    def _collect_attrs(self, kw: Dict[str, Any]) -> None:
        attrs = [
            name
            for name in list(self.__dir__()) + list(self.__annotations__.keys())
            if (
                not name.startswith("_")
                and name not in NON_ATTRS_NAMES
                and not inspect.ismethod(getattr(self, name, None))
            )
        ]
        extra = {}
        for name, value in kw.items():
            if name in attrs:
                setattr(self, name, value)
            else:
                extra[name] = value
        self.extra = extra

    def _check_required_attrs(self) -> None:
        attrs = self.attrs

        for name, value in attrs.items():
            if value is required:
                raise MissingRequiredAttribute(name)

        for name in self.__annotations__.keys():
            if name.startswith("_") or name in NON_ATTRS_NAMES:
                continue
            if name not in attrs:
                raise MissingRequiredAttribute(name)

    def _check_attrs_types(self) -> None:
        # TODO: type check attrs if types are available
        # in self.__annotations__
        pass

    def _build_jinja_env(self) -> None:
        self._jinja_env = Environment(
            loader=FileSystemLoader(self._get_root_path()),
            extensions=list(Component._extensions) + [JinjaX],
        )
        self._jinja_env.globals.update(Component._globals)
        self._jinja_env.filters.update(Component._filters)
        self._jinja_env.tests.update(Component._tests)

    def init(self) -> None:
        pass

    def render(self) -> str:
        components = collect_components(self.uses, {self.__class__})
        styles, scripts = collect_assets(components)
        Component._globals["styles"] = styles
        Component._globals["scripts"] = scripts
        self._jinja_env.globals["styles"] = styles
        self._jinja_env.globals["scripts"] = scripts
        return self._render()

    def _render(self) -> str:
        attrs = self.attrs
        attrs.update({comp.__name__: comp for comp in self.uses})

        tmpl = self._jinja_env.get_template(self._template_name)
        return tmpl.render(**attrs)


def collect_components(
    components: Set[Type[Component]], collected: Set[Type[Component]]
) -> Set[Type[Component]]:
    collected = collected.union(components)
    for comp in components:
        if comp.uses:
            collected = collect_components(comp.uses, collected)
    return collected


def collect_assets(components: Set[Type[Component]]) -> Tuple[List[str], List[str]]:
    styles = []
    scripts = []
    for comp in components:
        css_path = comp._get_css_path()
        if css_path:
            styles.append(css_path)
        js_path = comp._get_js_path()
        if js_path:
            scripts.append(js_path)

    return styles, scripts


class required:
    pass


class MissingRequiredAttribute(Exception):
    pass
