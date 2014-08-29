#! /usr/bin/env python

from setuptools import setup

setup(name='sagefs',
      version='1.0',
      description='Sage Filesystem and stuff',
      author='Stephen Tredger',
      packages=['sagefs', 'geniauth'],
      entry_points={
        'paste.filter_factory': [
            'geniauthmiddleware = geniauth.swiftmiddleware:filter_factory'
        ]
      },
      install_requires=[
        'requests',
        'BeautifulSoup',
        'pymongo',
        'python-swiftclient==1.4.0'
      ]
     )