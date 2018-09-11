# sanic-swagger

[![Codacy Badge](https://api.codacy.com/project/badge/Grade/8e7b064677ab4b6cbc2508b626bcba0a)](https://app.codacy.com/app/abatilo/sanic-swagger?utm_source=github.com&utm_medium=referral&utm_content=abatilo/sanic-swagger&utm_campaign=Badge_Grade_Settings)
[![CircleCI](https://circleci.com/gh/abatilo/sanic-swagger.svg?style=svg)](https://circleci.com/gh/abatilo/sanic-swagger)
[![codecov](https://codecov.io/gh/abatilo/sanic-swagger/branch/master/graph/badge.svg)](https://codecov.io/gh/abatilo/sanic-swagger)
[![PyPI status](https://img.shields.io/pypi/status/sanic-swagger.svg)](https://pypi.python.org/pypi/sanic-swagger/)
[![PyPI version](https://badge.fury.io/py/sanic-swagger.svg)](https://badge.fury.io/py/sanic-swagger)
[![PyPI pyversions](https://img.shields.io/pypi/pyversions/sanic-swagger.svg)](https://pypi.python.org/pypi/sanic-swagger/)
[![FOSSA Status](https://app.fossa.io/api/projects/git%2Bgithub.com%2Fabatilo%2Fsanic-swagger.svg?type=shield)](https://app.fossa.io/projects/git%2Bgithub.com%2Fabatilo%2Fsanic-swagger?ref=badge_shield)

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


## License
[![FOSSA Status](https://app.fossa.io/api/projects/git%2Bgithub.com%2Fabatilo%2Fsanic-swagger.svg?type=large)](https://app.fossa.io/projects/git%2Bgithub.com%2Fabatilo%2Fsanic-swagger?ref=badge_large)