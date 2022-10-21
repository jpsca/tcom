# Argumentos extra

Si le pasas argumentos no declarados a un componentes, estos no son descartados si no, en cambio, recogidos en un objeto `attrs` que puede renderizar estos argumentos extra llamando a `attrs.render()`

Por ejemplo, este componente:

```html+jinja title="components/Card.jinja"
{#def title #}

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

Puedes agregar o quitar argumentos, antes de renderizarlos, usando los otros métodos del objeto `attrs`. Por ejemplo:

```html+jinja
{#def title #}

{% do attrs.add_class("card") -%}
<div {{ attrs.render() }}>
  <h1>{{ title }}</h1>
  {{ content }}
</div>
```

## Métodos de `attrs`

### `.set(name=value, ...)`

Agrega un atributo o activa una propiedad:
- Usa un nombre y un valor para agregar un atributo (ej. `type="text"`)
- Usa `True` como valor para activar una propiedad (ej. `disabled`)
- Usa `False` como valor para quitar un atributo o propiedad

Los guiones bajos en los nombres serán reemplazados automáticamente por guiones, así que `aria_selected` se volverá el atributo `aria-selected`.

Los atributos o propiedades son sobreescritos **excepto** si se trata de "class" o "classes".
En esos casos, las nuevas clases se agregan a las antiguas en vez de reemplazarlas.

```html+jinja title="Agregando atributos/propiedades"
{% do attrs.set(
  id="loremipsum",
  disabled=True,
  data_test="foobar",
  class="m-2 p-4",
) %}
```

```html+jinja title="Quitando atributos/propiedades"
{% do attrs.set(
  title=False,
  disabled=False,
  data_test=False,
  class=False,
) %}
```


### `.setdefault(name=value, ...)`

Agrega un atributo (ej. `type="text"`), *pero solo si no está ya presente*.

```html+jinja
{% do attrs.setdefault("aria-label", "Products") %}
```


### `.remove_class(name1, name2, ...)`

Elimina una o más clases de la lista de clases.

```html+jinja
{% do attrs.remove_class("hidden") %}
{% do attrs.remove_classes("active", "animated") %}
```

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
    Usar `{{ attrs.render() }}` para pasar los argumentos extra a otros componentes **NO FUNCIONARÁ**. Esto es porque los componentes se convierten a macros antes de renderizar la página.

    Si necesitas que funcione, debes usar el argumento especial `__attrs`.

    ```html+jinja
    {#--- MUY MAL 😵 ---#}
    <MyButton {{ attrs.render() }} />

    {#--- BIEN 👍 ---#}
    <MyButton __attrs={ attrs } />
    ```

    Otra opción es definir explícitamente que argumentos necesitan los sub-componentes:

    ```html+jinja
    {#def btn_class='' #}

    <MyButton class={btn_class} />
    ```
