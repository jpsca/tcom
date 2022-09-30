import logging
import os
from typing import Any, Callable, Optional, Union
from pathlib import Path
from uuid import uuid4

import jinja2
from markupsafe import Markup

from .component import Component
from .exceptions import ComponentNotFound
from .jinjax import DEBUG_ATTR_NAME, JinjaX, RENDER_CMD
from .middleware import ComponentsMiddleware
from .html_attrs import HTMLAttrs


logger = logging.getLogger("tcom")

TFileExt = Union[tuple[str, ...], str]

DEFAULT_URL_ROOT = "/static/components/"
ALLOWED_EXTENSIONS = (".css", ".js")
DEFAULT_PREFIX = ""
DEFAULT_EXTENSION = ".jinja"
DELIMITER = "."
SLASH = "/"
ASSETS_PLACEHOLDER_KEY = "components_assets"
PROP_ATTRS = "attrs"
PROP_CONTENT = "content"


class Catalog:
    __slots__ = (
        "components",
        "prefixes",
        "root_url",
        "file_ext",
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
        file_ext: "TFileExt" = DEFAULT_EXTENSION,
    ) -> None:
        self.components: "dict[str, Component]" = {}
        self.prefixes: "dict[str, jinja2.FileSystemLoader]" = {}
        self.collected_css: "list[str]" = []
        self.collected_js: "list[str]" = []
        self.assets_placeholder = f"<components_assets-{uuid4().hex} />"
        self.file_ext = file_ext

        root_url = root_url.strip().rstrip(SLASH)
        self.root_url = f"{root_url}{SLASH}"

        extensions = (extensions or []) + ["jinja2.ext.do", JinjaX]
        jinja_env = jinja2.Environment(
            extensions=extensions,
            undefined=jinja2.StrictUndefined,
        )
        globals = globals or {}
        globals[RENDER_CMD] = self._render
        globals["render"] = self.inline_render
        globals["get_source"] = self.get_source
        globals[ASSETS_PLACEHOLDER_KEY] = self.assets_placeholder
        jinja_env.globals.update(globals)
        jinja_env.filters.update(filters or {})
        jinja_env.tests.update(tests or {})
        self.jinja_env = jinja_env

    def add_folder(
        self,
        root_path: "Union[str, Path]",
        *,
        prefix: str = DEFAULT_PREFIX,
    ) -> None:
        prefix = prefix.strip().strip(f"{DELIMITER}{SLASH}").replace(SLASH, DELIMITER)

        root_path = str(root_path)
        if prefix in self.prefixes:
            loader = self.prefixes[prefix]
            if root_path in loader.searchpath:
                return
            loader.searchpath.append(root_path)
        else:
            self.prefixes[prefix] = jinja2.FileSystemLoader(root_path)

    def add_module(self, module: "Any", *, prefix: "Optional[str]" = None) -> None:
        if prefix is None:
            prefix = module.prefix or ""
        self.add_folder(module.components_path, prefix=prefix)

    def render(
        self,
        __name: str,
        *,
        content: str = "",
        source: str = "",
        **kw,
    ) -> str:
        self.collected_css = []
        self.collected_js = []

        kw["__content"] = content
        kw["__source"] = source
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

    def get_middleware(
        self,
        application: "Callable",
        allowed_ext: "Optional[tuple[str, ...]]" = ALLOWED_EXTENSIONS,
        **kw,
    ) -> ComponentsMiddleware:
        middleware = ComponentsMiddleware()
        middleware.configure(application=application, allowed_ext=allowed_ext, **kw)

        for prefix, loader in self.prefixes.items():
            url_prefix = self._get_url_prefix(prefix)
            url = f"{self.root_url}{url_prefix}"
            for root in loader.searchpath[::-1]:
                middleware.add_files(root, url)

        return middleware

    def get_source(self, cname: str, file_ext: "TFileExt" = "") -> str:
        prefix, name = self._split_name(cname)
        _root_path, path = self._get_component_path(prefix, name, file_ext=file_ext)
        return Path(path).read_text()

    # Private

    def _render(
        self,
        __name: str,
        *,
        caller: "Optional[Callable]" = None,
        **kw,
    ) -> str:
        content = kw.pop("__content", "")
        attrs = kw.pop("__attrs", None) or {}
        file_ext = kw.pop("__file_ext", "")
        source = kw.pop("__source", "")
        prefix, name = self._split_name(__name)
        url_prefix = self._get_url_prefix(prefix)

        if source:
            from_source = True
        else:
            from_source = False
            root_path, path = self._get_component_path(prefix, name, file_ext=file_ext)
            source = path.read_text()

        component = Component(name=__name, url_prefix=url_prefix, source=source)
        for css in component.css:
            if css not in self.collected_css:
                self.collected_css.append(css)
        for js in component.js:
            if js not in self.collected_js:
                self.collected_js.append(js)

        attrs = attrs.as_dict if isinstance(attrs, HTMLAttrs) else attrs
        attrs.update(kw)
        kw = attrs

        props, extra = component.filter_args(kw)
        props[PROP_ATTRS] = HTMLAttrs(extra)
        props[PROP_CONTENT] = content or (caller() if caller else "")

        self.jinja_env.loader = self.prefixes[prefix]

        try:
            if from_source:
                tmpl = self.jinja_env.from_string(source)
                logger.debug("Rendering from source %s", __name)
            else:
                tmpl_name = str(path.relative_to(root_path))
                tmpl = self.jinja_env.get_template(tmpl_name)
                logger.debug("Rendering %s", tmpl_name)
        except Exception:  # pragma: no cover
            print("*** Pre-processed source: ***")
            print(getattr(self.jinja_env, DEBUG_ATTR_NAME, ""))
            print("*" * 10)
            raise

        return tmpl.render(**props).strip()

    def _split_name(self, cname: str) -> "tuple[str, str]":
        cname = cname.strip().strip(DELIMITER)
        if DELIMITER not in cname:
            return DEFAULT_PREFIX, cname
        for prefix in self.prefixes.keys():
            if cname.startswith(prefix):
                return prefix, cname.removeprefix(prefix)
        return DEFAULT_PREFIX, cname

    def _get_url_prefix(self, prefix: str) -> str:
        url_prefix = (
            prefix.strip().strip(f"{DELIMITER}{SLASH}").replace(DELIMITER, SLASH)
        )
        if url_prefix:
            url_prefix = f"{url_prefix}{SLASH}"
        return url_prefix

    def _get_component_path(
        self, prefix: str, name: str, file_ext: "TFileExt" = ""
    ) -> "tuple[Path, Path]":
        name = name.replace(DELIMITER, SLASH)
        name_dot = f"{name}."
        file_ext = file_ext or self.file_ext
        root_paths = self.prefixes[prefix].searchpath

        for root_path in root_paths:
            for curr_folder, _folders, files in os.walk(
                root_path, topdown=False, followlinks=True
            ):
                relfolder = os.path.relpath(curr_folder, root_path).strip(".")
                if relfolder and not name_dot.startswith(relfolder):
                    continue

                for filename in files:
                    if relfolder:
                        filepath = f"{relfolder}/{filename}"
                    else:
                        filepath = filename
                    if filepath.startswith(name_dot) and filepath.endswith(file_ext):
                        return Path(root_path), Path(curr_folder) / filename

        raise ComponentNotFound(
            f"Unable to found a file named {name}{file_ext} "
            f"nor one following the pattern {name_dot}*{file_ext}"
        )

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
