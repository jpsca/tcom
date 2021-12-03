from jinjax import Component


class Greeting(Component):
    message: str
    with_default: int = 4
