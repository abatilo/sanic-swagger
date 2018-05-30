from collections import defaultdict

import attr

from .serializer import RouteSpec, RouteField


metadata_aliases = ["description", "unique", "min_items", "max_items"]


def field(*args, **kwargs):
    for alias in metadata_aliases:
        value = kwargs.pop(alias, None)
        if value is not None:
            if kwargs.get("metadata", None) is None:
                kwargs.update({"metadata": {alias: value}})
            else:
                kwargs["metadata"].update({alias: value})
    return attr.ib(*args, **kwargs)


class _ModelMeta(type):

    def __new__(mcls, name, bases, attrs):
        return attr.s(super().__new__(mcls, name, bases, attrs))


class Model(metaclass=_ModelMeta):
    pass


definitions = {}
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


def consumes(*args, content_type=None, location="query", required=False):

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
            "description": description,
            "example": examples,
            "model": model,
        }
        return func

    return inner
