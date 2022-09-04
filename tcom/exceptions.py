class ComponentNotFound(Exception):
    def __init__(self, name: str) -> None:
        msg = f"File with pattern `{name}` not found"
        super().__init__(msg)


class MissingRequiredAttr(Exception):
    def __init__(self, component: str, attr: str) -> None:
        msg = f"`{component}` component requires a `{attr}` attribute"
        super().__init__(msg)


class InvalidFrontMatter(Exception):
    pass
