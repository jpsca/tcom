from jinjax import Component


class Greeting(Component):
    message: str
    with_default: int = 4

    @property
    def custom_property(self):
        return "foobar"

    def custom_method(self):
        pass
