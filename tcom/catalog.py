from pathlib import Path
from typing import TYPE_CHECKING
from uuid import uuid4

import jinja2
from markupsafe import Markup

from .component import Component
from .exceptions import ComponentNotFound
from .jinjax import DEBUG_ATTR_NAME, JinjaX, RENDER_CMD
from .middleware import ComponentsMiddleware
from .html_attrs import HTMLAttrs

if TYPE_CHECKING:
    from typing import Any, Callable, Iterable, Optional, Union


DEFAULT_URL_ROOT = "/static/components/"
ALLOWED_EXTENSIONS = (".css", ".js")
DEFAULT_PREFIX = ""
DEFAULT_PATTERN = ".*jinja"
DELIMITER = "."
SLASH = "/"
ASSETS_PLACEHOLDER_KEY = "components_assets"
HTML_ATTRS_KEY = "attrs"
CONTENT_KEY = "content"


class Catalog:
    __slots__ = (
        "components",
        "prefixes",
        "root_url",
        "allowed_ext",
        "pattern",
        "globals",
        "filters",
        "tests",
        "extensions",
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
        allowed_ext: "Optional[Iterable[str]]" = None,
        pattern: str = DEFAULT_PATTERN,
        root_url: str = DEFAULT_URL_ROOT,
    ) -> None:
        self.components: "dict[str, Component]" = {}
        self.prefixes: "dict[str, jinja2.Environment]" = {}
        self.allowed_ext: "set[str]" = set(allowed_ext or ALLOWED_EXTENSIONS)
        self.collected_css: "list[str]" = []
        self.collected_js: "list[str]" = []
        self.assets_placeholder = f"<components_assets-{uuid4().hex} />"
        self.pattern = pattern

        root_url = root_url.strip().rstrip(SLASH)
        self.root_url = f"{root_url}{SLASH}"

        globals = globals or {}
        globals[RENDER_CMD] = self._render
        globals["render"] = self.inline_render
        globals["get_source"] = self.get_source
        globals[ASSETS_PLACEHOLDER_KEY] = self.assets_placeholder
        self.globals = globals

        filters = filters or {}
        self.filters = filters

        self.tests = tests or {}

        extensions = extensions or []
        self.extensions = extensions + ["jinja2.ext.do", JinjaX]

    def add_folder(
        self,
        folderpath: "Union[str, Path]",
        *,
        prefix: str = ""
    ) -> None:
        prefix = prefix.strip().strip(f"{DELIMITER}{SLASH}")
        path_prefix = prefix.replace(DELIMITER, SLASH)

        if path_prefix in self.prefixes:
            root_path = self._get_root_path(path_prefix)
            if path_prefix == DEFAULT_PREFIX:
                msg = (
                    f"`{root_path}` already is the main folder. "
                    "Use a prefix to add more folders."
                )
            else:
                msg = (
                    f"`{root_path}` already using the prefix `{prefix}`. "
                    "Use a different prefix."
                )
            raise ValueError(msg)

        self.prefixes[path_prefix] = self._get_jinja_env(folderpath)

    def add_module(self, module: "Any", *, prefix: "Optional[str]" = None) -> None:
        if prefix is None:
            prefix = module.prefix or ""
        self.add_folder(module.components_path, prefix=prefix)

    def render(self, __name: str, *, content: str = "", **kw) -> str:
        self.collected_css = []
        self.collected_js = []

        kw[f"__{CONTENT_KEY}"] = content
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
        for prefix in self.prefixes:
            middleware.add_files(
                self._get_root_path(prefix),
                f"{self.root_url}{self._get_url_prefix(prefix)}"
            )
        return middleware

    def get_source(self, cname: str) -> str:
        prefix, name = self._split_name(cname)
        root_path = self._get_root_path(prefix)
        path = self._get_component_path(root_path, name)
        return Path(path).read_text()

    # Private

    def _get_jinja_env(self, folderpath: "Union[str, Path]") -> "jinja2.Environment":
        loader = jinja2.FileSystemLoader(str(folderpath))
        env = jinja2.Environment(
            loader=loader,
            extensions=self.extensions,
            undefined=jinja2.StrictUndefined,
        )
        env.globals.update(self.globals)
        env.filters.update(self.filters)
        env.tests.update(self.tests)
        return env

    def _render(
        self,
        __name: str,
        *,
        caller: "Optional[Callable]" = None,
        **kw
    ) -> str:
        prefix, name = self._split_name(__name)
        url_prefix = self._get_url_prefix(prefix)
        root_path = self._get_root_path(prefix)
        path = self._get_component_path(root_path, name)
        source = path.read_text()

        component = Component(name=__name, url_prefix=url_prefix, source=source)
        for css in component.css:
            if css not in self.collected_css:
                self.collected_css.append(css)
        for js in component.js:
            if js not in self.collected_js:
                self.collected_js.append(js)

        content = kw.get(f"__{CONTENT_KEY}")
        attrs = kw.get(f"__{HTML_ATTRS_KEY}")

        if attrs and isinstance(attrs, HTMLAttrs):
            attrs = attrs.as_dict
        if attrs and isinstance(attrs, dict):
            attrs.update(kw)
            kw = attrs

        props, extra = component.filter_args(kw)
        props[HTML_ATTRS_KEY] = HTMLAttrs(extra)
        props[CONTENT_KEY] = content or (caller() if caller else "")

        jinja_env = self.prefixes[prefix]
        tmpl_name = str(path.relative_to(root_path))
        try:
            tmpl = jinja_env.get_template(tmpl_name)
        except Exception:  # pragma: no cover
            print("*** Pre-processed source: ***")
            print(getattr(jinja_env, DEBUG_ATTR_NAME, ""))
            print("*" * 10)
            raise

        return tmpl.render(**props).strip()

    def _split_name(self, cname: str) -> "tuple[str, str]":
        cname = cname.strip().strip(DELIMITER).replace(DELIMITER, SLASH)
        if SLASH not in cname:
            return DEFAULT_PREFIX, cname
        for prefix in self.prefixes:
            if cname.startswith(prefix):
                return prefix, cname.removeprefix(prefix)
        return DEFAULT_PREFIX, cname

    def _get_root_path(self, prefix: str) -> "Path":
        return Path(self.prefixes[prefix].loader.searchpath[0])  # type: ignore

    def _get_url_prefix(self, prefix: str) -> str:
        url_prefix = prefix.strip().strip(SLASH)
        if url_prefix:
            url_prefix = f"{url_prefix}{SLASH}"
        return url_prefix

    def _get_component_path(self, root_path: "Path", name: str) -> "Path":
        glob_name = f"{name}{self.pattern}"
        try:
            return next(root_path.glob(glob_name))
        except StopIteration:
            raise ComponentNotFound(glob_name)

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

    def _render_attrs(self, attrs: dict) -> "Markup":
        html_attrs = []
        for name, value in attrs.items():
            if value != "":
                html_attrs.append(f"{name}={value}")
            else:
                html_attrs.append(name)
        return Markup(" ".join(html_attrs))
