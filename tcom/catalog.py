from collections import defaultdict
from pathlib import Path
from typing import TYPE_CHECKING
from uuid import uuid4

import jinja2
from markupsafe import Markup

from .component import Component
from .jinjax import DEBUG_ATTR_NAME, JinjaX, RENDER_CMD
from .middleware import ComponentsMiddleware
from .html_attrs import HTMLAttrs

if TYPE_CHECKING:
    from typing import Any, Callable, Iterable, Optional, Union


DEFAULT_URL_ROOT = "/static/components/"
ALLOWED_EXTENSIONS = (".css", ".js")
COMPONENT_PATTERN = "*.jinja"
DEFAULT_PREFIX = "."
ASSETS_PLACEHOLDER_KEY = "components_assets"
HTML_ATTRS_KEY = "attrs"
CONTENT_KEY = "content"


def filter_unique(text):
    return f"{text}-{uuid4().hex}"


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
        self.collected_css: "list[str]" = []
        self.collected_js: "list[str]" = []
        self.assets_placeholder = f"<components_assets-{uuid4().hex} />"

        globals = globals or {}
        globals[RENDER_CMD] = self._render
        globals["render"] = self.inline_render
        globals["get_source"] = self.get_source
        globals[ASSETS_PLACEHOLDER_KEY] = self.assets_placeholder

        filters = filters or {}
        filters["unique"] = filter_unique

        tests = tests or {}
        extensions = extensions or []

        self._build_jinja_env(globals, filters, tests, extensions)

    def add_folder(
        self,
        folderpath: "Union[str, Path]",
        *,
        prefix: str = DEFAULT_PREFIX
    ) -> None:
        prefix = prefix.strip("/")
        folderpath = Path(folderpath)
        self.prefixes[prefix].append(str(folderpath))

        subloader = self.jinja_env.loader.mapping.get(prefix)  # type: ignore
        subloader = subloader or jinja2.ChoiceLoader([])
        subloader.loaders.append(jinja2.FileSystemLoader(str(folderpath)))
        self.jinja_env.loader.mapping[prefix] = subloader  # type: ignore

    def add_module(
        self,
        module: "Any",
        *,
        prefix: "Optional[str]" = None,
    ) -> None:
        if prefix is None:
            prefix = module.prefix or DEFAULT_PREFIX
        self.add_folder(module.components_path, prefix=prefix)

    def render(
        self,
        __name: str,
        *,
        content: str = "",
        **kw
    ) -> str:
        self.collected_css = []
        self.collected_js = []

        kw["__content"] = content
        html = self._render(__name, **kw)
        html = self._insert_assets(html)
        return html

    def inline_render(self, name_or_attrs, **kw):
        if isinstance(name_or_attrs, str):
            return self._render(name_or_attrs, **kw)
        else:
            attrs = name_or_attrs or {}
            attrs.update(kw)
            return self._render_attrs(attrs)

    def get_middleware(self, application, **kw) -> ComponentsMiddleware:
        middleware = ComponentsMiddleware(
            application, allowed_ext=self.allowed_ext, **kw
        )
        for prefix, paths in self.prefixes.items():
            prefix = prefix.strip(".")
            if prefix:
                prefix += "/"
            for path in paths:
                middleware.add_files(path, f"{self.root_url}{prefix}")
        return middleware

    def get_source(self, name: str) -> str:
        component = self._get_component(name)
        return component.get_source()

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
            extensions=list(extensions) + ["jinja2.ext.do", JinjaX],
            undefined=jinja2.StrictUndefined,
        )
        self.jinja_env.globals.update(globals)
        self.jinja_env.filters.update(filters)
        self.jinja_env.tests.update(tests)

    # content = path.read_text()
    # relpath = str(path.relative_to(folderpath))
    # self.components[name] = Component(
    #     name=name,
    #     path=path.resolve(),
    #     relpath=relpath,
    #     content=content,
    #     prefix=prefix,
    # )

    def _render(
        self,
        __name: str,
        *,
        caller: "Optional[Callable]" = None,
        __content: str = "",
        __attrs: "Optional[Any]" = None,
        **kw
    ) -> str:
        source, _filename, _uptodate = self.jinja_env.loader.get_source(self.jinja_env, __name)

        component = Component(name=__name, content=source)
        for css in component.css:
            if css not in self.collected_css:
                self.collected_css.append(css)
        for js in component.js:
            if js not in self.collected_js:
                self.collected_js.append(js)

        attrs = __attrs
        if attrs and isinstance(attrs, HTMLAttrs):
            attrs = attrs.as_dict

        if attrs and isinstance(attrs, dict):
            attrs.update(kw)
            kw = attrs

        props, extra = component.filter_args(kw)
        props[HTML_ATTRS_KEY] = HTMLAttrs(extra)
        props[CONTENT_KEY] = __content or (caller() if caller else "")

        try:
            tmpl = self.jinja_env.get_template(__name)
        except Exception:  # pragma: no cover
            print("*** Pre-processed source: ***")
            print(getattr(self.jinja_env, DEBUG_ATTR_NAME, ""))
            print("*" * 10)
            raise

        return tmpl.render(**props).strip()

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

    def _render_attrs(self, attrs):
        html_attrs = []
        for name, value in attrs.items():
            if value != "":
                html_attrs.append(f"{name}={value}")
            else:
                html_attrs.append(name)
        return Markup(" ".join(html_attrs))
