import os
from setuptools import setup
from setuptools import Extension
from Cython.Distutils import build_ext

ext_modules=[
    Extension("_compat", ["_compat.py"]),
    Extension("core", ["core.py"]),
    Extension("events", ["events.py"]),
    Extension("rt", ["rt.py"]),
    Extension("util", ["util.py"]),
    Extension("resources.base", ["resources/base.py"]),
    Extension("resources.container", ["resources/container.py"]),
    Extension("resources.resource", ["resources/resource.py"]),
    Extension("resources.store", ["resources/store.py"])
]

setup(
    cmdclass = {'build_ext': build_ext},
    ext_modules = ext_modules
)
