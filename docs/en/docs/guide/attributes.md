# Component Attributes

More often than not, a component takes one or more attributes to render. Every attribute must be declared in the metadata section (the comment at the top) of the component.

```html+jinja title="components/Form.jinja"
{#
action = ...
method = 'post'
multipart = false
#}
<form method="{{ method }}" action="{{ action }}"
  {%- if multipart %} enctype="multipart/form-data"{% endif %}
>
  {{ content }}
</form>
```

In this example, the component takes three attributes: "action", "method", and "multipart". The last two have a default value, so they are optional, but the first one has `...` as value. That means that it must be passed when rendering this component.

!!! note

    Required attributes must have a value of three dots **without quotes**.

So all of these are valid forms to use this component:

```html+jinja
<Form action="/new">...</Form>
<Form action="/new" method="PATCH">...</Form>
<Form multipart={False} action="/new">...</Form>
```

The values of the declared attributes can be used in the template as values with the same name.


## Non-string attributes

In the example above, both "action" and "method" are strings, but "multipart" is a boolean, so we cannot pass it like `multipart="false"`
because that will make it a string that evaluates as `True`, which is the opposite of what we want.

Instead, you must use curly brackets instead of quotes (`name={value}` instead of `name="value"`).

Between the brackets, you can use datetimes, objects, lists, or any Python expressions.

```html+jinja
{# A datetime value #}
<DateTime date={datetime_value} />

{# A query result #}
<Post post={post} />

{# In-place calculations #}
<FooBar number={2**10} />

{# A list #}
<FooBar items={[1,2,3,4]} />
```


## Components with content

So far we have seen self-closing components, but there is another, much more useful type: components that wrap other HTML content and/or other components.

```html+jinja
{# Self-closing component #}
<Name attributes />

{# Component with content #}
<Name attributes> ...content here... </Name>
```

A great use case is to make layout components:

```html+jinja title="components/PageLayout.jinja"
{# title = ... #}
<!DOCTYPE html>
<html lang="en">
<head>
	<meta charset="utf-8">
	<title>{{ title }}</title>
</head>
<body>
{{ content }}
</body>
```

```html+jinja title="components/ArchivePage.jinja"
{# posts = ... #}
<PageLayout title="Archive">
  {% for post in posts %}
  <Post post={ post }} />
  {% endfor %}
</PageLayout>
```

Everything between the open and close tags of the components will be rendered and passed to the `PageLayout` component as a special, implicit, `content` variable.

To test a component in isolation, you can also manually send a content attribute using the special `__content` attribute:

```python
catalog.render("PageLayout", title="Hello world", __content="TEST")
```

## Extra attributes

If you pass attributes not declared in a component, those are not discarded, but rather collected in a `attrs` object. Read more about it in the next section.
