
Getting started
===============

Compatibility
-------------

qha is compatible with Python 3.5 or later, and Numpy versions 1.7 to 1.14.

Our supported platforms are:

* Linux x86 (32-bit and 64-bit)
* Windows 7 and later (32-bit and 64-bit)
* OS X 10.9 and later (64-bit)
* NVIDIA GPUs of compute capability 2.0 and later
* AMD APUs supported by the HSA 1.0 final runtime (Kaveri, Carrizo)


Installing using Conda
----------------------

The easiest way to install qha and get updates is by using Conda,
a cross-platform package manager and software distribution maintained
by Anaconda, Inc.  You can either use `Anaconda
<https://www.anaconda.com/download>`_ to get the full stack in one download,
or `Miniconda <https://conda.io/miniconda.html>`_ which will install
the minimum packages needed to get started.

Once you have conda installed, just type::

   $ conda install qha

or::

   $ conda update qha

Installing from PyPI
~~~~~~~~~~~~~~~~~~~~

pandas can be installed via pip from
`PyPI <http://pypi.python.org/pypi/qha>`__.::

   $ pip install qha

This will likely require the installation of a number of dependencies,
including NumPy, will require a compiler to compile required bits of code,
and can take a few minutes to complete.

Checking your installation
--------------------------

You should be able to import Numba from the Python prompt::

   $ python            
   Python 3.6.4 (default, Mar  9 2018, 23:15:03) 
   [GCC 4.2.1 Compatible Apple LLVM 9.0.0 (clang-900.0.39.2)] on darwin
   Type "help", "copyright", "credits" or "license" for more information.
   >>> import qha
   >>> qha.__version__
   '0.0.1'

