import pytest
from jinja2 import Environment

from jinjax import JinjaX


@pytest.fixture
def pre():
    env = Environment()
    return JinjaX(env)


def test_nested(pre):
    source = """
<div class="whatever">
    <Card label="Hello">
        <MyButton color="red blue" shadowSize={{size}}>
            <Icon name="ok" /> Click Me
            {{ whatever }}
        </MyButton>
    </Card>
    <label>meh</label>
</div>"""

    result = pre.preprocess(source)
    print(result)

    assert result == """
<div class="whatever">
    {% call Card._new(label="Hello") -%}
        {% call MyButton._new(color="red blue", shadowSize=size) -%}
            {{ Icon._new(name="ok") }} Click Me
            {{ whatever }}
        {%- endcall %}
    {%- endcall %}
    <label>meh</label>
</div>"""


def test_expr_prop(pre):
    source = "<MyComponent foo={{1 + 2 + 3 + 4}} />"
    result = pre.preprocess(source)
    print(result)
    assert result == "{{ MyComponent._new(foo=1 + 2 + 3 + 4) }}"
