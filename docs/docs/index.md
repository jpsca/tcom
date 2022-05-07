# TemplateComponents

A library for creating reusable, testable, encapsulated server-side components, to replace the current HTML spaguetti of partials.

## What's a template component?

A partial template that can be used as an HTML tag in other templates.
Think of TemplateComponents as an evolution of Jinja's macros, inspired by React and Vue.

`components/Greeting.html.jinja`

```html+jinja
{# message = ... #}
<div class="greeting">{{ message }}</div>
```

`components/Page.html.jinja`
```html+jinja
<div>
  <Greeting message="Hello world!" />
</div>
```

## Why use TemplateComponents

With Python, we work hard to write classes or function that are encapsulated, that do one thing well, and that make clear what arguments they take and what kind of output they return.

However, template code often fails basic code standards: long methods, deep conditional nesting, and mystery guests abound.

You can try to organize your templates with partials and macros, but they also quickly become a big ball of HTML mud.

Client-side components (like the ones you write with React) solves all of these problems, but you can't use them if your app is not a "single-page application".

Or rather, you couldn't, until now.


## Resources

- [Source code (MIT Licensed)](https://github.com/jpsca/tcom)
- [PyPI](https://pypi.org/project/tcom/)
- [Change log](https://github.com/jpsca/tcom/releases)
