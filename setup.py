# -*- coding: utf-8 -*-

from setuptools import setup

setup(name='desc-pro',
      version='1.8.2',
      description='Discrete event simulation for solar cell production using python module simpy',
      url='https://github.com/slierp/Discrete-event-simulation-for-solar-cell-production',
      author='Ronald Naber',
      license='Public domain',
      packages=['desc-pro','desc-pro/batchlocations','desc-pro/dialogs'],
      zip_safe=False,
      classifiers=[
      'Development Status :: 5 - Production/Stable',
      'Environment :: Win32 (MS Windows)',
      'Environment :: X11 Applications',
      'Environment :: X11 Applications :: Qt',
      'Operating System :: OS Independent',
      'Intended Audience :: End Users/Desktop',
      'Intended Audience :: Science/Research',
      'Programming Language :: Python',
      'Topic :: Scientific/Engineering'])

