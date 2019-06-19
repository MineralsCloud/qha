#!/usr/bin/env python3
# Created at Jun 15, 2019, by Qi Zhang


import filecmp
import os
import pathlib
import unittest

from qha.basic_io.input_maker import FromQEOutput


class TestMakeInput(unittest.TestCase):
    def setUp(self) -> None:
        self.dir = pathlib.Path(
            __file__).parent.parent.parent / 'examples/silicon/make_input/'
        os.chdir(self.dir)

    def test_make_input(self):
        converter = FromQEOutput(
            self.dir / 'filelist.yaml', self.dir / 'static', self.dir / 'q_points')
        converter.read_file_list()
        converter.read_static()
        converter.read_q_points()
        converter.read_frequency_files()
        converter.write_to_file(str(self.dir / 'input'))
        self.assertTrue(filecmp.cmp(self.dir / 'input', self.dir / '../input'))


if __name__ == '__main__':
    unittest.main()
