import tcom


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
    catalog = tcom.Catalog(**kw)
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


def test_other_file_extensions_ignored():
    catalog = get_catalog()
    middleware = catalog.get_middleware(application)
    resp = run_middleware(middleware, "/static/components/Page.jinja")
    assert resp == [b"NOPE"]


def test_add_custom_extensions():
    catalog = get_catalog()
    middleware = catalog.get_middleware(application, allowed_ext=[".jinja"])

    resp = run_middleware(middleware, "/static/components/Page.jinja")
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

    resp = run_middleware(middleware, "/static/components/Page.jinja")
    assert resp == [b"NOPE"]


def test_multiple_folders(tmp_path):
    folder1 = tmp_path / "folder1"
    folder1.mkdir()
    (folder1 / "folder1.css").write_text("folder1")

    folder2 = tmp_path / "folder2"
    folder2.mkdir()
    (folder2 / "folder2.css").write_text("folder2")

    catalog = tcom.Catalog()
    catalog.add_folder(folder1)
    catalog.add_folder(folder2)
    middleware = catalog.get_middleware(application)

    resp = run_middleware(middleware, "/static/components/folder1.css")
    assert resp.filelike.read() == b"folder1"
    resp = run_middleware(middleware, "/static/components/folder2.css")
    assert resp.filelike.read() == b"folder2"


def test_multiple_folders_precedence(tmp_path):
    folder1 = tmp_path / "folder1"
    folder1.mkdir()
    (folder1 / "name.css").write_text("folder1")

    folder2 = tmp_path / "folder2"
    folder2.mkdir()
    (folder2 / "name.css").write_text("folder2")

    catalog = tcom.Catalog()
    catalog.add_folder(folder1)
    catalog.add_folder(folder2)
    middleware = catalog.get_middleware(application)

    resp = run_middleware(middleware, "/static/components/name.css")
    assert resp.filelike.read() == b"folder1"
