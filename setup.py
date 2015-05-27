#!/usr/bin/env python
# coding: utf-8

from setuptools import setup

setup(name='marionette_testsuite',
      test_suite='marionette_testsuite',
      packages=['marionette_testsuite',
                'marionette_testsuite.http'],
      version='0.0.1',
      description='Marionette Test Suite',
      author='Kevin P. Dyer',
      author_email='kpdyer@gmail.com',
      url='https://github.com/kpdyer/marionette_testsuite')
