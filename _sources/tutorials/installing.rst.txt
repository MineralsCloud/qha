.. _installing:

Getting started
===============

.. contents:: Table of contents:
   :local:

Compatibility
-------------

``qha`` is compatible with Python 3.6.x.
Please do not use Python 3.7.x at this moment, since it contains breaking changes
and many Python packages don’t support Python 3.7.x yet. We may support Python 3.7.x in the future.

Our supported platforms are:

* Linux x86 (32-bit and 64-bit)
* Windows 7 and later (32-bit and 64-bit)
* OS X 10.9 and later (64-bit)
* NVIDIA GPUs of compute capability 2.0 and later

Dependencies
------------
- `bigfloat <https://pypi.python.org/pypi/bigfloat>`_ [#b]_
- `lazy-property <https://github.com/jackmaney/lazy-property>`_
- `matplotlib <https://matplotlib.org>`_ [#m]_
- `Numba <http://numba.pydata.org>`_
- `NumPy <http://www.numpy.org>`_
- `pandas <https://pandas.pydata.org>`_
- `PyYAML <http://pyyaml.org>`_
- `scientific-string <https://github.com/singularitti/scientific-string>`_
- `SciPy <https://www.scipy.org>`_
- `text-stream <https://github.com/singularitti/text-stream>`_

Notes:

.. [#b] ``GMP`` and ``MPFR`` libraries are required to use ``bigfloat`` package. On macOS,
    install these libraries via ``brew install mpfr``; on Linux, install ``libmpfr-dev`` ,
    for example, on Ubuntu use ``apt-get install libmpfr-dev``;
    on Windows, ``bigfloat`` can be installed from the binary file, please check
    `Unofficial Windows Binaries for Python Extension Packages <https://www.lfd.uci.edu/~gohlke/pythonlibs/>`_,
    download the version suitable for the system, for example,for a 64-bit system,
    use pip to install it ``pip(3) install /the/path/to/bigfloat‑0.3.0‑cp36‑cp36m‑win_amd64.whl``;

.. [#m] For some systems, ``python-tkinter`` package is needed by ``matplotlib``, otherwise the plot function will not work.

Installing the ``qha`` package
------------------------------
Installing using PyPI
~~~~~~~~~~~~~~~~~~~~~~

``qha`` can be installed via pip from
`PyPI <http://pypi.python.org/pypi/qha>`__.::

   $ pip install qha

This will likely require the installation of a number of dependencies,
including NumPy, will require a compiler to compile required bits of code,
and can take a few minutes to complete.

Installing from source
~~~~~~~~~~~~~~~~~~~~~~
Download the `latest release <https://github.com/MineralsCloud/qha/releases>`_ , and go to the top-level directory, run::

   $ pip install -e .

Checking your installation
--------------------------

You should be able to import Numba from the Python prompt::

   $ python
   Python 3.6.5 (default, Jun 18 2018, 22:40:57)
   [GCC 4.2.1 Compatible Apple LLVM 9.1.0 (clang-902.0.39.2)] on darwin
   Type "help", "copyright", "credits" or "license" for more information.
   >>> import qha
   >>> qha.__version__
   '1.0.12'

