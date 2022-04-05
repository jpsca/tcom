import oot


def application(environ, start_response):
    status = "200 OK"
    headers = [("Content-type", "text/plain")]
    start_response(status, headers)
    return [b"NOPE"]


def make_environ(**kw):
    kw.setdefault("PATH_INFO", "/")
    kw.setdefault("REQUEST_METHOD", "GET")
    return kw


def mock_start_response(status, headers):
    pass


def get_catalog(**kw):
    catalog = oot.Catalog(**kw)
    catalog.add_folder("tests/components")
    return catalog


def run_middleware(middleware, url):
    return middleware(make_environ(PATH_INFO=url), mock_start_response)


# Tests


def test_css_is_returned():
    catalog = get_catalog()
    middleware = catalog.get_middleware(application)

    resp = run_middleware(middleware, "/static/components/page.css")
    assert resp and not isinstance(resp, list)
    text = resp.filelike.read().strip()
    assert text == b"/* Page.css */"


def test_js_is_returned():
    catalog = get_catalog()
    middleware = catalog.get_middleware(application)

    resp = run_middleware(middleware, "/static/components/page.js")
    assert resp and not isinstance(resp, list)
    text = resp.filelike.read().strip()
    assert text == b"/* Page.js */"


def test_other_extensions_ignored():
    catalog = get_catalog()
    middleware = catalog.get_middleware(application)

    resp = run_middleware(middleware, "/static/components/Page.html.jinja")
    assert resp == [b"NOPE"]


def test_add_custom_extensions():
    catalog = get_catalog(allowed_ext=[".jinja"])
    middleware = catalog.get_middleware(application)

    resp = run_middleware(middleware, "/static/components/Page.html.jinja")
    assert resp and not isinstance(resp, list)
    text = resp.filelike.read().strip()
    assert b"<!DOCTYPE html>" in text


def test_custom_root_url():
    catalog = get_catalog(root_url="/static/co/")
    middleware = catalog.get_middleware(application)

    resp = run_middleware(middleware, "/static/co/page.css")
    assert resp and not isinstance(resp, list)
    text = resp.filelike.read().strip()
    assert text == b"/* Page.css */"


def test_autorefresh_load():
    catalog = get_catalog()
    middleware = catalog.get_middleware(application, autorefresh=True)

    resp = run_middleware(middleware, "/static/components/page.css")
    assert resp and not isinstance(resp, list)
    text = resp.filelike.read().strip()
    assert text == b"/* Page.css */"


def test_autorefresh_block():
    catalog = get_catalog()
    middleware = catalog.get_middleware(application, autorefresh=True)

    resp = run_middleware(middleware, "/static/components/Page.html.jinja")
    assert resp == [b"NOPE"]
