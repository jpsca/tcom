# Extra Arguments

If you pass arguments not declared in a component, those are not discarded, but rather collected in a `attrs` object that can render these extra arguments calling `attrs.render()`

For example, this component:

```html+jinja title="components/Card.jinja"
{#def title #}

<div {{ attrs.render() }}>
  <h1>{{ title }}</h1>
  {{ content }}
</div>
```

Called as:

```html+jinja
<Card title="Products" class="mb-10" open>bla</Card>
```

Will be rendered as:

```html
<div class="mb-10" open>
  <h1>Products</h1>
  bla
</div>
```

You can add or remove arguments before rendering them using the other methods of the `attrs` object. For example:

```html+jinja
{#def title #}

{% do attrs.add_class("card") -%}
<div {{ attrs.render() }}>
  <h1>{{ title }}</h1>
  {{ content }}
</div>
```

## `attrs` methods

### `.add(name, value=True)`

Adds an attribute (e.g. `type="text"`) or sets a property (e.g. `disabled`). Pass a name and a value to set an attribute. Omit the value or use `True` as value to set a property instead.

```html+jinja
{% do attrs.add("disabled") %}
{% do attrs.add("readonly", True) %}
{% do attrs.add("data-test", "foobar") %}
{% do attrs.add("id", 3) %}
```

### `.remove(name)`

Removes an attribute or property.

```html+jinja
{% if active -%}
{% do attrs.remove("disabled") %}
{%- endif %}
```

### `.add_class(name)` / `.add_classes(name1, name2, ...)`

Adds one or more classes to the list of classes
(both are actually the same method).

```html+jinja
{% do attrs.add_class("card") %}
{% do attrs.add_classes("active", "animated", "bright") %}
{% do attrs.add_classes("active animated bright") %}
```

### `.remove_class(name)` / `.remove_classes(name1, name2, ...)`

Removes one or more classes from the list of classes
(both are actually the same method).

```html+jinja
{% do attrs.remove_class("hidden") %}
{% do attrs.remove_classes("active", "animated") %}
```

### `.setdefault(name, value=True)`

Adds an attribute or sets a property, *but only if it's not already present*. Pass a name and a value to set an attribute. Omit the value or use `True` as value to set a property instead.

```html+jinja
{% do attrs.setdefault("aria-label", "Products") %}
```

### `.update(dd=None, **kw)`

Updates several attributes/properties with the values of `dd` and `kw` dicts.

```html+jinja
{%- do attrs.update(
    role="tab",
    aria_selected="true" if active else "false",
    aria_controls=target,
    tabindex="0" if active else "-1",
) -%}
```

The underscores in the names will be translated automatically to dashes, so `aria_selected` will become the attribute `aria-selected`.

### `.get(name, default=None)`

Returns the value of the attribute or property, or the default value if it doesn't exists.

```html+jinja
{%- set role = attrs.get("role", "tab")
```

### `.render()`

Renders the attributes and properties as a string.
To provide consistent output, the attributes and properties are sorted by name and rendered like this: `<sorted attributes> + <sorted properties>`.

```html+jinja
<button {{ attrs.render() }}>
  {{ content }}
</button>
```

!!! warning
    Using `<Component {{ attrs.render() }}>` to pass the extra arguments to other components **WILL NOT WORK**. That is because the components are translated to macros before the page render.

    You must pass them as the special argument `__attrs`.

    ```html+jinja
    {#--- WRONG 😵 ---#}
    <MyButton {{ attrs.render() }} />

    {#--- GOOD 👍 ---#}
    <MyButton __attrs={attrs} />
    ```

    Another options is to explicity define which arguments are needed for the sub-components:

    ```html+jinja
    {#def btn_class='' #}

    <MyButton class={btn_class} />
    ```
