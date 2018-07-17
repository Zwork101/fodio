from setuptools import setup

import sys

if sys.argv[1] == 'sdist':
    with open('./README.rst') as file:
        README = file.read()
else:
    README = ""

setup(
    name='fodio',
    version='1.0.1',
    packages=['fodio', 'demos'],
    url='https://github.com/Zwork101/fodio',
    license='Apache2',
    author='Nathan Zilora',
    author_email='zwork101@gmail.com',
    description='A scraping library made to be simple and asynchronous',
    install_requires=['aiohttp', 'pyquery'],
    long_description=README
)
