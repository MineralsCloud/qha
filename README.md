# qha: Powerful Python toolkit for quasi-harmonic approximation

[TOC]

## 1. About this code

Please check our [documentation](https://mineralscloud.github.io/qha/) for details.



## 2. Quick start: installation

### 2.1. Python 3.6.x required

`qha` is written in Python3, and can be installed from [Python package index (PyPI)](https://pypi.org/search/?q=qha) or local source files. 

Python3 can be downloaded from its official [website](https://www.python.org/) for Windows OS, MacOS, and Linux, check more details on [Python3 documentations](https://docs.python.org/3/using/index.html)

Python3.6.x are recommended. 

Please do not use Python3.7.x at this moment, since it contains breaking changes and many Python package don’t support Python3.7.x now, we may support Python3.7.x in the future. 

### 2.2.a. Install `qha` code from the internet via `conda` or `pip`

**Note**: Currently, there is no available online installation (on PyPI), check section [Installation from the source code](### Installation from the source code) to install it from the source code

Binary installers for the latest released version are available at the PyPI and on conda.

```shell
# use PyPI
$ pip install qha
```

```shell
# use conda
$ conda install qha
```



### 2.2.b. Installation from the source code

The source code is currently hosted on [GitHub](https://github.com/MineralsCloud/qha).

Download the latest release and unzip it, go to the top-level directory (e.g., `/path/to/repo/qha`), run

```shell
$ pip install .
```

Notice that you have to use Python version 3.6.x to install. If you want to install `qha` in development mode, instead run

```shell
$ pip install -e .
```



### 2.3. Trouble shooting of installation

1. Error raised about `mpfr.h` file, which belongs to a key library that `bigfloat` depends on `GMP` and `MPFR` libraries are required to use `bigfloat` package.
   * On Linux, install `libmpfr-dev` , for example, on Ubuntu use `apt-get install libmpfr-dev`; 
   * On Windows, `bigfloat` can be installed from the binary file, please check  "[Unofficial Windows Binaries for Python Extension Packages](https://www.lfd.uci.edu/~gohlke/pythonlibs/)", download the version suitable for the system, for example, for 64-bit version, use pip to install it `pip(3) install /the/path/to/bigfloat‑0.3.0‑cp36‑cp36m‑win_amd64.whl`
   * On macOS, install these libraries via `brew install mpfr`.



## 2.4. Checking the  examples 

To run the examples, go to `examples/ice VII/` or `examples/silicon/` 

```shell
$ qha run /path/to/settings.yaml
```

If you want to plot your results, in the same folder, run

```shell
$ qha plot /path/to/settings.yaml
```

## 2.5. Dependencies

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



## License

[GNU General Public License v3](./LICENSE.txt)

## Contributors

This repository is now maintained by [Tian Qin](mailto:qinxx197@umn.edu) and [Qi Zhang](mailto:qz2280@columbia.edu). Thanks to the contribution from [Chenxing Luo](https://github.com/chazeon).