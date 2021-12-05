from .components.button import Button
from .components.card import Card
from .components.greeting import Greeting
from .components.page import Page


def test_new_component():
    c = Greeting(message="Hello world!", lorem="ipsum")
    print(c.props)
    assert c.props == {
        "content": "",
        "message": "Hello world!",
        "with_default": 4,
        "extra": {
            "lorem": "ipsum",
        },
        "custom_property": "foobar",
        "custom_method": c.custom_method,
    }


def test_render_simple():
    c = Greeting(message="Hello world!")
    html = c.render().strip()
    assert html == '<div class="greeting">Hello world!</div>'


def test_render_content():
    content = '<button type="button">Close</button>'
    c = Card(content=content)
    html = c.render().strip()
    print(html)
    assert html == f"""
<section class="card">
{content}
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


def test_render_globals():
    c = Greeting(message="Hello ")
    html = c.render(secret="world!").strip()
    assert html == '<div class="greeting">Hello world!</div>'


def test_init():
    c = Button(type="primary", content="Text")
    assert c.render().strip() == (
        '<button class="disabled:bg-purple-300 focus:bg-purple-600 '
        "hover:bg-purple-600 bg-purple-500 text-white "
        "cursor-pointer rounded transition duration-200 text-center "
        'p-4 whitespace-nowrap font-bold\">Text</button>'
    ).strip()

    c = Button(type="danger", content="Text")
    assert c.render().strip() == (
        '<button class="hover:bg-red-600 focus:bg-red-600 disabled:bg-red-300 '
        "bg-red-500 text-white cursor-pointer rounded transition duration-200 "
        'text-center p-4 whitespace-nowrap font-bold">Text</button>'
    ).strip()
