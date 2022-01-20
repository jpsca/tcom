from oot import Component, required
from ..card import Card
from ..greeting import Greeting


class Page(Component):
    uses = {Card, Greeting}
    js = {"page/Page.js"}
    css = {"page/Page.css"}

    title: str = "Hi"
    message = required
