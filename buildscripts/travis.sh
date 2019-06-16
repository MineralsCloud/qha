#!/bin/bash
set -ev

echo "Do Python tests"
pytest qha/tests/test_different_phonon_dos.py
pytest qha/tests/test_read_input.py
pytest qha/tests/test_single_configuration.py
pytest qha/tests/test_unit_conversion.py
pytest qha/tests/test_input_maker.py

echo "Build docs"
cd docs/
make clean && make html
