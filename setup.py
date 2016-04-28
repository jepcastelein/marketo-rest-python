import os
import sys

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

# Don't import analytics-python module here, since deps may not be installed
# sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'pymarketo'))

long_description = '''
Marketo Python REST is a Python client that wraps the Marketo Rest API.
Originally developed by asamat with contributions from sandipsinha
'''

setup(
    name='marketorestpython',
    version= '0.2.2',
    url='https://github.com/jepcastelein/marketo-rest-python',
    author='Jep Castelein',
    author_email='jep@castelein.net',
    packages=['marketorestpython', 'marketorestpython.helper'],
    license='MIT License',
    install_requires=[
        'requests',
    ],
    keywords = ['Marketo', 'REST API', 'Wrapper', 'Client'],
    description='Python Client for the Marketo REST API',
    long_description=long_description
)
