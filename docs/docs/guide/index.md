# Getting started

## Conventions

- A component is a `.jinja` file inside a folder, commonly `yourapp/components`. You can also use subfolders inside to organize your components.
- The component name is the name of the file without extensions, and **must** begin with an uppercase letter.
- All components are auto-imported so the name of a component must be unique.

## Installation

Install the package using `pip`.

```bash
pip install tcom
```

## Usage

The first thing you must do in your app is to create a "catalog" of components. This is the object that manage the components and global settings. Then, you add to the catalog the folder(s) with your components.

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

The components are `.jinja` files whose first letter must be in uppercase. They can begin with a Jinja comment where it declare what attributes it takes. This metadata is in [TOML](https://toml.io/) format.

```html+jinja
{#
title = ...
message = ...
#}
<h1>{{ title }}</h1>
<div>{{ message }}. This is my component</div>
```
