# sanic-swagger

[![CircleCI](https://circleci.com/gh/abatilo/sanic-swagger.svg?style=svg)](https://circleci.com/gh/abatilo/sanic-swagger)
[![codecov](https://codecov.io/gh/abatilo/sanic-swagger/branch/master/graph/badge.svg)](https://codecov.io/gh/abatilo/sanic-swagger)

Annotate your [Sanic](https://github.com/channelcat/sanic) endpoints, and
automatically generate a
[Swagger](https://swagger.io/)/[OpenAPI](https://swagger.io/resources/open-api/)
compatible JSON spec file.

This project is a fork of both
[sanic-openapi](https://github.com/channelcat/sanic-openapi) and
[sanic-attrs](https://github.com/vltr/sanic-attrs).

As such, you can write all of your models as
[attrs](https://github.com/python-attrs/attrs) which gives you the handy
ability to use [cattrs](https://github.com/Tinche/cattrs) for dealing with your
serialization and deserialization of your models to and from JSON.
