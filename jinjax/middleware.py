from pathlib import Path
from typing import Any, Optional, Sequence, Type, Union

from whitenoise import WhiteNoise  # type: ignore
from whitenoise.responders import StaticFile  # type: ignore

from .component import DEFAULT_URL_PREFIX


ALLOWED_EXTENSIONS = (".css", ".js", )


class ComponentAssetsMiddleware(WhiteNoise):
    """WSGI middleware for serving components assets"""
    def __init__(
        self,
        application,
        root: Union[str, Type[Path], None] = None,
        prefix: str = DEFAULT_URL_PREFIX,
        *,
        allowed: Sequence[str] = ALLOWED_EXTENSIONS,
        **kwargs
    ) -> None:
        self.allowed = tuple(allowed)
        super().__init__(application, root=str(root), prefix=prefix, **kwargs)

    def find_file(self, url: str) -> Optional[StaticFile]:
        if not url.endswith(self.allowed):
            return None
        return super().find_file(url)

    def add_file_to_dictionary(self, url: str, path: str, stat_cache: Any) -> None:
        if not url.endswith(self.allowed):
            return None
        return super().add_file_to_dictionary(url, path, stat_cache)
