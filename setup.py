from __future__ import absolute_import
from setuptools import setup, find_packages


setup(
    name='webfriend-images',
    description='An Webfriend extension providing support for working with graphical data.',
    version='0.0.1',
    author='Gary Hetzel',
    author_email='garyhetzel@gmail.com',
    url='https://github.com/ghetzel/webfriend-images',
    install_requires=[
        'pyocr',
        'unidecode',
        'webfriend',
    ],
    packages=find_packages(exclude=['*.tests']),
    classifiers=[],
)
