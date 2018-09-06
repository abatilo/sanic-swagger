from collections import defaultdict
from enum import EnumMeta
from functools import partial, singledispatch

import attr

from .options import metadata_aliases
from .validators import max_str_len, min_max_str_len, min_str_len


def field(*args, **kwargs):
    for alias_group in metadata_aliases.values():
        for alias in alias_group:
            value = kwargs.pop(alias, None)
            if value is not None:
                if kwargs.get('metadata', None) is None:
                    kwargs.update({'metadata': {alias: value}})
                else:
                    kwargs['metadata'].update({alias: value})
    return attr.ib(*args, **kwargs)


class ModelMeta(type):

    def __new__(cls, name, bases, attrs):
        if bases:
            for k, f in attrs.items():
                annotations = attrs.get('__annotations__', {})
                _implement_converter(f, k, annotations)
                _implement_validators(f, k, annotations)
        return attr.s(super().__new__(cls, name, bases, attrs))


def _implement_converter(field, key, annotations):
    if hasattr(field, 'type') and field.type:
        _converter(field.type, field)
    elif key in annotations:
        _converter(annotations.get(key), field)


@singledispatch
def _converter(type_, field):
    if attr.has(type_):
        field.converter = attr.converters.optional(
            partial(_model_converter, type_)
        )


@_converter.register(EnumMeta)
def _converter_enum(type_, field):
    field.converter = attr.converters.optional(type_)


def _model_converter(model_cls, value):
    if isinstance(value, model_cls):
        return value
    return model_cls(**value)


@_converter.register(ModelMeta)
def _converter_model_meta(type_, field):
    field.converter = attr.converters.optional(
        partial(_model_converter, type_)
    )


def _implement_validators(field, key, annotations):
    if hasattr(field, 'type') and field.type:
        _implement_validator(field.type, field)
    elif key in annotations:
        _implement_validator(annotations.get(key), field)


@singledispatch
def _implement_validator(type_, field):
    if type_ == str:
        validator = None
        if (
            'min_length' in field.metadata
            and 'max_length' not in field.metadata
        ):
            validator = min_str_len
        elif (
            'max_length' in field.metadata
            and 'min_length' not in field.metadata
        ):
            validator = max_str_len
        elif 'min_length' in field.metadata and 'max_length' in field.metadata:
            validator = min_max_str_len
        if validator is not None:
            field.validator(validator)
        # TODO implement patterns
        # TODO implement format
    # TODO number
    #   (minimum, maximum, exclusive_minimum, exclusive_maximum, multiple_of)
    # TODO array (one_of, min_items, max_items, unique_items)
    # TODO object (min_properties, max_properties)


class Model(metaclass=ModelMeta):
    pass


# --------------------------------------------------------------- #
# Route Documenters
# --------------------------------------------------------------- #


class RouteSpec:
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


class RouteField:
    field = None
    location = None
    required = None

    def __init__(self, field, location=None, required=False):
        self.field = field
        self.location = location
        self.required = required


route_specs = defaultdict(RouteSpec)


def route(
    summary=None,
    description=None,
    consumes=None,
    produces=None,
    consumes_content_type=None,
    produces_content_type=None,
    exclude=None,
):
    def inner(func):
        route_spec = route_specs[func]

        if summary is not None:
            route_spec.summary = summary
        if description is not None:
            route_spec.description = description
        if consumes is not None:
            route_spec.consumes = consumes
        if produces is not None:
            route_spec.produces = produces
        if consumes_content_type is not None:
            route_spec.consumes_content_type = consumes_content_type
        if produces_content_type is not None:
            route_spec.produces_content_type = produces_content_type
        if exclude is not None:
            route_spec.exclude = exclude

        return func

    return inner


def exclude(boolean):
    def inner(func):
        route_specs[func].exclude = boolean
        return func

    return inner


def summary(text):
    def inner(func):
        route_specs[func].summary = text
        return func

    return inner


def description(text):
    def inner(func):
        route_specs[func].description = text
        return func

    return inner


def consumes(*args, content_type=None, location='query', required=False):
    def inner(func):
        if args:
            for arg in args:
                field = RouteField(arg, location, required)
                route_specs[func].consumes.append(field)
                route_specs[func].consumes_content_type = content_type
        return func

    return inner


def produces(*args, content_type=None):
    def inner(func):
        if args:
            field = RouteField(args[0])
            route_specs[func].produces = field
            route_specs[func].produces_content_type = content_type
        return func

    return inner


def tag(name):
    def inner(func):
        route_specs[func].tags.append(name)
        return func

    return inner


def response(code, description=None, examples=None, model=None):
    def inner(func):
        route_specs[func].responses[code] = {
            'description': description,
            'example': examples,
            'model': model,
        }
        return func

    return inner
