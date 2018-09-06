import json

import attr
import pytest
from sanic import Sanic
from sanic.blueprints import Blueprint
from sanic.response import text
from sanic.views import HTTPMethodView
from sanic_swagger import (
    doc,
    openapi_blueprint
)


@pytest.fixture
def app():
    app = Sanic(__name__, strict_slashes=True)
    app.blueprint(openapi_blueprint)
    return app


def test_bare_app(app):
    request, response = app.test_client.get('/openapi/spec.json')
    response_schema = json.loads(response.body.decode())
    assert response_schema['paths'] == {}


def test_route_with_a_variable(app):
    request, response = app.test_client.get('/openapi/spec.json')
    response_schema = json.loads(response.body.decode())
    assert len(response_schema['paths']) == 0
    assert '/{variable}' not in response_schema['paths']

    @app.get('/<variable>')
    async def noop(req):
        pass

    request, response = app.test_client.get('/openapi/spec.json')
    response_schema = json.loads(response.body.decode())
    assert len(response_schema['paths']) == 1
    assert '/{variable}' in response_schema['paths']


def test_add_a_description(app):
    request, response = app.test_client.get('/openapi/spec.json')
    response_schema = json.loads(response.body.decode())
    assert response_schema['paths'] == {}

    @app.get('/')
    @doc.description('A short description')
    async def noop(req):
        pass

    request, response = app.test_client.get('/openapi/spec.json')
    response_schema = json.loads(response.body.decode())
    assert response_schema['paths']['/']['get']['description'] \
        == 'A short description'


def test_add_a_summary(app):
    request, response = app.test_client.get('/openapi/spec.json')
    response_schema = json.loads(response.body.decode())
    assert response_schema['paths'] == {}

    @app.get('/')
    @doc.summary('A short summary')
    async def noop(req):
        pass

    request, response = app.test_client.get('/openapi/spec.json')
    response_schema = json.loads(response.body.decode())
    assert response_schema['paths']['/']['get']['summary'] \
        == 'A short summary'


def test_add_empty_consumes_and_produces(app):
    request, response = app.test_client.get('/openapi/spec.json')
    response_schema = json.loads(response.body.decode())
    assert response_schema['definitions'] == {}

    @app.get('/')
    @doc.consumes()
    @doc.produces()
    async def noop(req):
        pass

    request, response = app.test_client.get('/openapi/spec.json')
    response_schema = json.loads(response.body.decode())
    assert response_schema['definitions'] == {}


def test_non_empty_consumes_and_produces(app):
    class Consumes(doc.Model):
        pass

    class Produces(doc.Model):
        pass

    request, response = app.test_client.get('/openapi/spec.json')
    response_schema = json.loads(response.body.decode())
    assert 'Consumes' not in response_schema['definitions']
    assert 'Produces' not in response_schema['definitions']

    @app.get('/')
    @doc.consumes(Consumes)
    @doc.produces(Produces)
    async def noop(req):
        pass

    request, response = app.test_client.get('/openapi/spec.json')
    response_schema = json.loads(response.body.decode())
    assert 'Consumes' in response_schema['definitions']
    assert 'Produces' in response_schema['definitions']


def test_add_response_codes(app):
    class RegularResponse(doc.Model):
        pass

    class ErrorResponse(doc.Model):
        pass

    request, response = app.test_client.get('/openapi/spec.json')
    response_schema = json.loads(response.body.decode())
    assert 'RegularResponse' not in response_schema['definitions']
    assert 'ErrorResponse' not in response_schema['definitions']

    @app.get('/')
    @doc.response('200', 'Pet data', model=RegularResponse)
    @doc.response('401', 'Un-authorized', model=ErrorResponse)
    async def noop(req):
        pass
    request, response = app.test_client.get('/openapi/spec.json')
    response_schema = json.loads(response.body.decode())

    request, response = app.test_client.get('/openapi/spec.json')
    response_schema = json.loads(response.body.decode())
    assert 'RegularResponse' in response_schema['definitions']
    assert 'ErrorResponse' in response_schema['definitions']
    expected = {
        '200': {
            'description': 'Pet data',
            'schema': {
                '$ref': '#/definitions/RegularResponse',
                'type': 'object'
                }
        },
        '401': {
            'description': 'Un-authorized',
            'schema': {
                '$ref': '#/definitions/ErrorResponse',
                'type': 'object'
                }
        }
    }
    assert response_schema['paths']['/']['get']['responses'] == expected


def test_add_tag(app):
    request, response = app.test_client.get('/openapi/spec.json')
    response_schema = json.loads(response.body.decode())
    assert response_schema['paths'] == {}
    assert response_schema['tags'] == []

    @app.get('/')
    @doc.tag('tag')
    async def noop(req):
        pass
    request, response = app.test_client.get('/openapi/spec.json')
    response_schema = json.loads(response.body.decode())
    assert response_schema['paths']['/']['get']['tags'] == ['tag']
    assert response_schema['tags'] == [{'name': 'tag'}]


