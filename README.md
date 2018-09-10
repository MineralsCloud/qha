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



## Structure of the `qha` package

The `qha` source code are consists of three major parts.

1. `./qha` directory contains all the source code, it is the main code
2. `./examples` directory contains two examples, `./examples/silicon` is the example for single-configuration calculation, `./examples/ice VII` is the example for multi-configuration calculation.
3. `./docs` dirctory contains all the neccessary file to build the documents in `*.html` format

The brief of the organization of these directories follows as below:



### The main folder `./`

This main folder contains three files, including license information and readme files, and necessary file for installation purpose.

`LICENSE.txt` : The license file attached with the `qha` code 

`README.md` : Readme file of the code

`setup.py` : setup file needed for installation of the `qha` python package.



#### The`./qha/` folder

`qha/__init__.py`  

`qha/calculator.py`:  perform single-, multi-configuration calculations, one of the most important module in this code;

`qha/fitting.py`: Perform the Birch—Murnaghan EOS fitting; 

`qha/grid_interpolation.py`: Find the most suitable volume grid to perform the BM EOS fitting

`qha/plotting.py`: Simple module to plot calcualted physical properties;

`qha/settings.py`: Some default settings for calculation control.

`qha/single_configuration.py`: Calculate Helmholtz free energy for single-configration system  

`qha/statmech.py`: Calculate vibrational energy from calculated freqencies / vibrational density of state(VDOS) 

`qha/thermodynamics.py`: Derive Internal energy(U), enthalpy(H), and Gibbs free energy(G) from calculated Helmholtz free energy via basic thermodynamics relationship.

`qha/tools.py`: miscellaneous functions used in the code, e.g., function used to do  lagranage interpolation, or check whether an array is montonic increasing, etc.

`qha/type_aliases.py`:  

`qha/unit_conversion.py` 

`qha/v2p.py`: Function used to convert calculated properties on (T,V) grid to (T,P) grid

`qha/input_maker.py`  

`qha/out.py` 

##### The `./qha/readers` folder

`qha/readers/__init__.py` 

`qha/readers/read_input.py`

##### The `./qha/cli` folder

`qha/cli/__init__.py` 

`qha/cli/converter.py` 

`qha/cli/handler.py` 

`qha/cli/parser.py`  

`qha/cli/plotter.py`  

`qha/cli/runner.py`  

##### The `./qha/multi_configurations` folder

`qha/multi_configurations/__init__.py` 

`qha/multi_configurations/different_phonon_dos.py` 

`qha/multi_configurations/same_phonon_dos.py` 

##### The `./qha/tests` folder

`qha/tests/__init__.py` 

`qha/tests/test_overall_run.py` 

`qha/tests/test_read_input.py` 

`qha/tests/test_samevdos_overall.py` 

`qha/tests/test_single_configuration.py` 

`qha/tests/test_unit_conversion.py`



#### The `./examples/` folder

This folder contains two examples for demo purpose.

##### The `./examples/ice VII` folder

`examples/ice VII/input_01` : input_01 through input_52 are input files of 52 distinguish configurations;
`examples/ice VII/input_02`
`examples/ice VII/input_03`
`…`
`examples/ice VII/input_52`

`examples/ice VII/settings.yaml`: This file is the calculation setting file, see the tutorial for more details. 

##### The `./examples/silicon` folder

examples/silicon/input
examples/silicon/make_input/README.md
examples/silicon/make_input/V+1.freq
examples/silicon/make_input/V+2.freq
examples/silicon/make_input/V+3.freq
examples/silicon/make_input/V+4.freq
examples/silicon/make_input/V+5.freq
examples/silicon/make_input/V-1.freq
examples/silicon/make_input/V-2.freq
examples/silicon/make_input/V-3.freq
examples/silicon/make_input/V-4.freq
examples/silicon/make_input/V-5.freq
examples/silicon/make_input/V0.freq
examples/silicon/make_input/filelist.yaml
examples/silicon/make_input/q_points
examples/silicon/make_input/static
examples/silicon/settings.yaml



#### The `./docs/` folder

docs/Makefile
docs/make.bat
docs/source/_static/input_format.png
docs/source/api/fitting.rst
docs/source/api/grid_interpolation.rst
docs/source/api/index.rst
docs/source/api/input_maker.rst
docs/source/api/multi_configurations.rst
docs/source/api/read_input.rst
docs/source/api/settings.rst
docs/source/api/single_configuration.rst
docs/source/api/statmech.rst
docs/source/api/thermodynamics.rst
docs/source/api/tools.rst
docs/source/api/unit_conversion.rst
docs/source/api/v2p.rst
docs/source/conf.py
docs/source/develop/contributing.rst
docs/source/develop/index.rst
docs/source/index.rst
docs/source/tutorials/convert.rst
docs/source/tutorials/doc.rst
docs/source/tutorials/index.rst
docs/source/tutorials/installing.rst
docs/source/tutorials/plot.rst
docs/source/tutorials/run.rst



## License

[GNU General Public License v3](./LICENSE.txt)

## Documentation

The official documentation is hosted on our [GitHub page](https://mineralscloud.github.io/qha/).

## Contributors

This repository is now maintained by [Tian Qin](mailto:qinxx197@umn.edu) and [Qi Zhang](mailto:qz2280@columbia.edu). Thanks to the contribution from [Chenxing Luo](https://github.com/chazeon).
