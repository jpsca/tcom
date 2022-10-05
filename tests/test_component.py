import pytest

from tcom import Component, InvalidArgument


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


def test_fails_when_invalid_name():
    with pytest.raises(InvalidArgument):
        source = "{#def 000abc -#}\n"
        co = Component(name="", source=source)
        print(co.required, co.optional)


def test_fails_when_missing_comma_between_props():
    with pytest.raises(InvalidArgument):
        source = "{#def lorem ipsum -#}\n"
        co = Component(name="", source=source)
        print(co.required, co.optional)


def test_fails_when_missing_quotes_arround_default_value():
    with pytest.raises(InvalidArgument):
        source = "{#def lorem=ipsum -#}\n"
        co = Component(name="", source=source)
        print(co.required, co.optional)


def test_fails_when_prop_is_expression():
    with pytest.raises(InvalidArgument):
        source = "{#def a-b -#}\n"
        co = Component(name="", source=source)
        print(co.required, co.optional)


def test_fails_when_extra_comma_between_props():
    with pytest.raises(InvalidArgument):
        source = "{#def a, , b -#}\n"
        co = Component(name="", source=source)
        print(co.required, co.optional)


def test_comma_in_default_value():
    com = Component(
        name="Test.jinja",
        source="{#def a='lorem, ipsum' -#}\n",
    )
    assert com.optional == {"a": "lorem, ipsum"}


def test_load_assets():
    com = Component(
        name="Test.jinja",
        source='{#css a.css, "b.css", /c.css -#}\n{#js a.js, b.js, c.js -#}\n',
        url_prefix="/static/"
    )
    assert com.css == ["/static/a.css", "/static/b.css", "/static/c.css"]
    assert com.js == ["/static/a.js", "/static/b.js", "/static/c.js"]


def test_no_comma_in_assets_list_is_your_problem():
    com = Component(
        name="Test.jinja",
        source="{#js a.js b.js c.js -#}\n",
        url_prefix="/static/"
    )
    assert com.js == ["/static/a.js b.js c.js"]
