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

Por ejemplo, si el archivo se llama `PersonForm.jinja`, el nombre del componente es `PersonForm` y puede ser usado como `<PersonForm>...</PersonForm>`.

Un componente puede empezar con un comentario Jinja donde declaras que argumentos puede recibir. Algunos de estos argumentos pueden tener un valor por defecto (haciéndolos opcionales):

```html+jinja
{#def title, message='Hi' #}

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

o después, actualizando el `jinja.Environment` ya creado:

```python
catalog.jinja_env.globals.update({ ... })
catalog.jinja_env.filters.update({ ... })
catalog.jinja_env.tests.update({ ... })
catalog.jinja_env.extensions.extend([ ... ])
```

Si usas **Flask**, por ejemplo, deberías pasarle los valores de su propio entorno Jinja:

```python
app = Flask(__name__)

catalog = tcom.Catalog(
    globals=app.globals,
    filters=app.filters,
    tests=app.tests,
    extensions=app.extensions,
)
```

La [extensión "do"](https://jinja.palletsprojects.com/en/3.0.x/extensions/#expression-statement) está activada por defecto, para que puedas escribir cosas como:

```html+jinja
{% do attrs.add_class("btn") %}
```
