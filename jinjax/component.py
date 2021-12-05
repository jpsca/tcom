import inspect
from pathlib import Path
from typing import Callable, Optional, Set, Tuple, Type

from jinja2 import Environment, FileSystemLoader
from markupsafe import Markup

from jinjax.extension import JinjaX


DEFAULT_STATIC_URL = "/components/"

LINK = '<link href="URL" rel="stylesheet">'
SCRIPT = '<script src="URL" defer></script>'

NON_PROPS_ATTRS = ("uses", "init", "props", "render")


class Component:
    __name__ = "Component"
    uses: Set[Type["Component"]] = set()

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

        self.init()

    def init(self):
        pass

    def render(self, static_url: str = DEFAULT_STATIC_URL, **globals) -> str:
        components = collect_components(self.uses, set())
        css, js = collect_assets(components, static_url)
        globals["css_components"] = css
        globals["js_components"] = js
        return self._render(**globals)

    def _render(self, **globals) -> str:
        globals.update({comp.__name__: comp for comp in self.uses})
        jinja_env = getattr(
            self,
            "jinja_env",
            Environment(
                loader=FileSystemLoader(self._get_root_path()),
                extensions=[JinjaX],
            ),
        )
        tmpl = jinja_env.get_template(self._template_name, globals=globals)
        return tmpl.render(**self.props)


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
