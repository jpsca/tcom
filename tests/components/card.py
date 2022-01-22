from oot import Component
from .close_btn import CloseBtn


class Card(Component):
    uses = {CloseBtn}
    js = ("card.js", )
    css = ("card.css", )
