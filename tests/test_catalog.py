import pytest

import tcom


@pytest.fixture()
def catalog():
    catalog = tcom.Catalog()
    catalog.add_folder("tests/components")
    return catalog


def test_render_simple(catalog):
    html = catalog.render("Greeting", message="Hello world!")
    assert html == '<div class="greeting">Hello world!</div>'


def test_render_content(catalog):
    content = '<button type="button">Close</button>'
    html = catalog.render("Card", content=content)
    print(html)
    assert html == f"""
<section class="card">
{content}
<button type="button" disabled>&times;</button>
</section>""".strip()


def test_component_uses_other(catalog):
    html = catalog.render("Page", message="Hello")
    print(html)
    assert """
<section class="card">
<div class="greeting">Hello</div>
<button type="button">Close</button>
<button type="button" disabled>&times;</button>
</section>""".strip() in html


def test_assets_included(catalog):
    html = catalog.render("Page", message="Hello")
    print(html)
    assert '<link rel="stylesheet" href="/static/components/greeting.css">' in html
    assert '<link rel="stylesheet" href="/static/components/card.css">' in html
    assert '<script src="/static/components/card.js" defer></script>' in html
    assert '<script src="/static/components/greeting.js" defer></script>' not in html


def test_global_values():
    message = "Hello world!"
    catalog = tcom.Catalog()
    catalog.jinja_env.globals["globalvar"] = message
    catalog.add_folder("tests/components")
    html = catalog.render("WithGlobal")
    print(html)
    assert message in html


def test_required_attr_are_required(catalog):
    with pytest.raises(tcom.MissingRequiredAttr):
        catalog.render("Page")
