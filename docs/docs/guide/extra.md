# Extra Attributes

If you pass attributes not declared in a component, those are not discarded, but rather collected in a `attrs` object that can render these extra attributes calling `attrs.render()`

For example, this component:

`components/Card.html.jinja`
```html+jinja
{# title = ... #}
<div {{ attrs.render() }}>
  <h1>{{ title }}</h1>
  {{ content }}
</div>
```

Called as:

```html+jinja
<Card title="Products" class="bg-blue-500 mb-10" open>
bla
</Card>
```

Will be rendered as:

```html
<div class="bg-blue-500 mb-10" open>
  <h1>Products</h1>
  bla
</div>
```


## `attrs` methods

You can add or remove attributes before rendering them using the other methods of the `attrs` object. For example:

```html+jinja
{# title = ... #}
{% do attrs.add_class("card") %}
<div {{ attrs.render() }}>
  <h1>{{ title }}</h1>
  {{ content }}
</div>
```

### `.add(name, value=True)`

Adds an attribute or sets a property. Pass a name and a value to set an attribute. Omit the value or use `True` as value to set a property instead.

### `.remove(name)`

Removes an attribute or property.

### `.add_class(cls_name)`

Adds a class to the list of classes.

### `.remove_class(cls_name)`

Removes a class to the list of classes.

### `.setdefault(name, value=True)`

Adds an attribute or sets a property, but only if it's not already present. Pass a name and a value to set an attribute. Omit the value or use `True` as value to set a property instead.

### `.update(dd=None, **kw)`

Updates several attributes/properties with the values of `dd` and `kw` dicts.

### `.get(name, default=None)`

Returns the value of the attribute or property, or the default value if it doesn't exists.

### `.render()`

Renders the attributes and properties as a string.
To provide consistent output, the attributes and properties are sorted by name and rendered like this: `<sorted attributes> + <sorted properties>`.

