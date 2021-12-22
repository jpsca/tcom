from typing import Any, Callable, Dict, List, Tuple

from jinjax import ComponentAssetsMiddleware


def simple_app(
    environ: Dict[str, Any], start_response: Callable[[str, List[Tuple[str, str]]], None]
):
    status = "200 OK"
    headers = [("Content-type", "text/plain")]
    start_response(status, headers)
    return [b"Hello World"]


def mock_start_response(status: str, headers: List[Tuple[str, str]]) -> None:
    pass


def make_environ(**kw):
    kw.setdefault("PATH_INFO", "/")
    kw.setdefault("REQUEST_METHOD", "GET")
    return kw


def test_css_is_returned():
    app = ComponentAssetsMiddleware(simple_app, "tests/components")
    fileobj = app(
        make_environ(PATH_INFO="/components/page/Page.css"),
        mock_start_response,
    )
    assert fileobj
    text = fileobj.filelike.read().strip()
    assert text == b"/* Page.css */"


def test_js_is_returned():
    app = ComponentAssetsMiddleware(simple_app, "tests/components")
    resp = app(
        make_environ(PATH_INFO="/components/page/Page.js"),
        mock_start_response,
    )
    text = resp.filelike.read().strip()
    assert text == b"/* Page.js */"


def test_other_extensions_ignored():
    app = ComponentAssetsMiddleware(simple_app, "tests/components")
    resp = app(
        make_environ(PATH_INFO="/components/page/Page.html.jinja"),
        mock_start_response,
    )
    assert resp == [b"Hello World"]


def test_add_custom_extensions():
    app = ComponentAssetsMiddleware(simple_app, "tests/components", allowed=[".jinja"])
    resp = app(
        make_environ(PATH_INFO="/components/page/Page.html.jinja"),
        mock_start_response,
    )
    text = resp.filelike.read().strip()
    assert b"<!DOCTYPE html>" in text


def test_custom_prefix():
    app = ComponentAssetsMiddleware(
        simple_app, "tests/components", prefix="/static/co/"
    )
    fileobj = app(
        make_environ(PATH_INFO="/static/co/page/Page.css"),
        mock_start_response
    )
    text = fileobj.filelike.read().strip()
    assert text == b"/* Page.css */"


def test_autorefresh_load():
    app = ComponentAssetsMiddleware(simple_app, "tests/components", autorefresh=True)
    fileobj = app(
        make_environ(PATH_INFO="/components/page/Page.css"),
        mock_start_response
    )
    text = fileobj.filelike.read().strip()
    assert text == b"/* Page.css */"


def test_autorefresh_block():
    app = ComponentAssetsMiddleware(simple_app, "tests/components", autorefresh=True)
    resp = app(
        make_environ(PATH_INFO="/components/page/Page.html.jinja"),
        mock_start_response,
    )
    assert resp == [b"Hello World"]
