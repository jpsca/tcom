from .components.card import Card
from .components.greeting import Greeting
from .components.page import Page


def test_new_component():
    c = Greeting(message="Hello world!", lorem="ipsum")
    print(c.props)
    assert c.props == {
        "message": "Hello world!",
        "with_default": 4,
        "extra": {
            "lorem": "ipsum",
        }
    }


def test_render_simple():
    c = Greeting(message="Hello world!")
    html = c.render().strip()
    assert html == '<div class="greeting">Hello world!</div>'


def test_render_body():
    body = '<button type="button">Close</button>'
    c = Card(body=body)
    html = c.render().strip()
    print(html)
    assert html == f"""
<section class="card">
{body}
<button type="button">&times;</button>
</section>""".strip()


def test_component_uses_other():
    c = Page(message="Hello")
    html = c.render().strip()
    print(html)
    assert """
<section class="card">
<div class="greeting">Hello</div>
<button type="button">Close</button>
<button type="button">&times;</button>
</section>""".strip() in html


def test_assets_included():
    c = Page(message="Hello")
    html = c.render().strip()
    print(html)
    assert '<link href="/components/greeting/Greeting.css" rel="stylesheet">' in html
    assert '<link href="/components/card/Card.css" rel="stylesheet">' in html
    assert '<script src="/components/card/Card.js" defer></script>' in html
    assert '<script src="/components/card/Greeting.js" defer></script>' not in html