def test_str_len_validators(app):
    request, response = app.test_client.get('/openapi/spec.json')
    response_schema = json.loads(response.body.decode())
    assert 'MinAndMax' not in response_schema['definitions']
    assert 'MinOrMax' not in response_schema['definitions']

    class MinAndMax(doc.Model):
        attr_with_min_max: str = attr.ib(metadata={
            'description': 'attribute with min and max metadata',
            'min_length': 12,
            'max_length': 36
        })

    class MinOrMax(doc.Model):
        attr_with_min: str = attr.ib(metadata={
            'description': 'attribute with min metadata',
            'min_length': 12
        })
        attr_with_max: str = attr.ib(metadata={
            'description': 'attribute with max metadata',
            'max_length': 12
        })

    @app.get('/')
    @doc.consumes(MinAndMax)
    @doc.produces(MinOrMax)
    async def noop(req):
        pass

    expected_min_and_max_definition = {
        'properties': {
            'attr_with_min_max': {
                'description': 'attribute with min and max metadata',
                'maxLength': 36,
                'minLength': 12,
                'type': 'string'
            }
        },
        'type': 'object'
    }

    expected_min_or_max_definition = {
        'properties': {
            'attr_with_max': {
                'description': 'attribute with max metadata',
                'maxLength': 12,
                'type': 'string'
            },
            'attr_with_min': {
                'description': 'attribute with min metadata',
                'minLength': 12,
                'type': 'string'
            }
        },
        'type': 'object'
    }
    expected_parameters = [
        {
            'format': None,
            'in': 'query',
            'name': 'body',
            'required': False,
            'schema': {
                '$ref': '#/definitions/MinAndMax'
            },
            'type': 'object'
        }
    ]
    expected_response_schema = {
        '$ref': '#/definitions/MinOrMax',
        'type': 'object'
    }

    request, response = app.test_client.get('/openapi/spec.json')
    response_schema = json.loads(response.body.decode())
    assert response_schema['definitions']['MinAndMax'] == \
        expected_min_and_max_definition
    assert response_schema['definitions']['MinOrMax'] == \
        expected_min_or_max_definition
    assert response_schema['paths']['/']['get']['parameters'] == \
        expected_parameters
    assert response_schema['paths']['/']['get']['responses']['200']['schema'] \
        == expected_response_schema


def test_exclude_endpoint(app):
    request, response = app.test_client.get('/openapi/spec.json')
    response_schema = json.loads(response.body.decode())
    assert response_schema['paths'] == {}

    @app.get('/')
    @doc.exclude(True)
    @doc.summary('Summary')
    async def noop(req):
        pass

    request, response = app.test_client.get('/openapi/spec.json')
    response_schema = json.loads(response.body.decode())
    assert response_schema['paths'] == {'/': {}}


def test_long_form_route_description_with_all_nones(app):
    request, response = app.test_client.get('/openapi/spec.json')
    response_schema = json.loads(response.body.decode())
    assert response_schema['paths'] == {}

    @app.get('/')
    @doc.route(None, None, None, None, None, None, None)
    async def noop(req):
        pass

    request, response = app.test_client.get('/openapi/spec.json')
    response_schema = json.loads(response.body.decode())
    expected = {
        '/': {
            'get': {
                'consumes': ['application/json'],
                'operationId': 'noop',
                'parameters': [],
                'produces': ['application/json'],
                'responses': {
                    '200': {'description': 'successful operation'}
                }
            }
        }
    }
    assert response_schema['paths'] == expected


def test_long_form_route_description_with_defaults(app):
    request, response = app.test_client.get('/openapi/spec.json')
    response_schema = json.loads(response.body.decode())
    assert response_schema['paths'] == {}

    @app.get('/')
    @doc.route('', '', [], [], '', '', False)
    async def noop(req):
        pass

    request, response = app.test_client.get('/openapi/spec.json')
    response_schema = json.loads(response.body.decode())
    expected = {
        '/': {
            'get': {
                'consumes': ['application/json'],
                'description': '',
                'summary': '',
                'operationId': 'noop',
                'parameters': [],
                'produces': ['application/json'],
                'responses': {
                    '200': {'description': 'successful operation'}
                }
            }
        }
    }
    assert response_schema['paths'] == expected


def test_class_based_routing(app):
    class SimpleView(HTTPMethodView):

        @doc.summary('Simple endpoint')
        def get(self, request):
            return text('worked')

    blueprint_with_route = Blueprint('withroute', url_prefix='withroute')
    blueprint_with_route.add_route(SimpleView.as_view(), '/')
    blueprint_with_no_routes = Blueprint('routeless', url_prefix='routeless')

    app.blueprint(blueprint_with_route)
    app.blueprint(blueprint_with_no_routes)

    _, response = app.test_client.get('/withroute/')
    assert response.status == 200
    _, response = app.test_client.get('/routeless/')
    assert response.status == 404
