#!/usr/bin/env python3

from distutils.core import setup

setup(name='qha',
      version='1.0.6',
      description='A powerful tool for quasi-harmonic approximation',
      author='Tian Qin, Qi Zhang',
      author_email='qinxx197@umn.edu, qz2280@columbia.edu',
      maintainer='Tian Qin, Qi Zhang',
      maintainer_email='qinxx197@umn.edu, qz2280@columbia.edu',
      license='GNU General Public License 3',
      url='https://bitbucket.org/singularitti/qha',
      classifiers=[
          'Development Status :: 5 - Production/Stable',
          'Intended Audience :: Science/Research',
          'Topic :: Scientific/Engineering :: Physics',
          'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
          'Programming Language :: Python :: 3.5',
          'Programming Language :: Python :: 3.6',
      ],
      python_requires='>=3.5',
      keywords='thermodynamic-properties quasi-harmonic-approximation scientific-computation',
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
      entry_points={
          'console_scripts': [
              'qha=qha.qha:main',
              'qha-convert=qha.qha_convert:main'
          ],
      })
