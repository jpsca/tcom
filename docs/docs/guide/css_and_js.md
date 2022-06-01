# Adding CSS and JS

Your components might need custom styles or custom JavaScript for many reasons. Instead of using global stylesheet or scripts files, writing assets per individual component has several advantages:

- **Portability**: You can copy a component from one project to another kmowing it will keep working as expected.
- **Performance**: On each page, only load the css and js that you need. Also, the browser will already have cached the assets of the components for other pages that use them.
- **Simple testing**: You can test the JS of a component indepently from others.


## Declaring assets

The css and/or the js of a component must be declared in the metatada header:

```toml
{#
css = [ ... ]
js = [ ... ]

...
#}
```

The filepaths must be relative to the root of your components catalog (e.g.: `components/`). Both of these list are optional.


## Including assets in your pages

The catalog will collect all css and js file paths from the components used on a "page" render on the `catalog.collected_css` and `catalog.collected_js` lists.

For example, after rendering this component:

```html+jinja title="components/MyPage.html.jinja"
{#
css = ['mypage.css']
js = ['mypage.js']
-#}
<Layout title="My page">
  <Card>
    <CardBody>
      <h1>Lizard</h1>
      <p>The Iguana is a type of lizard</p>
    </CardBody>
    <CardActions>
      <Button size="small">Share</Button>
    </CardActions>
  </Card>
</Layout>
```

Asuming the `Card`, and `Button` components declare css assests, this will the state of the `collected_css` list:

```py
catalog.collected_css
['mypage.css', 'card.css', 'button.css']
```

You can add the `<link>` and `<script>` tags in your page automatically by rendering the global `components_assets` variable in your layout component like this:

```html+jinja title="components/Layout.html.jinja" hl_lines="7"
{# title = '' #}
<!DOCTYPE html>
<html lang="en">
<head>
	<meta charset="utf-8">
	<title>{{ title }}</title>
	{{ components_assets }}
</head>
<body>
	{{ content }}
</body>
</html>
```

The variable will be rendered as:

```html
<link rel="stylesheet" href="/static/components/mypage.css">
<link rel="stylesheet" href="/static/components/card.css">
<link rel="stylesheet" href="/static/components/button.css">
<script src="/static/components/mypage.js" defer></script>
<script src="/static/components/card.js" defer></script>
<script src="/static/components/button.js" defer></script>
```

## Middleware

The tags above will not work at all if your application can't return the content of those files, and right now it can't.

For that reason, TemplateComponents include a WSGI middleware that will process those URLs if you add it to your application.

```py
from flask import Flask
from tcom import Catalog

app = Flask(__name__)

# Here we add the flask Jinja globals, filters, etc.
# like `url_for()`
catalog = tcom.Catalog(
    globals=app.jinja_env.globals,
    filters=app.jinja_env.filters,
    tests=app.jinja_env.tests,
    extensions=app.jinja_env.extensions,
)
catalog.add_folder("myapp/components")

app.wsgi_app = catalog.get_middleware(
    app.wsgi_app,
    autorefresh=app.debug,
)
```

The middleware uses the battle-tested [Whitenoise library](http://whitenoise.evans.io/) and it will only respond to the *.css* and *.js* files inside the component(s) folder(s) (you can configure it to also return files with other extensions).


## Good practices

### CSS Scoping

The styles of your components will not be auto-scoped. This means the styles of a component can affect other components, and, likewise, it will be affected by global styles or the styles of other components.

To protect yourself against that, always add a custom class to the root element of your components and use it to scope the rest of the component styles. Always use a class instead of an id, or the component will not be usable more than once per page.

Example:

```html+jinja title="components/Card.html.jinja"
{# css=['card.css'] }
{% do attrs.add_class("Card") -%}

<div {{ attrs.render() }}>
  <h1>My Card</h1>
  ...
</div>
```

```css title="components/card.css"
/* 🚫 DO NOT do this */
h1 { font-size: 2em; }

/* 👍 DO THIS instead */
.Card h1 { font-size: 2em; }
```

### JS events

Your components might be inserted in the page on-the fly, after the JavaScript files has been loaded and executed. So, attaching events to the elements on the page on load will not be enough:

```js title="components/card.js"
// This will fail for any Card component inserted after page load
document.querySelectorAll('.Card button.share')
  .forEach( (node) => {
    node.addEventListener("click", handleClick)
  })

/* ... etc ... */
```

An alternative can be using the `MutationObserver` JS API to detect changes to the document and re-attach the event to all the components present:

```js title="components/card.js"
new MutationObserver( (mutationList) => {
  mutationList.forEach( (mutation) => {
    if (mutation.type !== "childList") return
    mutation.addedNodes.forEach( (node) => {
      if (node.nodeType === 1) {
        addEvents(node)
      }
    })
  })
})
.observe(document.body, {
    subtree: true,
    childList: true,
    attributes: false,
    characterData: false
})

function addEvents (root) {
  /* Attach events to all the child components
  of the new node */
  root.querySelectorAll('.Card button.share')
    .forEach( (node) => {
      node.addEventListener("click", handleClick)
    })
}

// We call it a first time to attach the events for the
// components present on the document on page load
addEvents(document)

/* ... etc ... */
```
