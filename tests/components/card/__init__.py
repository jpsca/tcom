from oot import Component
from ..close_btn import CloseBtn


class Card(Component):
    uses = {CloseBtn}
    js = {"card/Card.js"}
    css = {"card/Card.css"}
