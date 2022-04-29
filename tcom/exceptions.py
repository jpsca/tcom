class ComponentNotFound(Exception):
    pass


class MissingRequiredAttr(Exception):
    def __init__(self, component: str, attr: str) -> None:
        msg = f"`{component}` component requires a `{attr}` attribute"
        super().__init__(msg)


class InvalidFrontMatter(Exception):
    pass
