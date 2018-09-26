#!/usr/bin/env python
# coding: utf-8

import os
import re

from numpy.distutils.core import Extension, setup

#######################
#  Fortran extension  #
#######################

NemohCore = Extension(
    name="capytaine.NemohCore",
    sources=[
        "capytaine/NemohCore/constants.f90",
        "capytaine/NemohCore/Green_Rankine.f90",
        "capytaine/NemohCore/Initialize_Green_wave.f90",
        "capytaine/NemohCore/Green_wave.f90",
        "capytaine/NemohCore/old_Prony_decomposition.f90",
    ],
    extra_compile_args=['-O2', '-fopenmp'],
    extra_link_args=['-fopenmp'],
    # # Uncomment the following lines to get more verbose output from f2py.
    # define_macros=[
    #     ('F2PY_REPORT_ATEXIT', 1),
    #     ('F2PY_REPORT_ON_ARRAY_COPY', 1),
    # ],
)

#########################
#  Read version number  #
#########################

here = os.path.abspath(os.path.dirname(__file__))

def read(*parts):
    with open(os.path.join(here, *parts), 'r') as fp:
        return fp.read()

def find_version(*file_paths):
    version_file = read(*file_paths)
    version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]",
                              version_file, re.M)
    if version_match:
        return version_match.group(1)
    raise RuntimeError("Unable to find version string.")


if __name__ == "__main__":

    ##########
    #  Main  #
    ##########

    setup(name='capytaine',
          version=find_version('capytaine', '__init__.py'),
          description='Python-based distribution of Nemoh',
          url='http://github.com/mancellin/capytaine',
          author='Matthieu Ancellin',
          author_email='matthieu.ancellin@ucd.ie',
          license='GPLv3',
          packages=[
              'capytaine',
              'capytaine.mesh',
              'capytaine.geometric_bodies',
              'capytaine.tools',
              'capytaine.ui',
              'capytaine.ui.vtk',
              'capytaine.io',
          ],
          install_requires=[
              'attrs',
              'numpy',
              'scipy',
              'pandas',
              'xarray',
              'matplotlib',
              'vtk',
          ],
          entry_points={
              'console_scripts': [
                  'capytaine=capytaine.ui.cli:main',
              ],
          },
          ext_modules=[NemohCore],
          )
