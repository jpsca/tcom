from pathlib import Path
from types import ModuleType
from typing import Any, Dict, Optional, Sequence, Type, Union

from whitenoise import WhiteNoise  # type: ignore
from whitenoise.responders import StaticFile  # type: ignore

import jinjax


DEFAULT_URL_PREFIX = "/components/"
ALLOWED_EXTENSIONS = (".css", ".js", )


class ComponentAssetsMiddleware(WhiteNoise):
    """WSGI middleware for serving components assets"""
    def __init__(
        self,
        application,
        root: Union[str, Type[Path]],
        prefix: str = DEFAULT_URL_PREFIX,
        *,
        importmap: Optional[Dict[str, ModuleType]] = None,
        allowed: Sequence[str] = ALLOWED_EXTENSIONS,
        **kwargs
    ) -> None:
        self.allowed = tuple(allowed)
        prefix = prefix.strip().rstrip("/") + "/"
        super().__init__(application, root=str(root), prefix=prefix, **kwargs)

        importmap = importmap or {}
        importmap["jinjax/"] = jinjax
        for iprefix, mod in importmap.items():
            iprefix = iprefix.strip().strip("/") + "/"
            self.add_files(mod.__path__[0], prefix=f"{prefix}{iprefix}")

    def find_file(self, url: str) -> Optional[StaticFile]:
        if not url.endswith(self.allowed):
            return None
        return super().find_file(url)

    def add_file_to_dictionary(self, url: str, path: str, stat_cache: Any) -> None:
        if not url.endswith(self.allowed):
            return None
        return super().add_file_to_dictionary(url, path, stat_cache)
