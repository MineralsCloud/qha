# qha: A Powerful Python toolkit for quasi-harmonic approximation

[TOC]

## What is it

Please check our [documentation](https://mineralscloud.github.io/qha/) for details.

## Quick start: installation

### Python environment

`qha` is written in Python, and can be installed from [Python package index (PyPI)](https://pypi.org/search/?q=qha) or local source files. 

Python 3 can be downloaded from its official [website](https://www.python.org/) for systems including Windows, macOS, and Linux,
please check more details on [Python 3 documentation](https://docs.python.org/3/using/index.html).

To install `qha`, currently, Python 3.6.x distributions are recommended.

Please do not use Python 3.7.x at this moment, since it contains breaking changes and many Python packages don’t support Python 3.7.x yet. We may support Python 3.7.x in the future. 

### Where to get it

Binary installers for the latest released version are available at the PyPI and on conda.

```shell
# use PyPI
$ pip install qha
```

```shell
# use conda
$ conda install qha
```

### Dependencies

- [bigfloat](https://pypi.python.org/pypi/bigfloat)
- [lazy-property](https://github.com/jackmaney/lazy-property)
- [matplotlib](https://matplotlib.org)
- [Numba](http://numba.pydata.org)
- [NumPy](http://www.numpy.org)
- [pandas](https://pandas.pydata.org)
- [PyYAML](http://pyyaml.org)
- [scientific-string](https://github.com/singularitti/scientific-string)
- [SciPy](https://www.scipy.org)
- [text-stream](https://github.com/singularitti/text-stream)

### Installation from sources

The source code is currently hosted on [GitHub](https://github.com/MineralsCloud/qha). Please go to [the “releases” page](https://github.com/MineralsCloud/qha/releases) to download the tagged releases. Unzip the downloaded sources, go to the top-level directory (e.g., `/path/to/repo/qha`), run

```shell
$ pip install .
```

Notice that you have to use Python version 3.6.x to install. If you want to install `qha` in development mode, instead run

```shell
$ pip install -e .
```

### Trouble shooting of installation

1. Error raised about `mpfr.h` file: To solve this error, `GMP` and `MPFR` libraries are required to use `bigfloat` package.
   * On Linux, install `libmpfr-dev` , for example, on Ubuntu type `apt-get install libmpfr-dev`; 
   * On Windows, `bigfloat` can be installed from the binary file, please check [“Unofficial Windows Binaries for Python Extension Packages”](https://www.lfd.uci.edu/~gohlke/pythonlibs/), download the version suitable for the system, for example, for a 64-bit system, use pip to install it `pip(3) install /the/path/to/bigfloat‑0.3.0‑cp36‑cp36m‑win_amd64.whl`;
   * On macOS, install these libraries via `brew install mpfr`. Of course, you need the [Homebrew package manager](https://brew.sh) installed to run this command.


## Checking the examples 

To run the examples, go to `examples/ice VII/` or `examples/silicon/` directories and type in terminal:

```shell
$ qha run /path/to/settings.yaml
```

If you want to plot your results, in the same folder, run

```shell
$ qha plot /path/to/settings.yaml
```

## License

[GNU General Public License v3](./LICENSE.txt)

## Documentation

The official documentation is hosted on our [GitHub page](https://mineralscloud.github.io/qha/).

## Contributors

This repository is now maintained by [Tian Qin](mailto:qinxx197@umn.edu) and [Qi Zhang](mailto:qz2280@columbia.edu). Thanks to the contribution from [Chenxing Luo](https://github.com/chazeon).
