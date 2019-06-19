#!/bin/bash
set -ev

qha -V

cd examples/
cd silicon
qha run ./settings.yaml
cd ..
cd ice\ VII
qha run ./settings.yaml
cd ..
pwd # I am at root/qha/examples
cd ..

echo "Do Python tests"
pytest qha/tests/test_different_phonon_dos.py
pytest qha/tests/test_read_input.py
pytest qha/tests/test_single_configuration.py
pytest qha/tests/test_unit_conversion.py
pytest qha/tests/test_input_maker.py
pytest qha/tests/test_overall_run.py

echo "Build docs"
cd docs/
make clean && make html
