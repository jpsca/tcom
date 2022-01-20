import os
import shutil
from pathlib import Path
from tempfile import mkdtemp

import pytest

from oot import cli


@pytest.fixture()
def cwd():
    """Set the current working directory to a real temporary folder path
    which is unique to each test function invocation.
    The original working directory is restored at the end.
    """
    dst = mkdtemp()
    cwd = os.getcwd()
    os.chdir(dst)
    yield Path(dst)
    os.chdir(cwd)
    shutil.rmtree(dst)


def test_new(cwd: Path):
    cli.new("FooBar")
    assert (cwd / "foo_bar").is_dir()
    assert (cwd / "foo_bar" / "__init__.py").is_file()
    assert (cwd / "foo_bar" / "FooBar.html.jinja").is_file()
    code = (cwd / "foo_bar" / "__init__.py").read_text()
    assert "class FooBar(Component)" in code


def test_no_overwrite(cwd: Path):
    cli.new("FooBar")
    with pytest.raises(FileExistsError):
        cli.new("FooBar")
