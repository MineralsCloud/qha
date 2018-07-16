# Example to run `qha-convert`

This tutorial is suitable for outputs from Quantum ESPRESSO.

## Necessary files

Three files are needed to run this script to generate input file for `qha` script:

1. `filelist.yaml` file
  * the description of the system in `comment` key: a string,
  * the number of formula unit in `formula_unit_number` key: an integer,
  * A YAML list of files containing frequencies `*.freq` in `frequency_files` key: a YAML list of strings.

  If you have trouble writing YAML, please refer to its syntax [here](http://docs.ansible.com/ansible/latest/reference_appendices/YAMLSyntax.html).

2. `static` file: Contains the pressures (in kbar or GPa), optimized volumes (in bohr$^3$) and energies (static energies in Rydberg unit).

3. `q_points` file: Contains the q-points' coordinates and their weights in the Brillouin zone.

## Usage

After preparing those three files, just run

```shell
$ qha-convert filelist.yaml static q_points
```

and if there was already an input, it will be backuped. The names of these three files can be arbitrary but currently the order of `qha-convert` cannot be changed.

