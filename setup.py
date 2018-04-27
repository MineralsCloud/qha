#!/usr/bin/env python3

from distutils.core import setup

setup(name='qha',
      version='1.0.0',
      description='A powerful tool for quasi-harmonic approximation',
      author='Tian Qin, Qi Zhang',
      author_email='qinxx197@umn.edu, qz2280@columbia.edu',
      license='GNU General Public License 3',
      url='https://bitbucket.org/singularitti/qha',
      install_requires=[
          'lazy_property',
          'numba',
          'numpy',
          'bigfloat',
          'pandas',
          'scientific-string',
          'scipy',
          'text-stream',
          'pyyaml',
          'matplotlib',
          'seaborn',
      ],
      packages=[
          'qha',
          'qha.multi_configurations',
          'qha.readers',
      ],
      scripts=[
          'scripts/qha',
          'scripts/qha-convert'
      ])
