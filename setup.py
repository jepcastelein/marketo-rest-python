import os
import sys

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

# Don't import analytics-python module here, since deps may not be installed
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'pymarketo'))

long_description = '''
python_marketo is a python query client that wraps the Marketo Rest API.
For sending data to Marketo,
'''

setup(
    name='pythonmarketo',
    version= '0.0.6',
    url='https://github.com/asamat/python_marketo',
    author='Arunim Samat',
    author_email='arunimsamat@gmail.com',
    packages=['pythonmarketo', 'pythonmarketo.helper'],
    license='MIT License',
    install_requires=[
        'requests',
    ],
    description='Wrapper to Marketo Rest API.',
    long_description=long_description
)