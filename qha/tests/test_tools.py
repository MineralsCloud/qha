#!/usr/bin/env python3

import unittest

import numpy as np

import qha.tools


class TestTools(unittest.TestCase):
    def test_find_nearest(self):
        xs = np.arange(10, 10000)
        index = qha.tools.find_nearest(xs, 501.9)
        self.assertEqual(xs[index], 501)

    def test_lagrange3(self):
        xs = [0, 1, 3]
        ys = [2, 4, 5]
        f = qha.tools.lagrange3(xs, ys)
        self.assertEqual(f(2.5), 5.125)
