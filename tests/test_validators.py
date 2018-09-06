import pytest
import attr
from sanic_swagger.validators import (
    min_str_len,
    max_str_len,
    min_max_str_len
)


@pytest.fixture
def attribute():
    return attr.Attribute(name='just_for_testing',
                          default=attr.NOTHING,
                          validator=None,
                          repr=True,
                          cmp=True,
                          hash=None,
                          init=True,
                          metadata=dict({
                            'min_length': 4,
                            'max_length': 12
                          }),
                          type=None,
                          converter=None,
                          kw_only=False)


@pytest.fixture
def none_attrib():
    return attr.Attribute(name='just_for_testing',
                          default=attr.NOTHING,
                          validator=None,
                          repr=True,
                          cmp=True,
                          hash=None,
                          init=True,
                          metadata=dict({
                            'min_length': None,
                            'max_length': None
                          }),
                          type=None,
                          converter=None,
                          kw_only=False)


def test_min_str_len_does_nothing_with_none(none_attrib):
    try:
        min_str_len(None, none_attrib, 'nevergetschecked')
    except ValueError:
        pytest.fail()


def test_min_str_len_raises_an_error(attribute):
    with pytest.raises(ValueError):
        min_str_len(None, attribute, 'cat')


def test_min_str_len_does_not_raise_an_error(attribute):
    try:
        min_str_len(None, attribute, 'catsfdsa')
    except ValueError:
        pytest.fail('min_str_len validator is broken')


def test_max_str_len_does_nothing_with_none(none_attrib):
    try:
        max_str_len(None, none_attrib, 'nevergetschecked')
    except ValueError:
        pytest.fail()


def test_max_str_len_raises_an_error(attribute):
    with pytest.raises(ValueError):
        max_str_len(None, attribute, 'longerthan12characters')


def test_max_str_len_does_not_raise_an_error(attribute):
    try:
        max_str_len(None, attribute, 'lessthan12')
    except ValueError:
        pytest.fail('max_str_len validator is broken')


def test_min_max_str_len_raises_an_error(attribute):
    with pytest.raises(ValueError):
        min_max_str_len(None, attribute, 'longerthan12characters')


def test_min_max_str_len_does_not_raise_an_error(attribute):
    try:
        min_max_str_len(None, attribute, 'lessthan12')
    except ValueError:
        pytest.fail('max_str_len validator is broken')
