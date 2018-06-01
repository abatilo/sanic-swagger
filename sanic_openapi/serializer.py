# import inspect

# from datetime import date, datetime
# from enum import EnumMeta
# from functools import singledispatch
# from typing import Any, Dict, GenericMeta, List, Set, Union

Field = object


definitions = {}


class JsonBody(Field):
    def __init__(self, fields=None, **kwargs):
        self.fields = fields or {}
        super().__init__(**kwargs, name="body")

    def serialize(self):
        return {
            "schema": {
                "type": "object",
                "properties": {
                    key: serialize_schema(schema)
                    for key, schema in self.fields.items()
                },
            },
            **super().serialize(),
        }


class Object(Field):
    def __init__(self, cls, *args, object_name=None, **kwargs):
        super().__init__(*args, **kwargs)

        self.cls = cls
        self.object_name = object_name or cls.__name__

        if self.cls not in definitions:
            definitions[self.cls] = (self, self.definition)

    @property
    def definition(self):
        return {
            "type": "object",
            "properties": {
                key: serialize_schema(schema)
                for key, schema in self.cls.__dict__.items()
                if not key.startswith("_")
            },
            **super().serialize(),
        }

    def serialize(self):
        return {
            "type": "object",
            "$ref": "#/definitions/{}".format(self.object_name),
            **super().serialize(),
        }


def serialize_schema(schema):
    schema_type = type(schema)

    # --------------------------------------------------------------- #
    # Class
    # --------------------------------------------------------------- #
    if schema_type is type:
        if issubclass(schema, Field):
            return schema().serialize()
        # elif schema is dict:
        #     return Dictionary().serialize()
        # elif schema is list:
        #     return List().serialize()
        # elif schema is int:
        #     return Integer().serialize()
        # elif schema is float:
        #     return Float().serialize()
        # elif schema is str:
        #     return String().serialize()
        # elif schema is bool:
        #     return Boolean().serialize()
        # elif schema is date:
        #     return Date().serialize()
        # elif schema is datetime:
        #     return DateTime().serialize()
        else:
            return Object(schema).serialize()

    # --------------------------------------------------------------- #
    # Object
    # --------------------------------------------------------------- #
    else:
        if issubclass(schema_type, Field):
            return schema.serialize()
        # elif schema_type is dict:
        #     return Dictionary(schema).serialize()
        # elif schema_type is list:
        #     return List(schema).serialize()

    return {}


# --------------------------------------------------------------- #
# Route Documenters
# --------------------------------------------------------------- #


class RouteSpec(object):
    consumes = None
    consumes_content_type = None
    produces = None
    produces_content_type = None
    summary = None
    description = None
    operation = None
    blueprint = None
    tags = None
    exclude = None
    responses = None

    def __init__(self):
        self.tags = []
        self.consumes = []
        self.responses = {}
        super().__init__()


class RouteField(object):
    field = None
    location = None
    required = None

    def __init__(self, field, location=None, required=False):
        self.field = field
        self.location = location
        self.required = required
