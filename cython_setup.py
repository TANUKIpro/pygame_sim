from distutils.core import setup, Extension
from Cython.Build import cythonize
from numpy import get_include # cimport numpy を使うため

ext = Extension("const_update", sources=["const_update.pyx"], include_dirs=['.', get_include()])
setup(name="const_update", ext_modules=cythonize([ext]))
