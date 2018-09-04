from typing import List, Dict, Any, Union, FrozenSet
from datetime import date, datetime
from enum import Enum

import pytest
import attr
from sanic_attrs import doc
from sanic_attrs import serializer


def test_serialize_any():
    @attr.s
    class Foo:
        bar: Any = doc.field()

    expected = {
        'type': 'object',
        'format': None,
        '$ref': '#/definitions/Foo'
    }
    actual = serializer._serialize_type(Foo, None)
    assert actual == expected


def test_serialize_optionals():
    @attr.s
    class Foo:
        bar: Union[str, None] = doc.field()

    expected = {
        'type': 'object',
        'format': None,
        '$ref': '#/definitions/Foo'
    }
    actual = serializer._serialize_type(Foo, None)
    assert actual == expected


def test_serialize_other_unions():
    @attr.s
    class Foo:
        bar: Union[str, float, bool] = doc.field()

    # TODO: This seems like the wrong response. No "oneOf" data is generated
    #       as part of the final spec.
    expected = {
        'type': 'object',
        'format': None,
        '$ref': '#/definitions/Foo'
    }
    actual = serializer._serialize_type(Foo, None)
    assert actual == expected


def test_enums():
    class Colors(Enum):
        RED: str = 'RED'
        BLUE: str = 'BLUE'

    expected = {
        'type': 'string',
        'format': None,
        '$ref': '#/definitions/Colors'
    }
    actual = serializer._serialize_enum_meta(Colors, None)
    assert actual == expected


def test_generic_collection():
    expected = {
        'type': 'array',
        'items': {
            'type': 'string'
        }
    }
    actual = serializer._serialize_generic_meta(List[str], None)
    assert actual == expected


def test_generic_dict():
    expected = {
        'type': 'object',
        'properties': {
            'key': {
                'type': 'string'
            },
            'value': {
                'type': 'integer', 'format': 'int64'
            }
        }
    }
    actual = serializer._serialize_generic_meta(Dict[str, int], None)
    assert actual == expected


def test_typing_frozenset_is_not_supported():
    with pytest.raises(TypeError):
        serializer._serialize_generic_meta(FrozenSet[str], None)


def test_serialize_custom_attrs_class():
    @attr.s
    class Foo:
        bar: str

    expected = {
        'type': 'object',
        'format': None,
        '$ref': '#/definitions/Foo'
    }
    actual = serializer._serialize_custom_objects(Foo, None)
    assert actual == expected


def test_serialize_custom_attrs_class_with_required_attrs():
    @attr.s
    class Foo:
        bar: str = doc.field(required=True)

    expected = {
        'type': 'object',
        'format': None,
        '$ref': '#/definitions/Foo',
    }
    actual = serializer._serialize_custom_objects(Foo, None)
    assert actual == expected


def test_serialize_integer():
    expected = {'type': 'integer', 'format': 'int64'}
    actual = serializer._serialize_raw_type_information(int, None)
    assert actual == expected


def test_serialize_float():
    expected = {'type': 'number', 'format': 'double'}
    actual = serializer._serialize_raw_type_information(float, None)
    assert actual == expected


def test_serialize_string():
    expected = {'type': 'string'}
    actual = serializer._serialize_raw_type_information(str, None)
    assert actual == expected


def test_serialize_boolean():
    expected = {'type': 'boolean'}
    actual = serializer._serialize_raw_type_information(bool, None)
    assert actual == expected


def test_serialize_date():
    expected = {'type': 'string', 'format': 'date'}
    actual = serializer._serialize_raw_type_information(date, None)
    assert actual == expected


def test_serialize_datetime():
    expected = {'type': 'string', 'format': 'date-time'}
    actual = serializer._serialize_raw_type_information(datetime, None)
    assert actual == expected


def test_serialize_bytes():
    expected = {'type': 'string', 'format': 'byte'}
    actual = serializer._serialize_raw_type_information(bytes, None)
    assert actual == expected


def test_list_raises_exception():
    with pytest.raises(TypeError):
        serializer._serialize_raw_type_information(list, None)


def test_dict_raises_exception():
    with pytest.raises(TypeError):
        serializer._serialize_raw_type_information(dict, None)


def test_that_non_attrs_class_is_unsupported():
    class Foo:
        pass

    with pytest.raises(TypeError):
        serializer._serialize_raw_type_information(Foo, None)


def test_attr_class_is_recursively_checked():
    @attr.s
    class Foo:
        bar: str

    try:
        serializer._serialize_raw_type_information(Foo, None)
    except TypeError:
        pytest.fail()
