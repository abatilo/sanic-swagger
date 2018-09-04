import re
from itertools import repeat

from sanic.blueprints import Blueprint
from sanic.constants import HTTP_METHODS
from sanic.response import json
from sanic.views import CompositionView

from .doc import RouteSpec, route_specs
from .serializer import object_definitions, serialize

blueprint = Blueprint('openapi', url_prefix='openapi')

_spec = {}


# Removes all null values from a dictionary
def remove_nulls(dictionary, deep=True):
    return {
        k: remove_nulls(v, deep) if deep and type(v) is dict else v
        for k, v in dictionary.items()
        if v is not None
    }


@blueprint.listener('before_server_start')
def build_spec(app, loop):
    _spec['swagger'] = '2.0'
    _spec['info'] = {
        'version': getattr(app.config, 'API_VERSION', '1.0.0'),
        'title': getattr(app.config, 'API_TITLE', 'API'),
        'description': getattr(app.config, 'API_DESCRIPTION', ''),
        'termsOfService': getattr(app.config, 'API_TERMS_OF_SERVICE', None),
        'contact': {'email': getattr(app.config, 'API_CONTACT_EMAIL', None)},
        'license': {
            'name': getattr(app.config, 'API_LICENSE_NAME', None),
            'url': getattr(app.config, 'API_LICENSE_URL', None),
        },
    }
    _spec['schemes'] = getattr(app.config, 'API_SCHEMES', ['http'])

    host = getattr(app.config, 'API_HOST', None)
    if host is not None:
        _spec['host'] = host

    base_path = getattr(app.config, 'API_BASEPATH', None)
    if base_path is not None:
        _spec['basePath'] = base_path

    # --------------------------------------------------------------- #
    # Authorization
    # --------------------------------------------------------------- #

    _spec['securityDefinitions'] = getattr(
        app.config, 'API_SECURITY_DEFINITIONS', None
    )
    _spec['security'] = getattr(app.config, 'API_SECURITY', None)

    # --------------------------------------------------------------- #
    # Blueprint Tags
    # --------------------------------------------------------------- #

    for blueprint in app.blueprints.values():
        if hasattr(blueprint, 'routes'):
            for route in blueprint.routes:
                if hasattr(route.handler, 'view_class'):
                    # class based view
                    view = route.handler.view_class
                    for http_method in HTTP_METHODS:
                        _handler = getattr(view, http_method.lower(), None)
                        if _handler:
                            route_spec = route_specs[_handler]
                            route_spec.blueprint = blueprint
                            if not route_spec.tags:
                                route_spec.tags.append(blueprint.name)
                else:
                    route_spec = route_specs[route.handler]
                    route_spec.blueprint = blueprint
                    if not route_spec.tags:
                        route_spec.tags.append(blueprint.name)

    paths = {}
    for uri, route in app.router.routes_all.items():
        if (
            uri.startswith('/swagger')
            or uri.startswith('/openapi')
            or '<file_uri' in uri
        ):
            # TODO: add static flag in sanic routes
            continue

        # --------------------------------------------------------------- #
        # Methods
        # --------------------------------------------------------------- #

        # Build list of methods and their handler functions
        handler_type = type(route.handler)
        if handler_type is CompositionView:
            view = route.handler
            method_handlers = view.handlers.items()
        else:
            method_handlers = zip(route.methods, repeat(route.handler))

        methods = {}
        for _method, _handler in method_handlers:
            # route_spec = route_specs.get(_handler) or RouteSpec()
            if hasattr(_handler, 'view_class'):
                view_handler = getattr(_handler.view_class, _method.lower())
                route_spec = route_specs.get(view_handler) or RouteSpec()
            else:
                route_spec = route_specs.get(_handler) or RouteSpec()

            if _method == 'OPTIONS' or route_spec.exclude:
                continue

            consumes_content_types = (
                route_spec.consumes_content_type
                or getattr(
                    app.config,
                    'API_CONSUMES_CONTENT_TYPES',
                    ['application/json'],
                )
            )
            produces_content_types = (
                route_spec.produces_content_type
                or getattr(
                    app.config,
                    'API_PRODUCES_CONTENT_TYPES',
                    ['application/json'],
                )
            )

            # Parameters - Path & Query String
            route_parameters = []
            for parameter in route.parameters:
                route_parameters.append(
                    {
                        **serialize(parameter.cast),
                        'required': True,
                        'in': 'path',
                        'name': parameter.name,
                    }
                )

            for consumer in route_spec.consumes:
                spec = serialize(consumer.field)
                if 'properties' in spec:
                    for name, prop_spec in spec['properties'].items():
                        route_param = {
                            **prop_spec,
                            'required': consumer.required,
                            'in': consumer.location,
                            'name': name,
                        }
                else:
                    route_param = {
                        **spec,
                        'required': consumer.required,
                        'in': consumer.location,
                        'name': consumer.field.name
                        if hasattr(consumer.field, 'name')
                        else 'body',
                    }

                if '$ref' in route_param:
                    route_param['schema'] = {'$ref': route_param['$ref']}
                    del route_param['$ref']

                route_parameters.append(route_param)

            if '200' not in route_spec.responses:
                route_spec.responses['200'] = {
                    'description': 'successful operation',
                    'example': None,
                    'schema': serialize(route_spec.produces.field)
                    if route_spec.produces
                    else None,
                }

            for k, v in route_spec.responses.items():
                if v.get('model', None) is not None:
                    schema = serialize(v.get('model'))
                    route_spec.responses[k]['schema'] = schema
                    del route_spec.responses[k]['model']

            endpoint = remove_nulls(
                {
                    'operationId': route_spec.operation or route.name,
                    'summary': route_spec.summary,
                    'description': route_spec.description,
                    'consumes': consumes_content_types,
                    'produces': produces_content_types,
                    'tags': route_spec.tags or None,
                    'parameters': route_parameters,
                    'responses': route_spec.responses,
                }
            )

            methods[_method.lower()] = endpoint

        uri_parsed = uri
        for parameter in route.parameters:
            uri_parsed = re.sub(
                '<' + parameter.name + '.*?>',
                '{' + parameter.name + '}',
                uri_parsed,
            )

        paths[uri_parsed] = methods

    # --------------------------------------------------------------- #
    # Definitions
    # --------------------------------------------------------------- #

    _spec['definitions'] = {}
    _spec['definitions'].update(
        {
            str(key.__name__): definition
            for key, definition in object_definitions.items()
        }
    )

    # --------------------------------------------------------------- #
    # Tags
    # --------------------------------------------------------------- #

    # TODO: figure out how to get descriptions in these
    tags = {}
    for route_spec in route_specs.values():
        if route_spec.blueprint and route_spec.blueprint.name in (
            'swagger',
            'openapi',
        ):
            # TODO: add static flag in sanic routes
            continue
        for tag in route_spec.tags:
            tags[tag] = True
    _spec['tags'] = [{'name': name} for name in tags.keys()]

    _spec['paths'] = paths


@blueprint.route('/spec.json')
def spec(request):
    return json(_spec)
