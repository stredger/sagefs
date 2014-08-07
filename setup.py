#! /usr/bin/env python

from setuptools import setup

setup(name='sagefs',
      version='1.0',
      description='Sage Filesystem and stuff',
      author='Stephen Tredger',
      packages=['sagefs', 'geeauth'],
      entry_points={
        'paste.filter_factory': [
            'geeauthmiddleware = geeauth.swiftmiddleware:filter_factory'
        ]
      }
     )