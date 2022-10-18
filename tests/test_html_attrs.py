from tcom.html_attrs import HTMLAttrs


def test_parse_initial_attrs():
    attrs = HTMLAttrs({
        "title": "hi",
        "data-position": "top",
        "class": "z4 c3 a1 z4 b2",
        "open": True,
        "disabled": False,
    })
    assert attrs.classes == "a1 b2 c3 z4"
    assert attrs.get("class") == "a1 b2 c3 z4"
    assert attrs.get("data-position") == "top"
    assert attrs.get("data_position") == "top"
    assert attrs.get("title") == "hi"
    assert attrs.get("open") is True
    assert attrs.get("disabled", "meh") == "meh"


def test_getattr():
    attrs = HTMLAttrs({
        "title": "hi",
        "class": "z4 c3 a1 z4 b2",
        "open": True,
    })
    assert attrs["class"] == "a1 b2 c3 z4"
    assert attrs["title"] == "hi"
    assert attrs["open"] == True
    assert attrs["lorem"] is None


def test_deltattr():
    attrs = HTMLAttrs({
        "title": "hi",
        "class": "z4 c3 a1 z4 b2",
        "open": True,
    })
    assert attrs["class"] == "a1 b2 c3 z4"
    del attrs["title"]
    assert attrs["title"] is None


def test_render():
    attrs = HTMLAttrs({
        "title": "hi",
        "data-position": "top",
        "class": "z4 c3 a1 z4 b2",
        "open": True,
        "disabled": False,
    })
    assert attrs.render() == 'class="a1 b2 c3 z4" data-position="top" title="hi" open'


def test_set():
    attrs = HTMLAttrs({})
    attrs.set(title="hi")
    attrs.set(data_position="top")
    attrs.set(open=True)
    assert attrs.render() == 'data-position="top" title="hi" open'

    attrs.set(title=False)
    attrs.set(open=False)
    assert attrs.render() == 'data-position="top"'


def test_class_management():
    attrs = HTMLAttrs({
        "class": "z4 c3 a1 z4 b2",
    })
    attrs.set(classes="lorem bipsum lorem a1")

    assert attrs.classes == "a1 b2 bipsum c3 lorem z4"

    attrs.remove_class("bipsum")
    assert attrs.classes == "a1 b2 c3 lorem z4"

    attrs.set(classes=None)
    attrs.set(classes="meh")
    assert attrs.classes == "meh"


def test_setdefault():
    attrs = HTMLAttrs({
        "title": "hi",
    })
    attrs.setdefault(
        title="default title",
        data_lorem="ipsum",
        open=True,
        disabled=False,
    )
    assert attrs.render() == 'data-lorem="ipsum" title="hi"'


def test_as_dict():
    attrs = HTMLAttrs({
        "title": "hi",
        "data-position": "top",
        "class": "z4 c3 a1 z4 b2",
        "open": True,
        "disabled": False,
    })
    assert attrs.as_dict == {
        "class": "a1 b2 c3 z4",
        "data-position": "top",
        "title": "hi",
        "open": True,
    }


def test_as_dict_no_classes():
    attrs = HTMLAttrs({
        "title": "hi",
        "data-position": "top",
        "open": True,
    })
    assert attrs.as_dict == {
        "data-position": "top",
        "title": "hi",
        "open": True,
    }
