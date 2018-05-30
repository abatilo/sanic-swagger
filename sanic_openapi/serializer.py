import inspect
from datetime import date, datetime
from enum import EnumMeta
from functools import singledispatch
from typing import Any, Dict, GenericMeta, List, Set, Union


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


def serialize_field(field):
    return {
        "name": field.name,
        "description": field.metadata.get("description", None),
        **serialize_type(field.type)
    }


@singledispatch
def serialize_type(v):
    res = {}
    if inspect.isclass(v.type) and type(v.type) == EnumMeta:
        res["enum"] = [str(e.value) for e in v.type]
    elif hasattr(v.type, "__base__"):
        if v.type.__base__ == List:
            res["type"] = "array"
            if len(v.type.__args__):
                res["items"] = serialize_type(v.type.__args__[0])
                # print("Argument: {!r}".format(v.type.__args__[0]))
        elif v.type.__base__ == Set:
            res["type"] = "array"
            if len(v.type.__args__):
                res["items"] = serialize_type(v.type.__args__[0])
                # print("Argument: {!r}".format(v.type.__args__[0]))
        elif v.type.__base__ == Dict:
            res["type"] = "object"
            if v.type.__args__:
                print("Key: {!r}".format(v.type.__args__[0]))
                print("Value: {!r}".format(v.type.__args__[1]))
    elif hasattr(v.type, "__origin__"):
        if v.type.__origin__ == Union:
            print("Base type: {!r}".format(v.type.__args__[0]))
            if type(None) == v.type.__args__[1]:
                print("Optional: yes")
            else:
                print("anyOf: - type ...")  # TODO does it includes null?
    elif v.type == Any:
        print("Any type - ")


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


# https://swagger.io/docs/specification/data-models/dictionaries/

# @serialize_type.register(dict)
# @serialize_type.register(Dict)
# def _serialize_dict(v):
#     return {
#         "type": "object",
#         "properties": {
#             key: serialize_schema(schema)
#             for key, schema in v.items()
#         }
#     }

@serialize_type.register(EnumMeta)
def _serialize_enum_meta(v):
    return {
        "type": "object",
        "properties": {
            key: serialize_schema(schema)
            for key, schema in v.items()
        }
    }


@serialize_type.register(GenericMeta)
def _serialize_generic_meta(v):
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


class JsonBody(Field):
    def __init__(self, fields=None, **kwargs):
        self.fields = fields or {}
        super().__init__(**kwargs, name="body")

    def serialize(self):
        return {
            "schema": {
                "type": "object",
                "properties": {key: serialize_schema(schema) for key, schema in self.fields.items()},
            },
            **super().serialize()
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


# import inspect
# from enum import Enum, IntEnum
# from typing import Dict, List, Optional, Set, Union, Any

# import attr

# metadata_aliases = ["description", "unique", "min_items", "max_items"]


# def field(*args, **kwargs):
#     for alias in metadata_aliases:
#         value = kwargs.pop(alias, None)
#         if value is not None:
#             if kwargs.get("metadata", None) is None:
#                 kwargs.update({"metadata": {alias: value}})
#             else:
#                 kwargs["metadata"].update({alias: value})
#     return attr.ib(*args, **kwargs)


# class _ModelMeta(type):

#     def __new__(mcls, name, bases, attrs):
#         return attr.s(super().__new__(mcls, name, bases, attrs))


# class Model(metaclass=_ModelMeta):
#     pass


# class PlatformEnum(str, Enum):
#     XBOX1 = "XBOX1"
#     PLAYSTATION4 = "PLAYSTATION4"
#     PC = "PC"


# class LanguageEnum(IntEnum):
#     ENGLISH = 1
#     JAPANESE = 2
#     SPANISH = 3
#     GERMAN = 4
#     PORTUGUESE = 5


# class Game(Model):
#     name: str = field(description="The name of the game")
#     platform: PlatformEnum = field(description="Which platform it runs on")
#     score: float = field(description="The average score of the game")
#     resolution_tested: str = field(description="The resolution which the game was tested")
#     genre: List[str] = field(description="One or more genres this game is part of")
#     rating: Dict[str, float] = field(description="Ratings given on each country")
#     screenshots: Set[bytes] = field(description="Screenshots of the game")
#     review_link: Optional[str] = field(description="The link of the game review (if exists)")
#     junk: Union[str, bytes] = field(description="This should not work")
#     more_junk: Any = field(description="The more junk field")
#     language: LanguageEnum = field(description="The language of the game.")


# def main():
#     for f in attr.fields(Game):
#         print("=====================")
#         print("Name: {}".format(f.name))
#         print("Description: {}".format(f.metadata.get('description')))
#         print("Type: {!r}".format(f.type))
#         print("Type of type: {!r}".format(type(f.type)))
#         if inspect.isclass(f.type) and issubclass(f.type, Enum):
#             print("Choices: {}".format(", ".join([str(e.value) for e in f.type])))
#         elif hasattr(f.type, "__base__"):
#             if f.type.__base__ == List:
#                 print("Base type: {!r}".format(f.type.__base__))
#                 if len(f.type.__args__):
#                     print("Argument: {!r}".format(f.type.__args__[0]))
#             elif f.type.__base__ == Set:
#                 print("Base type: {!r}".format(f.type.__base__))
#                 if len(f.type.__args__):
#                     print("Argument: {!r}".format(f.type.__args__[0]))
#             elif f.type.__base__ == Dict:
#                 print("Base type: {!r}".format(f.type.__base__))
#                 if f.type.__args__:
#                     print("Key: {!r}".format(f.type.__args__[0]))
#                     print("Value: {!r}".format(f.type.__args__[1]))
#         elif hasattr(f.type, "__origin__"):
#             if f.type.__origin__ == Union:
#                 print("Base type: {!r}".format(f.type.__args__[0]))
#                 if type(None) == f.type.__args__[1]:
#                     print("Optional: yes")
#                 else:
#                     print(">> THIS TYPE IS NOT ALLOWED!")
#         elif f.type == Any:
#             print(">> THIS TYPE IS NOT ALLOWED!")

#         print("")
#         if f.name == "xxx":
#             from IPython import embed
#             embed()


# if __name__ == '__main__':
#     main()
