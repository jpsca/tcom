from typing import TYPE_CHECKING

from whitenoise import WhiteNoise  # type: ignore

if TYPE_CHECKING:
    from typing import Any, Iterable, Optional
    from whitenoise.responders import StaticFile  # type: ignore


class ComponentsMiddleware(WhiteNoise):
    """WSGI middleware for serving components assets"""

    def __init__(
        self, application, *, allowed_ext: "Optional[Iterable[str]]" = None, **kw
    ) -> None:
        self.allowed_ext = tuple(allowed_ext) if allowed_ext else None
        super().__init__(application, **kw)

    def find_file(self, url: str) -> "Optional[StaticFile]":
        if not self.allowed_ext or url.endswith(self.allowed_ext):
            return super().find_file(url)
        return None

    def add_file_to_dictionary(self, url: str, path: str, stat_cache: "Any") -> None:
        if not self.allowed_ext or url.endswith(self.allowed_ext):
            super().add_file_to_dictionary(url, path, stat_cache)
