import codecs
import os
import re
from setuptools import setup


with codecs.open(os.path.join(os.path.abspath(os.path.dirname(
        __file__)), 'sanic_attrs', '__init__.py'), 'r', 'latin1') as fp:
    try:
        version = re.findall(r"^__version__ = '([^']+)'\r?$",
                             fp.read(), re.M)[0]
    except IndexError:
        raise RuntimeError('Unable to determine version.')

setup(
    name='sanic-attrs',
    version=version,
    url='http://github.com/vltr/sanic-attrs/',
    license='MIT',
    author='Channel Cat',
    author_email='channelcat@gmail.com',
    maintainer='Richard Kuesters',
    maintainer_email="rkuesters@gmail.com",
    description='OpenAPI / Swagger support for Sanic using attrs',
    packages=['sanic_attrs'],
    package_data={'sanic_attrs': ['ui/*']},
    platforms='any',
    install_requires=[
        'sanic>=0.7.0',
        'attrs>=18.0.0',
    ],
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Environment :: Web Environment',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ],
)
