from jinjax import Component
from ..card import Card
from ..greeting import Greeting


class Page(Component):
    uses = {Card, Greeting}

    title: str = "Hi"
    message: str
