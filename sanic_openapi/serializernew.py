from datetime import date, datetime
from enum import EnumMeta
from functools import singledispatch
from typing import Any, Dict, GenericMeta, List, Set, Union

import attr

from .doc import ModelMeta


definitions = {}
components = {}


def serialize(f):
    if hasattr(f, "type"):
        return {
            "description": f.metadata.get("description", None),
            **_serialize_type(f.type),
        }
    else:
        return _serialize_type(f)


@singledispatch
def _serialize_type(v):
    if v == Any:
        return {"type": "object"}  # TODO is this the best way to deal with?
    elif v.__origin__ == Union:
        if len(v.__args__) == 2 and type(None) == v.__args__[1]:
            output = _serialize_type(v.__args__[0])
            output.update({"nullable": True})
            return output
        else:
            return {"oneOf": [_serialize_type(arg) for arg in v.__args__]}


@_serialize_type.register(EnumMeta)  # for enums
def _serialize_enum_meta(v):
    choices = [e.value for e in v]
    output = _serialize_type(type(choices[0]))
    output.update({"enum": choices})
    return output


@_serialize_type.register(GenericMeta)  # for typing generics
def _serialize_generic_meta(v):
    if v.__base__ == List or v.__base__ == Set:
        output = {"type": "array"}
        if len(v.__args__):
            output.update({"items": {**_serialize_type(v.__args__[0])}})
        return output
    elif v.__base__ == Dict:
        output = {"type": "object"}
        if v.__args__:
            output.update(
                {
                    "properties": {
                        "key": _serialize_type(v.__args__[0]),
                        "value": _serialize_type(v.__args__[1]),
                    }
                }
            )
        return output
    else:
        raise TypeError("This type is not supported")


def _serialize_model(v):
    return {
        "type": "object",
        "properties": {str(f.name): serialize(f) for f in attr.fields(v)},
    }


@_serialize_type.register(ModelMeta)  # for recursive types
def _serialize_model_meta(v):
    return _serialize_model(v)


@_serialize_type.register(type)
def _serialize_type_type(v):
    if v == int:
        return {"type": "integer", "format": "int64"}
    elif v == float:
        return {"type": "number", "format": "double"}
    elif v == str:
        return {"type": "string"}
    elif v == bool:
        return {"type": "boolean"}
    elif v == date:
        return {"type": "string", "format": "date"}
    elif v == datetime:
        return {"type": "string", "format": "date-time"}
    elif v == bytes:
        return {"type": "string", "format": "byte"}
    else:
        if attr.has(v):
            return _serialize_model(v)
        raise TypeError("This type is not supported")
