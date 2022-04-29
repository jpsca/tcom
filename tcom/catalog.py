from collections import defaultdict
from pathlib import Path
from typing import TYPE_CHECKING
from uuid import uuid4

import jinja2

from .component import Component, EXTRA_ATTRS_KEY
from .exceptions import ComponentNotFound
from .jinjax import DEBUG_ATTR_NAME, JinjaX, RENDER_CMD
from .middleware import ComponentsMiddleware
from .utils import dedup_classes, get_html_attrs

if TYPE_CHECKING:
    from typing import Any, Callable, Iterable, Optional, Union


DEFAULT_URL_ROOT = "/static/components/"
ALLOWED_EXTENSIONS = (".css", ".js")
COMPONENT_PATTERN = "*.jinja"
DEFAULT_PREFIX = ""
ASSETS_PLACEHOLDER_KEY = "components_assets"
SELF_PREFIX = "tcs"
SELF_PATH = Path(__file__).parent / "js"
CLASS_KEY = "class"
CLASS_ALT_KEY = "classes"
HTML_ATTRS_KEY = "html_attrs"
CONTENT_KEY = "content"


class Catalog:
    __slots__ = (
        "components",
        "prefixes",
        "root_url",
        "allowed_ext",
        "jinja_env",
        "assets_placeholder",
        "collected_css",
        "collected_js",
    )

    def __init__(
        self,
        *,
        globals: "Optional[dict[str, Any]]" = None,
        filters: "Optional[dict[str, Any]]" = None,
        tests: "Optional[dict[str, Any]]" = None,
        extensions: "Optional[list]" = None,
        root_url: str = DEFAULT_URL_ROOT,
        allowed_ext: "Optional[Iterable[str]]" = None,
    ) -> None:
        self.components: "dict[str, Component]" = {}
        self.prefixes: "dict[str, list[str]]" = defaultdict(list)
        self.root_url = f"/{root_url.strip().strip('/')}/".replace(r"//", r"/")
        self.allowed_ext: "set[str]" = set(allowed_ext or ALLOWED_EXTENSIONS)
        self.collected_css: "set[str]" = set()
        self.collected_js: "set[str]" = set()

        globals = globals or {}
        filters = filters or {}
        tests = tests or {}
        extensions = extensions or []

        globals[RENDER_CMD] = self._render
        self.assets_placeholder = f"<components_assets-{uuid4()} />"
        globals[ASSETS_PLACEHOLDER_KEY] = self.assets_placeholder

        self._build_jinja_env(globals, filters, tests, extensions)

        self.add_folder(SELF_PATH, prefix=SELF_PREFIX)

    def add_folder(
        self,
        folderpath: "Union[str, Path]",
        *,
        prefix: str = DEFAULT_PREFIX
    ) -> None:
        prefix = prefix.strip("/")
        folderpath = Path(folderpath)
        self.prefixes[prefix].append(str(folderpath))

        loader_prefix = prefix or "."
        subloader = self.jinja_env.loader.mapping.get(loader_prefix)  # type: ignore
        subloader = subloader or jinja2.ChoiceLoader([])
        subloader.loaders.append(jinja2.FileSystemLoader(str(folderpath)))
        self.jinja_env.loader.mapping[loader_prefix] = subloader  # type: ignore

        for path in folderpath.rglob(COMPONENT_PATTERN):
            name = path.name.split(".", 1)[0]
            if not name[0].isupper():
                continue
            content = path.read_text()
            relpath = str(path.relative_to(folderpath))
            self.components[name] = Component(
                name=name,
                relpath=relpath,
                content=content,
                prefix=prefix,
            )

    def render(self, name: str, *, prefix: str = DEFAULT_PREFIX, **kwargs) -> str:
        self.collected_css = set()
        self.collected_js = set()

        html = self._render(name, prefix=prefix, **kwargs)
        html = self._insert_assets(html)

        return html

    def get_middleware(self, application, **kwargs) -> ComponentsMiddleware:
        middleware = ComponentsMiddleware(
            application, allowed_ext=self.allowed_ext, **kwargs
        )
        for prefix, paths in self.prefixes.items():
            if prefix:
                prefix += "/"
            for path in paths:
                middleware.add_files(path, f"{self.root_url}{prefix}")
        return middleware

    # Private

    def _build_jinja_env(
        self,
        globals: "dict[str, Any]",
        filters: "dict[str, Any]",
        tests: "dict[str, Any]",
        extensions: "list",
    ) -> None:
        self.jinja_env = jinja2.Environment(
            loader=jinja2.PrefixLoader({}),
            extensions=list(extensions) + [JinjaX],
            undefined=jinja2.StrictUndefined,
        )
        self.jinja_env.globals.update(globals)
        self.jinja_env.filters.update(filters)
        self.jinja_env.tests.update(tests)

    def _get_component(self, name: str) -> Component:
        component = self.components.get(name)
        if component is None:
            raise ComponentNotFound(name)
        return component

    def _insert_assets(self, html: str) -> str:
        html_css = [
            f'<link rel="stylesheet" href="{self.root_url}{css}">'
            for css in self.collected_css
        ]
        html_js = [
            f'<script src="{self.root_url}{js}" defer></script>'
            for js in self.collected_js
        ]
        return html.replace(self.assets_placeholder, "\n".join(html_css + html_js))

    def _render(
        self,
        name: str,
        *,
        prefix: str = DEFAULT_PREFIX,
        content: str = "",
        caller: "Optional[Callable]" = None,
        **kwargs
    ) -> str:
        component = self._get_component(name)
        for css in component.css:
            self.collected_css.add(css)
        for js in component.js:
            self.collected_js.add(js)

        classes = dedup_classes(
            " ".join([
                kwargs.pop(CLASS_KEY, ""),
                kwargs.get(CLASS_ALT_KEY, ""),
            ])
        )
        if classes:
            kwargs[CLASS_KEY] = classes

        props = component.filter_args(kwargs)
        props[HTML_ATTRS_KEY] = get_html_attrs(props[EXTRA_ATTRS_KEY])
        props[CONTENT_KEY] = content or (caller() if caller else "")

        tmpl_name = f"{prefix or '.'}/{component.relpath}"
        try:
            tmpl = self.jinja_env.get_template(tmpl_name)
        except Exception:  # pragma: no cover
            print("*** Pre-processed source: ***")
            print(getattr(self.jinja_env, DEBUG_ATTR_NAME, ""))
            print("*" * 10)
            raise
        return tmpl.render(**props).strip()
