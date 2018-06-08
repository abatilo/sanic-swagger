import attr

from sanic.response import HTTPResponse, json_dumps


def model(
    body,
    status=200,
    headers=None,
    content_type="application/json",
    dumps=json_dumps,
    **kwargs
):

    if not attr.has(body):
        raise TypeError(
            "The body (object) sent to `response.model` should be an instance "
            "of `doc.Model` or `@attr.s` decorated class"
        )
    return HTTPResponse(
        dumps(attr.asdict(body), **kwargs),
        headers=headers,
        status=status,
        content_type=content_type,
    )
