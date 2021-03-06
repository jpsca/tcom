# Atributos de componentes

A menudo, un componente toma uno o más atributos para renderizar, podría ser una fecha, una lista de artículos o un texto.

Cada atributo debe ser declarado en la metadata (el comentario al principio) del componente.

```html+jinja title="components/Form.html.jinja"
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

En este ejemplo, el componente toma tres atributos: "action", "method", y "multipart". Los últimos dos tienen un valor por defecto, de modo que son opcionales - no necesitas pasarlos para llamar al componente - pero el primer argumento tiene un `...` como valor. Esto signifca que tienes que pasarle un valor cuando llames al componente.

!!! note "Nota"

    Atributos requeridos tienen un valor de tres puntos **sin comillas**.

Así que todas estas son formas válidas de usar este componente:

```html+jinja
<Form action="/new">...</Form>
<Form action="/new" method="PATCH">...</Form>
<Form multipart={{ false }} action="/new">...</Form>
```

Los valores de los atributos declarados pueden usarse en la plantilla como variables con el mismo nombre.


## Atributos que no son textos

En el ejemplo anterior, tanto "action" como "method" son cadenas de texto, pero "multipart" es un booleano. No podemos pasarlo como `multipart="false"` porque eso lo volveria un texto, que además evaluaría a verdadero, que es lo opuesto a lo que queremos.

En vez de eso, debemos usar la sintáxis de Jinja para imprimir valores (`{{ valor }}`). Dentro, puedes usar fechas, objetos, listas, expresiones de Python, etc.

```html+jinja
{# Un valor de fecha #}
<DateTime date={{ datetime_value }} />

{# Un objeto #}
<Post post={{ post }} />

{# Cálculos al vuelo #}
<FooBar number={{ 2**10 }} />

{# Una lista #}
<FooBar items={{ [1, 2, 3, 4] }} />
```


## Componentes con contenido

Hasta ahora, hemos visto componentes que terminan en `/>`, sin una etiqueta de cierre. Pero hay otro tipo, mucho más útil: componentes que envuelven otras etiquetas HTML y/o a otros componentes.


```html+jinja
{# Componente de cierre automático #}
<Name attributes />

{# Componente con contenido #}
<Name attributes> ...content here... </Name>
```

Un gran caso de uso es hacer componentes de base:

```html+jinja title="components/PageLayout.html.jinja"
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

```html+jinja title="components/ArchivePage.html.jinja"
{# posts = ... #}
<PageLayout title="Archive">
  {% for post in posts %}
  <Post post={{ post }} />
  {% endfor %}
</PageLayout>
```

Todo entre las etiquetas inicial y de cierre del componente será renderizado y pasado al componente `PageLayout` en una variable implícita especial `content`.

Para probar un componente en aislamiento, puedes también definir manualmente el contenido con el atributo especial `__content`:

```python
catalog.render("PageLayout", title="Hello world", __content="TEST")
```

## Atributos extra

Si le pasas atributos no declarados a un componentes, estos no son descartados, si no, en cambio, recogidos en un objeto `attrs`. Lee más acerca de esto en la siguiente sección.
