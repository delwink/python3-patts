import re
from setuptools import setup

version = ''
with open('patts/__init__.py', 'r') as f:
    version = re.search(r'^__version__\s*=\s*[\'"]([^\'"]*)[\'"]',
                        f.read(), re.MULTILINE).group(1)

if not version:
    raise RuntimeError('Cannot find version information')

setup(
    name='patts',
    version=version,
    description='Python bindings for libpatts',
    author='David McMackins II',
    author_email='david@delwink.com',
    url='http://delwink.com/software/patts.html',
    packages=['patts'],
    package_data={'': ['COPYING']},
    package_dir={'patts': 'patts'},
    include_package_data=True,
    license='AGPLv3'
)
