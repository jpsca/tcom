# Empieza aquí

## Instalación

Instala el paquete usando `pip`.

```bash
pip install tcom
```

## Como usar

La primera cosa que tienes que hacer, es crear un "catálogo" de componentes. Este es el objeto que maneja los componentes y su configuración global. Luego de eso, añades al catálogo los folders con tus componentes.

```python
from tcom import Catalog

catalog = Catalog()
catalog.add_folder("myapp/components")
```

Usas el catálogo para renderizar los componente de tus vistas:

```python
def posts():
  ...
  return catalog.render(
    "PostsIndex",
    title="Lorem ipsum",
    posts=posts_list,
  )

```

## Componentes

Los components son archivos `.jinja`. El nombre del archivo antes del primer punto es el nombre del componente y **debe** empezar con mayúscula. Esta es la única forma de distinguirlos de etiquetas HTML normales.

Por ejemplo, si el archivo se llama `PersonForm.html.jinja`, el nombre del componente es `PersonForm` y puede ser usado como `<PersonForm>...</PersonForm>`.

Un componente puede empezar con un comentario Jinja donde declaras que atributos puede recibir. Esta metadata está em formato [TOML](https://toml.io/).

```html+jinja
{#
title = ...
message = ...
#}
<h1>{{ title }}</h1>
<div>{{ message }}. Este archivo es un componente</div>
```

## Jinja

Template Components usa Jinja internamente para renderizar las plantillas. Puedes agregar tus propias variables globales, filtros, tests y extensiones de Jinja, al crear el catálogo:

```python
from tcom import Catalog

catalog = Catalog(
    globals={ ... },
    filters={ ... },
    tests={ ... },
    extensions=[],
)
```

o después, diréctamente en el entorno de Jinja creado en `catalog.jinja_env`.

Si usas **Flask**, por ejemplo, deberías pasarle los valores de su propio entorno Jinja:

```python
app = Flask(__name__)

catalog = tcom.Catalog(
    globals=app.jinja_env.globals,
    filters=app.jinja_env.filters,
    tests=app.jinja_env.tests,
    extensions=app.jinja_env.extensions,
)
```

La [extensión "do"](https://jinja.palletsprojects.com/en/3.0.x/extensions/#expression-statement) está activada por defecto, para que puedas escribir cosas como:

```html+jinja
{% do attrs.add_class("btn") %}
```
