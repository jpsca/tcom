from typing import Any, Iterable, Optional

from whitenoise import WhiteNoise  # type: ignore
from whitenoise.responders import StaticFile  # type: ignore


class ComponentsMiddleware(WhiteNoise):
    """WSGI middleware for serving components assets"""

    def __init__(
        self, application, *, allowed_ext: Optional[Iterable[str]] = None, **kwargs
    ) -> None:
        self.allowed_ext = tuple(allowed_ext) if allowed_ext else None
        super().__init__(application, **kwargs)

    def find_file(self, url: str) -> Optional[StaticFile]:
        if self.allowed_ext and not url.endswith(self.allowed_ext):
            return None
        return super().find_file(url)

    def add_file_to_dictionary(self, url: str, path: str, stat_cache: Any) -> None:
        if self.allowed_ext and not url.endswith(self.allowed_ext):
            return None
        return super().add_file_to_dictionary(url, path, stat_cache)
