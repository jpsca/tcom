import pytest
from jinja2 import Environment

from tcom.jinjax import JinjaX


@pytest.fixture
def pre() -> JinjaX:
    env = Environment()
    return JinjaX(env)


def test_nested(pre: JinjaX):
    source = """
<div class="whatever">
    <Card label="Hello">
        <MyButton color="red blue" shadowSize={{ size }}>
            <Icon name="ok" /> Click Me
            {{ whatever }}
        </MyButton>
    </Card>
    <label>meh</label>
</div>"""

    result = pre.preprocess(source)
    print(result)

    assert (
        result
        == """
<div class="whatever">
    {% call __render("Card", label="Hello") -%}
        {% call __render("MyButton", color="red blue", shadowSize=size) -%}
            {{ __render("Icon", name="ok") }} Click Me
            {{ whatever }}
        {%- endcall %}
    {%- endcall %}
    <label>meh</label>
</div>"""
    )


def test_expr_prop(pre: JinjaX):
    source = "<MyComponent foo={{1 + 2 + 3 + 4}} />"
    result = pre.preprocess(source)
    print(result)
    assert result == '{{ __render("MyComponent", foo=1 + 2 + 3 + 4) }}'


def test_multiple_args(pre: JinjaX):
    source = "<MyComponent a={{ a }} b={{ b }} c={{c}} />"
    result = pre.preprocess(source)
    print(result)
    assert result == '{{ __render("MyComponent", a=a, b=b, c=c) }}'


def test_line_jump_in_attr_value(pre: JinjaX):
    source = """
        <Tab
          classes="a
          b"
        >Tab 1</Tab>
    """.strip()
    result = pre.preprocess(source)
    print(result)
    assert (
        result
        == '{% call __render("Tab", classes="a           b") -%}Tab 1{%- endcall %}'
    )
