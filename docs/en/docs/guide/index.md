# Getting started

## Installation

Install the package using `pip`.

```bash
pip install tcom
```

## Usage

The first thing you must do in your app is to create a "catalog" of components. This is the object that manage the components and its global settings. Then, you add to the catalog the folder(s) with your components.

```python
from tcom import Catalog

catalog = Catalog()
catalog.add_folder("myapp/components")
```

You use the catalog to render a parent component from your views:

```python
def myview():
  ...
  return catalog.render(
    "ComponentName",
    title="Lorem ipsum",
    message="Hello",
  )

```

## Components

The components are `.jinja` files. The name of the file before the first dot is the component name and it **must** begin with an uppercase letter. This is the only way to distinguish themn from regular HTML tags.

For example, if the filename es `PersonForm.html.jinja`, the name of the component is `PersonForm` and can be used like `<PersonForm>...</PersonForm>`.

A component can begin with a Jinja comment where it declare what attributes it takes. This metadata is in [TOML](https://toml.io/) format.

```html+jinja
{#
title = ...
message = ...
#}
<h1>{{ title }}</h1>
<div>{{ message }}. This is my component</div>
```

## Jinja

Template Components use Jinja internally to render the templates. You can add your own global variables and functions, filters, tests, and Jinja extensions when creating the catalog:

```python
from tcom import Catalog

catalog = Catalog(
    globals={ ... },
    filters={ ... },
    tests={ ... },
    extensions=[ ... ],
)
```

or afterwards.

```python
catalog.globals.update({ ... })
catalog.filters.update({ ... })
catalog.tests.update({ ... })
catalog.extensions.extend([ ... ])
```

If you use **Flask**, for example, you should pass the values of its own Jinja environment:

```python
app = Flask(__name__)

catalog = tcom.Catalog(
    globals=app.globals,
    filters=app.filters,
    tests=app.tests,
    extensions=app.extensions,
)
```

The ["do" extension](https://jinja.palletsprojects.com/en/3.0.x/extensions/#expression-statement) is enabled by default, so you can write things like:

```html+jinja
{% do attrs.add_class("btn") %}
```
