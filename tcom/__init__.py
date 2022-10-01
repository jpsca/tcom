from pathlib import Path

from .catalog import Catalog  # noqa
from .component import Component  # noqa
from .exceptions import *  # noqa
from .html_attrs import HTMLAttrs  # noqa


components_path = Path(__file__).parent / "js"
prefix = "tcom"
