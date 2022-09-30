import pytest

from tcom import Component, InvalidProp


def test_load_props():
    com = Component(
        name="Test.jinja",
        source='{#def message, lorem=4, ipsum="bar" -#}\n',
    )
    assert com.required == ["message"]
    assert com.optional == {
        "lorem": 4,
        "ipsum": "bar",
    }


def test_expression_props():
    com = Component(
        name="Test.jinja",
        source="{#def expr=1 + 2 + 3, a=1 -#}\n",
    )
    assert com.required == []
    assert com.optional == {
        "expr": 6,
        "a": 1,
    }


def test_lowercase_booleans():
    com = Component(
        name="Test.jinja",
        source="{#def a=false, b=true -#}\n",
    )
    assert com.optional == {
        "a": False,
        "b": True,
    }


def test_no_props():
    com = Component(
        name="Test.jinja",
        source="\n",
    )
    assert com.required == []
    assert com.optional == {}


BAD_PROPS = [
    "000abc",
    "lorem ipsum",
    "lorem=ipsum",
    "lorem='ipsum', wat",
    "a-b",
]


def test_bad_props():
    for bad_prop in BAD_PROPS:
        with pytest.raises(InvalidProp):
            source = "{#def %s -#}\n" % (bad_prop,)
            print(source)
            Component(name="", source=source)


def test_load_assets():
    com = Component(
        name="Test.jinja",
        source='{#css a.css, "b.css", /c.css -#}\n{#js a.js, b.js c.js -#}\n',
        url_prefix="/static/"
    )
    assert com.css == ["/static/a.css", "/static/b.css", "/static/c.css"]
    assert com.js == ["/static/a.js", "/static/b.js c.js"]
