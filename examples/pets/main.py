import cattr
from sanic import Sanic
from sanic.response import json
from sanic_swagger import (
    doc,
    openapi_blueprint,
    swagger_blueprint
)

app = Sanic(__name__, strict_slashes=True)

app.blueprint(openapi_blueprint)
app.blueprint(swagger_blueprint)


class Pet(doc.Model):
    name: str = doc.field(description='Name of the pet')
    age: int = doc.field(description='How old is the pet')


@app.get('/')
@doc.summary('List pets')
@doc.produces(Pet)
async def root(req):
    pet = Pet('Chopper', 3)
    return json(cattr.unstructure(pet))


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
