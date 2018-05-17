
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

Dependencies
------------
- `bigfloat <https://pypi.python.org/pypi/bigfloat)>`_
- `lazy-property <https://github.com/jackmaney/lazy-property>`_
- `matplotlib <https://matplotlib.org>`_
- `Numba <http://numba.pydata.org>`_
- `NumPy <http://www.numpy.org>`_
- `pandas <https://pandas.pydata.org>`_
- `PyYAML <http://pyyaml.org>`_
- `scientific-string <https://github.com/singularitti/scientific-string>`_
- `SciPy <https://www.scipy.org>`_
- `text-stream <https://github.com/singularitti/text-stream>`_

Notes:

``GMP`` and ``MPFR`` libraries are required to use ``bigfloat`` package. On macOS,
install these libraries via ``brew install mpfr``; on Linux, install ``libmpfr-dev`` ,
for example, on Ubuntu use ``[sudo] apt-get install libmpfr-dev``;
on Windows, ``bigfloat`` can be installed from the binary file, please check
`Unofficial Windows Binaries for Python Extension Packages <https://www.lfd.uci.edu/~gohlke/pythonlibs/>`_

For some system, ``python-tkinter`` package is needed by ``matplotlib``, otherwise the plot function will not work.

Installing the ``mc-thermo`` package
----------------------------------
Installing using Conda
~~~~~~~~~~~~~~~~~~~~~~

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

Installing using PyPI
~~~~~~~~~~~~~~~~~~~~

``mc-thermo`` can be installed via pip from
`PyPI <http://pypi.python.org/pypi/qha>`__.::

   $ pip(3) install qha

This will likely require the installation of a number of dependencies,
including NumPy, will require a compiler to compile required bits of code,
and can take a few minutes to complete.

Installing from source
~~~~~~~~~~~~~~~~~~~~~~
Download the `latest release <https://github.com/MineralsCloud/qha/releases>`_ , and go to the top-level directory, run::

   $ pip(3) install -e .

Checking your installation
--------------------------

You should be able to import Numba from the Python prompt::

   $ python            
   Python 3.6.4 (default, Mar  9 2018, 23:15:03) 
   [GCC 4.2.1 Compatible Apple LLVM 9.0.0 (clang-900.0.39.2)] on darwin
   Type "help", "copyright", "credits" or "license" for more information.
   >>> import qha
   >>> qha.__version__
   '1.0.9'

