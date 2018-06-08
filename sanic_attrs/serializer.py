from datetime import date, datetime
from enum import EnumMeta
from functools import singledispatch
from typing import (
    Any,
    Collection,
    Dict,
    GenericMeta,
    Iterable,
    List,
    Mapping,
    Sequence,
    Set,
    Union,
)

import attr

from .doc import ModelMeta
from .options import metadata_aliases

required_fields = {}
components = {}


def serialize(field, model=None):
    if hasattr(field, "type"):
        return _merge_metadata(
            _serialize_type(field.type, model), field, model
        )
    else:
        return _serialize_type(field, model)


def _generate_component(func):
    def wrapper(type_, model):
        # if model is None:
        #     return func(type_, model)
        output = func(type_, model)
        components[type_] = output
        return {
            "type": output.get("type"),
            "format": output.get("format", None),
            "$ref": "#/definitions/{}".format(type_.__name__),
        }

    return wrapper


def _camel_case(snake_str):
    # from https://stackoverflow.com/a/42450252
    first, *others = snake_str.split("_")
    return "".join([first.lower(), *map(str.title, others)])


def _raise_simple_type(simple_type, *encouraged_type):
    if len(encouraged_type) > 1:
        encouraged = ", ".join([str(t.__name__) for t in encouraged_type])
    else:
        encouraged = str(encouraged_type[0])
    raise TypeError(
        'It is encouraged to use "{}" instead of "{}"'.format(
            encouraged, simple_type.__name__
        )
    )


def _merge_metadata(data, field, model):
    if data.get("type", None) is None:
        return data
    if data["type"] in metadata_aliases:
        for key in metadata_aliases[data["type"]] + metadata_aliases["all"]:
            if key in data:
                continue
            if key in field.metadata:
                data[_camel_case(key)] = field.metadata.get(key, None)
    if data.get("required", False):
        del data["required"]
        if model is not None:
            if model in required_fields:
                required_fields[model].append(field.name)
            else:
                required_fields[model] = [field.name]
    return data


@singledispatch
def _serialize_type(type_, model):
    if type_ == Any:
        return {"type": "object"}  # TODO is this the best way to deal with?
    elif type_.__origin__ == Union:
        if len(type_.__args__) == 2 and type(None) == type_.__args__[1]:
            output = _serialize_type(type_.__args__[0], model)
            output.update({"nullable": True})
            return output
        else:
            return {
                "oneOf": [
                    _serialize_type(arg, model) for arg in type_.__args__
                ]
            }


@_serialize_type.register(EnumMeta)  # for enums
@_generate_component
def _serialize_enum_meta(type_, model):
    choices = [e.value for e in type_]
    output = _serialize_type(type(choices[0]), model)
    output.update({"enum": choices})
    return output


@_serialize_type.register(GenericMeta)  # for typing generics
def _serialize_generic_meta(type_, model):
    if type_.__base__ in (List, Set, Sequence, Collection, Iterable):
        output = {"type": "array"}
        if len(type_.__args__):
            output.update(
                {"items": {**_serialize_type(type_.__args__[0], model)}}
            )
        return output
    elif type_.__base__ in (Dict, Mapping):
        output = {"type": "object"}
        if type_.__args__:
            output.update(
                {
                    "properties": {
                        "key": _serialize_type(type_.__args__[0], model),
                        "value": _serialize_type(type_.__args__[1], model),
                    }
                }
            )
        return output
    else:
        raise TypeError("This type is not supported")


def _serialize_model(type_, model):
    output = {
        "type": "object",
        "properties": {
            str(field.name): serialize(field, type_)
            for field in attr.fields(type_)
        },
    }
    if model is None and type_ in required_fields:
        output.update({"required": required_fields[type_]})
    return output


@_serialize_type.register(ModelMeta)  # for recursive types
@_generate_component
def _serialize_model_meta(type_, model):
    return _serialize_model(type_, model)


@_serialize_type.register(type)
def _serialize_type_type(type_, model):
    if type_ == int:
        return {"type": "integer", "format": "int64"}
    elif type_ == float:
        return {"type": "number", "format": "double"}
    elif type_ == str:
        return {"type": "string"}
    elif type_ == bool:
        return {"type": "boolean"}
    elif type_ == date:
        return {"type": "string", "format": "date"}
    elif type_ == datetime:
        return {"type": "string", "format": "date-time"}
    elif type_ == bytes:
        return {"type": "string", "format": "byte"}
    elif type_ in (list, set, tuple):
        _raise_simple_type(type_, Collection, Iterable, List, Sequence, Set)
    elif type_ == dict:
        _raise_simple_type(type_, Dict, Mapping)
    else:
        if attr.has(type_):  # for recursive types, just like ModelMeta
            return _generate_component(_serialize_model)(type_, model)
        raise TypeError("This type is not supported")
