#!/usr/bin/env python3

from pathlib import Path

from qha.input_maker import FromQEOutput


class ConvertHandler:
    def __init__(self, arguments_for_command: dict = {}):
        if not isinstance(arguments_for_command, dict):
            raise TypeError("The *arguments_for_command* argument must be a dictionary!")

        if not all(isinstance(k, str) for k in arguments_for_command.keys()):
            raise TypeError("The *arguments_for_command* argument's keys must be all strings!")

        if not all(isinstance(v, str) for v in arguments_for_command.values()):
            raise TypeError("The *arguments_for_command* argument's values must be all strings!")

        inp_file_list = arguments_for_command['inp_file_list']
        inp_static = arguments_for_command['inp_static']
        inp_q_points = arguments_for_command['inp_q_points']

        for file in (inp_file_list, inp_static, inp_q_points):
            if not Path(file).is_file():
                raise FileNotFoundError("File '{0}' not found!".format(file))

        self._arguments_for_command = arguments_for_command
        self.inp_file_list = inp_file_list
        self.inp_static = inp_static
        self.inp_q_points = inp_q_points

    def run(self):
        converter = FromQEOutput(self.inp_file_list, self.inp_static, self.inp_q_points)
        converter.read_file_list()
        converter.read_static()
        converter.read_q_points()
        converter.read_frequency_files()
        converter.write_to_file()
