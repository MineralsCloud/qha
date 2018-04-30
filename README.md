# qha: A powerful tool for quasi-harmonic approximation

[TOC]

This repo is created by [Tian Qin](mailto:qinxx197@umn.edu) (Sunny), for in-group use for [Renata Wentzcovitch](mailto:rmw2150@columbia.edu). It is now maintained by [Qi Zhang](mailto:qz2280@columbia.edu) and Sunny.

## What can be done

This code is designed to calculate the thermodynamics properties of crystalline phases with contribution from Phonons (Vibrational Energy). In short, calculate the volume ($V(T, P)$), bulk modulus ($B(T, P)$), enthalpy ($H(T, P)$), Helmholtz free energy ($F(T, P)$), Gibbs free energy ($G(T, P)$) at certain pressure ($P$) and Temperature ($T$).

## Input files needed

1. Input data file: `input`
2. Input control file: You can create your own settings according to the template given in `settings.yaml`.

## Output files

volume ($V(T, P)$), bulk modulus ($B(T, P)$), enthalpy ($H(T, P)$), Helmholtz free energy ($F(T, P)$), Gibbs free energy ($G(T, P)$) at certain pressure ($P$) and Temperature ($T$).

## Where to get it

The source code is currently hosted on [GitHub](https://github.com/MineralsCloud/qha).

Binary installers for the latest released version are available at the Python package index and on conda.

```shell
# conda
$ conda install qha
```

```shell
# or PyPI
$ pip install qha
```

## Dependencies

- [bigfloat](https://pypi.python.org/pypi/bigfloat)[^1]
- [lazy-property](https://github.com/jackmaney/lazy-property)
- [matplotlib](https://matplotlib.org)
- [Numba](http://numba.pydata.org)
- [NumPy](http://www.numpy.org)
- [pandas](https://pandas.pydata.org)
- [PyYAML](http://pyyaml.org)
- [scientific-string](https://github.com/singularitti/scientific-string)
- [SciPy](https://www.scipy.org)
- [text-stream](https://github.com/singularitti/text-stream)

[^1]: `GMP` and `MPFR` libraries are required to use `bigfloat` package. On macOS, install these libraries via `brew install mpfr`; on Linux, install `libmpfr-dev` , for example, on Ubuntu use `[sudo] apt-get install libmpfr-dev`; on Windows, `bigfloat` can be installed from the binary file, please check  "[Unofficial Windows Binaries for Python Extension Packages](https://www.lfd.uci.edu/~gohlke/pythonlibs/)"

## Installation from sources

Download the latest release, and go to the top-level directory, run

```shell
$ python setup.py install
```

Notice that you have to use Python version above 3.5 to install.

## Simple run

```shell
$ qha /path/to/settings.yaml
```

## License

GNU General Public License 3