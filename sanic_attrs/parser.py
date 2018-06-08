import attr

from sanic.blueprints import Blueprint

from .doc import route_specs


blueprint = Blueprint("attrs_parser", url_prefix="parser")


@blueprint.middleware("request")
async def parse_middleware(request):
    if (
        not request.method == "GET"
        and request.headers.get("content-type", None) == "application/json"
        and request.json is not None
    ):
        route = request.app.router.get(
            request
        )  # TODO: is there a way to avoid calling the router TWICE?
        if len(route) and route[0] in route_specs:
            spec = route_specs[route[0]]
            if len(spec.consumes) and attr.has(spec.consumes[0].field):
                spec_cls = spec.consumes[0].field
                request["input_obj"] = spec_cls(**request.json)
