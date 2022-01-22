from oot import Component, required
from .card import Card
from .greeting import Greeting


class Page(Component):
    uses = {Card, Greeting}
    js = ("page.js", )
    css = ("page.css", )

    title: str = "Hi"
    message = required
