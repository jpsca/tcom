from oot import Component


class Greeting(Component):
    css = {"greeting/Greeting.css"}

    message: str
    with_default: int = 4

    @property
    def custom_property(self):
        return "foobar"

    def custom_method(self):
        pass
