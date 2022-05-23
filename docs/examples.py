from logging import root
from pathlib import Path

import tcom


here = Path(__file__).parent
dest = here / "docs" / "static" / "examples"

catalog = tcom.Catalog(
    root_url="/docs/static/examples/"
)
catalog.add_folder(here / "examples")

for name in catalog.components:
    if name.startswith("Ex"):
        html = catalog.render(name)
        path = dest / f"{name}.html"
        print(path)
        path.write_text(html)
