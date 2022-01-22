import os
from pathlib import Path

import pytest

from oot import cli


def test_new_on_cwd(tmp_path: Path):
    cwd = os.getcwd()
    os.chdir(tmp_path)

    cli.new("FooBar")
    assert (tmp_path / "foo_bar.py").is_file()
    assert (tmp_path / "foo_bar.html.jinja").is_file()
    code = (tmp_path / "foo_bar.py").read_text()
    assert "class FooBar(Component)" in code

    os.chdir(cwd)


def test_new_on_path(tmp_path: Path):
    cli.new("FooBar", path=str(tmp_path))
    assert (tmp_path / "foo_bar.py").is_file()
    assert (tmp_path / "foo_bar.html.jinja").is_file()
    code = (tmp_path / "foo_bar.py").read_text()
    assert "class FooBar(Component)" in code


def test_no_overwrite(tmp_path: Path):
    cli.new("FooBar", path=str(tmp_path))
    with pytest.raises(FileExistsError):
        cli.new("FooBar", path=str(tmp_path))
