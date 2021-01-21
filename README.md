# qha: A Powerful Python toolkit for quasi-harmonic approximation

[TOC]

[![Stable docs](https://img.shields.io/badge/docs-stable-blue.svg)](https://mineralscloud.github.io/qha/)

## Contributors

This repository is now maintained by [Tian Qin](mailto:qinxx197@umn.edu) and [Qi Zhang](mailto:qz2280@columbia.edu). Thanks to the contribution from [Chenxing Luo](https://github.com/chazeon).

## How to cite

The associated paper is published on [Computer Physics Communications](https://www.sciencedirect.com/science/article/pii/S0010465518303953?via%3Dihub).

Please cite this article as: T. Qin, Q. Zhang, R.M. Wentzcovitch et al., qha: A Python package for quasiharmonic free energy calculation for multi-configuration systems, Computer Physics Communications (2018), https://doi.org/10.1016/j.cpc.2018.11.003.

## Quick start: installation

### Python environment

`qha` is written in Python, and can be installed from [Python package index (PyPI)](https://pypi.org/search/?q=qha) or local source files.

Python 3 can be downloaded from its official [website](https://www.python.org/) for systems including Windows, macOS, and Linux,
please check more details on [Python 3 documentation](https://docs.python.org/3/using/index.html).

To install `qha`, currently, Python 3.6.x distributions are recommended.

Please do not use Python 3.7.x at this moment, since it contains breaking changes and many Python packages don’t support Python 3.7.x yet. We may support Python 3.7.x in the future.

### Where to get it

Binary installers for the latest released version are available at the PyPI.

```shell
# use PyPI
$ pip install qha
```

### Dependencies

- [mpmath](https://mpmath.org/)
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

## Checking the examples

To run the examples, go to `examples/ice VII/` or `examples/silicon/` directories and type in terminal:

```shell
$ qha run /path/to/settings.yaml
```

If you want to plot your results, in the same folder, run

```shell
$ qha plot /path/to/settings.yaml
```



## Structure of the `qha` package

The `qha` source code consists of three major parts.

1. `./qha` directory contains all the source code.

2. `./examples` directory contains two examples, `./examples/silicon` is the example for single-configuration calculation, `./examples/ice VII` is the example for multi-configuration calculation.

The brief of the organization of these directories follows as below:

### The main folder `./`

This main folder contains three folders, license file, readme file, and setup file.

`LICENSE.txt`: The license file attached with the `qha` code;

`README.md`: Readme file of the code, it would be better to view it in a [Markdown](https://en.wikipedia.org/wiki/Markdown) editor, e.g., [Typora](https://typora.io);

`setup.py`: setup file needed for installation of the `qha` Python package.

#### The `./qha/` folder

`qha/__init__.py`: Tells Python interpreter that this is a Python package;

`qha/calculator.py`: Perform single-, multi-configuration calculations, one of the most crucial modules in this code;

`qha/fitting.py`: Perform the Birch—Murnaghan (BM) equation-of-state (EOS) fitting;

`qha/grid_interpolation.py`: Find the most suitable volume grid to perform the BM EOS fitting;

`qha/plotting.py`: A simple module to plot the calculated physical properties;

`qha/settings.py`: Define some computational settings for the calculation;

`qha/single_configuration.py`: Calculate the Helmholtz free energy for a single-configuration system;

`qha/statmech.py`: Define some useful statistical mechanics functions;

`qha/thermodynamics.py`: Derive the internal energy($U$), enthalpy($H$), and Gibbs free energy ($G$) from the calculated Helmholtz free energy ($F$) via basic thermodynamics relationship;

`qha/tools.py`: Define some miscellaneous functions used in the code, e.g., function used to perform Lagrange interpolation;

`qha/type_aliases.py`: Define some types for annotation in the code;

`qha/unit_conversion.py`: A module to convert units used in the calculation;

`qha/v2p.py`: Contain the function `v2p` used to convert calculated properties on $(T, V)$ grid to $(T, P)$ grid;

`qha/input_maker.py`: Generate the input file for `qha` from results obtained from *ab initio* calculation;

`qha/out.py`: Functions used to write calculated properties into files.

##### The `./qha/readers` folder

`qha/readers/__init__.py`

`qha/readers/read_input.py`: This module is used to read the input file.

##### The `./qha/cli` folder

This folder contains files used for the command-line interface.

`qha/cli/__init__.py`

`qha/cli/converter.py`

`qha/cli/handler.py`

`qha/cli/parser.py`

`qha/cli/plotter.py`

`qha/cli/runner.py`

##### The `./qha/multi_configurations` folder

This folder contains files to calculate Helmholtz free energy for the multi-configuration system.

`qha/multi_configurations/__init__.py`

`qha/multi_configurations/different_phonon_dos.py`: Work with `qha/calculator.py` to calculate Helmholtz free energy for the multi-configuration system with different phonon density of states (VDOS) for each configuration;

`qha/multi_configurations/same_phonon_dos.py`: Work with `qha/calculator.py` to calculate Helmholtz free energy for multi-configuration system with the same VDOS for all configurations.

##### The `./qha/tests` folder

this folder contains unit test files

`qha/tests/__init__.py`

`qha/tests/test_overall_run.py`

`qha/tests/test_read_input.py`

`qha/tests/test_samevdos_overall.py`

`qha/tests/test_single_configuration.py`

`qha/tests/test_unit_conversion.py`

#### The `./examples/` folder

This folder contains two examples for demonstration purpose.

##### The `./examples/silicon` folder

This folder conations an example to perform the single-configuration calculation. Also, an example to generate the input file for the `qha` code is included, check `examples/silicon/make_input/README` for details;

`examples/silicon/input`: The input file for `qha`;

`examples/silicon/settings.yaml`: This file is the computational settings file.

##### The `./examples/ice VII` folder

`examples/ice VII/input_01` : `input_01` through `input_52` are the input files of 52 distinguish configurations;
`examples/ice VII/input_02`
`examples/ice VII/input_03`
`…`
`examples/ice VII/input_52`

`examples/ice VII/settings.yaml`: This file is the computational settings file, see our online [tutorial](https://mineralscloud.github.io/qha/tutorials/index.html) for more details.

## License

[GNU General Public License v3](./LICENSE.txt)

## Documentation

The official documentation is hosted on our [GitHub page](https://mineralscloud.github.io/qha/).

