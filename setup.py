"""
Flask-Tinyclients
=================

Tiny clients for REST services.
"""
import os
import re
from setuptools import setup, find_packages


def fpath(name):
    return os.path.join(os.path.dirname(__file__), name)


def read(fname):
    return open(fpath(fname)).read()

init_str = read(fpath('flask_tinyclients/__init__.py'))


def grep(attr, file=None):
    if file is None:
        file = init_str
    pattern = r"{0}\W*=\W*'([^']+)'".format(attr)
    strval, = re.findall(pattern, file)
    return strval


setup(
    name='Flask-Tinyclients',
    version=grep('__version__'),
    url='https://github.com/certeu/Flask-Tinyclients',
    license='MIT',
    author='Alexandru Ciobanu',
    author_email='alex@cert.europa.eu',
    description='Tiny clients for REST services',
    long_description=__doc__,
    zip_safe=False,
    packages=find_packages(exclude=['tests']),
    platforms='any',
    install_requires=[
        'Flask>=0.9',
        'requests'
    ],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ]
)
