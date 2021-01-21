#!/usr/bin/env python3

import codecs
import os
import re
from distutils.core import setup

import setuptools

# Referenced from `here <https://packaging.python.org/guides/single-sourcing-package-version/>`_.
here = os.path.abspath(os.path.dirname(__file__))


def read(*parts):
    with codecs.open(os.path.join(here, *parts), 'r') as fp:
        return fp.read()


def find_version(*file_paths):
    version_file = read(*file_paths)
    version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]",
                              version_file, re.M)
    if version_match:
        return version_match.group(1)
    raise RuntimeError("Unable to find version string.")


setup(name='qha',
      version=find_version('qha', '__init__.py'),
      description='A powerful tool for quasi-harmonic approximation',
      author='Tian Qin, Qi Zhang',
      author_email='qinxx197@umn.edu, qz2280@columbia.edu',
      maintainer='Tian Qin, Qi Zhang',
      maintainer_email='qinxx197@umn.edu, qz2280@columbia.edu',
      license='GNU General Public License 3',
      url='https://github.com/MineralsCloud/qha',
      classifiers=[
          'Development Status :: 5 - Production/Stable',
          'Intended Audience :: Science/Research',
          'Topic :: Scientific/Engineering :: Physics',
          'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
          'Programming Language :: Python :: 3.6',
          'Programming Language :: Python :: 3.7',
          'Programming Language :: Python :: 3.8',
      ],
      python_requires='>=3.6',
      keywords='thermodynamic-properties quasi-harmonic-approximation scientific-computation',
      install_requires=[
          'lazy_property',
          'numba',
          'mpmath',
          'numpy',
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
          'qha.cli',
          'qha.basic_io',
      ],
      entry_points={
          'console_scripts': [
              'qha=qha.cli:main'
          ],
      })
