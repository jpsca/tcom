from pathlib import Path

from .catalog import Catalog  # noqa
from .exceptions import *  # noqa


components_path = Path(__file__).parent / "js"
prefix = "tcom"
