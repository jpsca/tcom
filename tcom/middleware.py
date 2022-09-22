from typing import TYPE_CHECKING

from whitenoise import WhiteNoise  # type: ignore

if TYPE_CHECKING:
    from typing import Any, Callable, Optional
    from whitenoise.responders import StaticFile  # type: ignore


class ComponentsMiddleware(WhiteNoise):
    """WSGI middleware for serving components assets"""
    allowed_ext = None

    def __init__(self) -> None:
        super().__init__(application=None)

    def configure(
        self,
        *,
        application: "Optional[Callable]" = None,
        allowed_ext: "Optional[tuple[str, ...]]" = None,
        **kw
    ):
        if application:
            self.application = application
        if allowed_ext:
            self.allowed_ext = tuple(allowed_ext)
        for attr in self.config_attrs:
            if attr in kw:
                setattr(self, attr, kw[attr])

    def find_file(self, url: str) -> "Optional[StaticFile]":
        if not self.allowed_ext or url.endswith(self.allowed_ext):
            return super().find_file(url)
        return None

    def add_file_to_dictionary(self, url: str, path: str, stat_cache: "Any") -> None:
        if not self.allowed_ext or url.endswith(self.allowed_ext):
            super().add_file_to_dictionary(url, path, stat_cache)
