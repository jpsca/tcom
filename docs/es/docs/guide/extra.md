# Atributos extra

Si le pasas atributos no declarados a un componentes, estos no son descartados si no, en cambio, recogidos en un objeto `attrs` que puede renderizar estos atributos extra llamando a `attrs.render()`

Por ejemplo, este componente:

```html+jinja title="components/Card.html.jinja"
{# title = ... #}
<div {{ attrs.render() }}>
  <h1>{{ title }}</h1>
  {{ content }}
</div>
```

usado como:

```html+jinja
<Card title="Products" class="bg-blue-500 mb-10" open>
bla
</Card>
```

será renderizado a:

```html
<div class="bg-blue-500 mb-10" open>
  <h1>Products</h1>
  bla
</div>
```

Puedes agregar o quitar atributos, antes de renderizarlos, usando los otros métodos del objeto `attrs`. Por ejemplo:

```html+jinja
{# title = ... #}
{% do attrs.add_class("card") -%}

<div {{ attrs.render() }}>
  <h1>{{ title }}</h1>
  {{ content }}
</div>
```

## Métodos de `attrs`

### `.add(name, value=True)`

Agrega un atributo (ej. `type="text"`) o activa una propiedad (ej. `disabled`). Usa un nombre y un valor para agregar un atributo, u omite el valor o usa `True` como valor para activar una propiedad.

```html+jinja
{% do attrs.add("disabled") %}
{% do attrs.add("readonly", True) %}
{% do attrs.add("data-test", "foobar") %}
{% do attrs.add("id", 3) %}
```

### `.remove(name)`

Elimina un atributo o propiedad.

```html+jinja
{% if active -%}
{% do attrs.remove("disabled") %}
{%- endif %}
```

### `.add_class(name)` / `.add_classes(name1, name2, ...)`

Agrega una o más clases a la lista de clases.

```html+jinja
{% do attrs.add_class("card") %}
{% do attrs.add_classes("active", "animated", "bright") %}
{% do attrs.add_classes("active animated bright") %}
```

### `.remove_class(name)` / `.remove_classes(name1, name2, ...)`

Elimina una o más clases de la lista de clases.

```html+jinja
{% do attrs.remove_class("hidden") %}
{% do attrs.remove_classes("active", "animated") %}
```

### `.setdefault(name, value)`

Agrega un atributo (ej. `type="text"`), *pero solo si no está ya presente*.

```html+jinja
{% do attrs.setdefault("aria-label", "Products") %}
```

### `.update(dd=None, **kw)`

Actualiza varios atributos o propiedades al mismo tiempo.

```html+jinja
{%- do attrs.update(
    role="tab",
    aria_selected="true" if active else "false",
    aria_controls=target,
    tabindex="0" if active else "-1",
) -%}
```

Los guiones bajos en los nombres serán reemplazados automáticamente por guiones, así que `aria_selected` se volverá el atributo `aria-selected`.

### `.get(name, default=None)`

Devuelve el valor del atributo, o el valor de `default` si el atributo no existe.

```html+jinja
{%- set role = attrs.get("role", "tab")
```

### `.render()`

Renderiza los atributos y propiedades como un texto.
Para dar un resultado consistente, los atributos y propiedades se ordenan alfabéticamente por nombre y renderizados así: `<attributor ordenados> + <propiedades ordenadas>`.

```html+jinja
<button {{ attrs.render() }}>
  {{ content }}
</button>
```

!!! warning "Cuidado"
    Usar `{{ attrs.render() }}` como un atributo en otros componentes **no funcionará**, porque los componentes se convierten a macros antes que renderizar la página.

    Si necesitas que funcione, debes usar el atributo especial `__attrs`.

    ```html+jinja
    {#--- MUY MAL 😵 ---#}
    <MyButton {{ attrs.render() }} />

    {#--- BIEN 👍 ---#}
    <MyButton __attrs={{ attrs }} />

    {#--- TAMBIÉN UNA OPCIÓN ---#}
    {# btn_class = '' #}
    <MyButton class={{ btn_class }}/>
    ```
