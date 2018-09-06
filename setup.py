import os

from setuptools import setup

here = os.path.abspath(os.path.dirname(__file__))

about = {'version': '0.0.1'}

with open(
    os.path.join(here, 'sanic_swagger', '__init__.py'), 'r', encoding='utf-8'
) as f:
    for line in f:
        if line.startswith('__version__'):
            about['version'] = line.strip().split('=')[1].strip(' \'"')

with open(os.path.join(here, 'README.md'), 'r', encoding='utf-8') as f:
    README = f.read()


setup(
    name='sanic-swagger',
    version=about['version'],
    url='http://github.com/abatilo/sanic-swagger/',
    license='MIT',
    author='Aaron Batilo',
    author_email='aaronbatilo@gmail.com',
    maintainer='Aaron Batilo',
    maintainer_email='aaronbatilo@gmail.com',
    description='OpenAPI / Swagger support for Sanic using attrs',
    long_description=README,
    long_description_content_type='text/markdown',
    packages=['sanic_swagger'],
    package_data={'sanic_swagger': ['ui/*']},
    platforms='any',
    install_requires=[
        'sanic>=0.7.0',
        'attrs>=18.0.0',
    ],
    classifiers=[
        'Intended Audience :: Developers',
        'Development Status :: 4 - Beta',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Environment :: Web Environment',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ],
)
