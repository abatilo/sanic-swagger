from datetime import date, datetime
from functools import singledispatch
from typing import Dict, List


definitions = {}


class Field:

    def __init__(
        self, description=None, required=None, name=None, choices=None
    ):
        self.name = name
        self.description = description
        self.required = required
        self.choices = choices

    def serialize(self):
        output = {}
        if self.name:
            output["name"] = self.name
        if self.description:
            output["description"] = self.description
        if self.required is not None:
            output["required"] = self.required
        if self.choices is not None:
            output["enum"] = self.choices
        return output


@singledispatch
def serialize_type(v):
    # TODO check if obj is attribute from attrs
    pass


@serialize_type.register(int)
def _serialize_int(v):
    return {"type": "integer", "format": "int64"}


@serialize_type.register(float)
def _serialize_float(v):
    return {"type": "number", "format": "double"}


@serialize_type.register(str)
def _serialize_str(v):
    return {"type": "string"}


@serialize_type.register(bool)
def _serialize_bool(v):
    return {"type": "boolean"}


@serialize_type.register(date)
def _serialize_date(v):
    return {"type": "string", "format": "date"}


@serialize_type.register(datetime)
def _serialize_datetime(v):
    return {"type": "string", "format": "date-time"}


@serialize_type.register(dict)
@serialize_type.register(Dict)
def _serialize_dict(v):
    return {
        "type": "object",
        "properties": {
            key: serialize_schema(schema)
            for key, schema in v.items()
        }
    }


@serialize_type.register(list)
def _serialize_list(v):
    pass  # TODO choices, like enum?


@serialize_type.register(List)
def _serialize_typing_list(v, items):
    # if len(self.items) > 1:
    #     items = Tuple(self.items).serialize()
    # elif self.items:
    #     items = serialize_schema(self.items[0])
    # return {"type": "array", "items": items}
    pass  # TODO list of what?


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
        elif schema_type is list:
            return List(schema).serialize()

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
