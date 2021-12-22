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
from jinja2.exceptions import TemplateSyntaxError
from jinja2.ext import Extension

from .extension import JinjaX
from .utils import dedup_classes, get_html_attrs


NON_ATTRS_NAMES = ("uses", "init", "props", "render")


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
    styles = []
    scripts = []
    for comp in components:
        css_path = comp._get_css()
        if css_path:
            styles.append(css_path)
        js_path = comp._get_js()
        if js_path:
            scripts.append(js_path)

    return styles, scripts


class required:
    pass


class MissingRequiredAttribute(Exception):
    pass


class Component:
    __name__ = "Component"
    uses: Set[TComponent] = set()

    _extensions: Sequence[Union[str, Type[Extension]]] = []
    _globals: Dict[str, Any] = {}
    _filters: Dict[str, Any] = {}
    _tests: Dict[str, Any] = {}

    classes = ""
    active_classes = ""
    disabled_classes = ""
    active = False
    disabled = False

    @classmethod
    def _new(cls, caller: Optional[Callable] = None, **kw) -> str:
        kw["content"] = caller() if caller else ""
        obj = cls(**kw)
        return obj._render()

    @classmethod
    def _get_root_path(cls) -> Path:
        return Path(inspect.getfile(cls)).parent

    @classmethod
    def _get_css(cls) -> Optional[str]:
        here = cls._get_root_path()
        css_path = here / f"{cls.__name__}.css"
        if css_path.exists():
            return f"{here.name}/{cls.__name__}.css"
        return None

    @classmethod
    def _get_js(cls) -> Optional[str]:
        here = cls._get_root_path()
        js_path = here / f"{cls.__name__}.js"
        if js_path.exists():
            return f"{here.name}/{cls.__name__}.js"
        return None

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

        self.content = kwargs.pop("content", "")
        self._template_name = f"{name}.html.jinja"

        self._collect_props(kwargs)
        self._check_required_props()
        self._check_props_types()
        self._build_jinja_env()

        self.classes = dedup_classes(f"{self.classes} {name}")
        self.active_classes = dedup_classes(self.active_classes)
        self.disabled_classes = dedup_classes(self.disabled_classes)

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
        props = self.props
        props["html_attrs"] = self._render_html_attrs()
        props.update({comp.__name__: comp for comp in self.uses})

        try:
            tmpl = self._jinja_env.get_template(self._template_name)
        except TemplateSyntaxError:
            print("*** Pre-processed source: ***")
            print(self._jinja_env._preprocessed_source)   # type: ignore
            print("*" * 10)
            raise
        return tmpl.render(**props)

    def _render_html_attrs(self) -> str:
        classes = dedup_classes(self.classes)
        active_classes = dedup_classes(self.active_classes)
        disabled_classes = dedup_classes(self.disabled_classes)

        class_groups = [classes]
        if self.active and active_classes:
            class_groups.append(active_classes)
        if self.active and disabled_classes:
            class_groups.append(disabled_classes)

        self.attrs.update({
            "class": " ".join(class_groups),
            "data_active": self.active_classes if self.active_classes else False,
            "data_disabled": self.disabled_classes if self.disabled_classes else False,
            "active": self.active,
            "disabled": self.disabled,
        })
        return get_html_attrs(self.attrs)
