import inspect
from pathlib import Path
from typing import Any, Callable, Dict, Optional, Sequence, Set, Tuple, Type, Union

from jinja2 import Environment, FileSystemLoader
from jinja2.ext import Extension
from markupsafe import Markup

from jinjax.extension import JinjaX


DEFAULT_URL_PREFIX = "/components/"

LINK = '<link href="URL" rel="stylesheet">'
SCRIPT = '<script src="URL" defer></script>'

NON_PROPS_ATTRS = ("uses", "init", "props", "render")


class Component:
    __name__ = "Component"
    uses: Set[Type["Component"]] = set()

    _jinja_extensions: Sequence[Union[str, Type[Extension]]] = []
    _jinja_globals: Dict[str, Any] = {}
    _jinja_filters: Dict[str, Any] = {}
    _jinja_tests: Dict[str, Any] = {}

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
    def props(self):
        return {
            name: getattr(self, name) for name in self.__dir__()
            if not name.startswith("_") and name not in NON_PROPS_ATTRS
        }

    def __init__(self, **kw) -> None:
        # Make sure this is a set, but also
        # fix the mistake to create an empty set like `{}`
        self.uses = set(self.uses) if self.uses else set()

        self.content = kw.pop("content", "")
        self._template_name = f"{self.__class__.__name__}.jinja"

        attrs = [
            name for name in list(self.__dir__()) + list(self.__annotations__.keys())
            if (
                not name.startswith("_")
                and name not in NON_PROPS_ATTRS
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

        # TODO: type check props if types are available
        # in self.__annotations__

        self._jinja_env = Environment(
            loader=FileSystemLoader(self._get_root_path()),
            extensions=list(Component._jinja_extensions) + [JinjaX],
        )
        self._jinja_env.globals.update(Component._jinja_globals)
        self._jinja_env.filters.update(Component._jinja_filters)
        self._jinja_env.tests.update(Component._jinja_tests)

        self.init()

    def init(self):
        pass

    def render(self, static_url: str = DEFAULT_URL_PREFIX) -> str:
        components = collect_components(self.uses, {self.__class__})
        css, js = collect_assets(components, static_url)
        Component._jinja_globals["css_components"] = css
        Component._jinja_globals["js_components"] = js
        self._jinja_env.globals["css_components"] = css
        self._jinja_env.globals["js_components"] = js
        return self._render()

    def _render(self) -> str:
        props = self.props
        props.update({comp.__name__: comp for comp in self.uses})

        tmpl = self._jinja_env.get_template(self._template_name)
        return tmpl.render(**props)


def collect_components(
    components: Set[Type[Component]],
    collected: Set[Type[Component]]
) -> Set[Type[Component]]:
    collected = collected.union(components)
    for comp in components:
        if comp.uses:
            collected = collect_components(comp.uses, collected)
    return collected


def collect_assets(components: Set[Type[Component]], static_url: str) -> Tuple[str, str]:
    css = []
    js = []
    for comp in components:
        css_path = comp._get_css_path()
        if css_path:
            css.append(css_path)
        js_path = comp._get_js_path()
        if js_path:
            js.append(js_path)

    static_url = static_url.rstrip("/")
    _LINK = LINK.replace("URL", f"{static_url}/URL")
    _SCRIPT = SCRIPT.replace("URL", f"{static_url}/URL")

    css_html = [_LINK.replace("URL", url) for url in css]
    js_html = [_SCRIPT.replace("URL", url) for url in js]
    return (
        Markup("\n".join(css_html)),
        Markup("\n".join(js_html)),
    )
