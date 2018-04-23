#!/usr/bin/env python3
# Created at Mar 19, 2018, by Qi Zhang

import unittest
from inspect import getmembers
from typing import List

import numpy as np

import qha.unit_conversion
from qha.unit_conversion import *


class TestUnitConversion(unittest.TestCase):
    def test_j_to_ev(self):
        self.assertEqual(j_to_ev(1), 6.241509125883258e+18)
        self.assertEqual(j_to_ev(900), 5.617358213294932e+21)

    def test_gpa_to_megabar(self):
        self.assertEqual(gpa_to_megabar(1), 0.01)
        self.assertEqual(gpa_to_megabar(900), 9)

    def test_b3_to_a3(self):
        self.assertAlmostEqual(b3_to_a3(1), 0.148185, places=6)
        self.assertAlmostEqual(b3_to_a3(900), 133.366, places=3)

    def test_eh_to_cm_inverse(self):
        self.assertEqual(eh_to_cm_inverse(1), 219474.6313702)
        self.assertAlmostEqual(eh_to_cm_inverse(900), 1.9752716823318e8, places=5)

    def test_ev_to_cm_inverse(self):
        self.assertAlmostEqual(ev_to_cm_inverse(1), 8065.540106923572, places=2)
        self.assertAlmostEqual(ev_to_cm_inverse(900), 7258986.096231216, places=-1)

    def test_ev_to_k(self):
        self.assertAlmostEqual(ev_to_k(1), 11604.52500617, places=2)
        self.assertAlmostEqual(ev_to_k(900), 10444072.505553002, places=-2)

    def test_ev_a3_to_gpa(self):
        self.assertAlmostEqual(ev_a3_to_gpa(1), 160.21766208, places=6)
        self.assertAlmostEqual(ev_a3_to_gpa(900), 144195.895872)

    def test_ha_b3_to_gpa(self):
        self.assertAlmostEqual(ha_b3_to_gpa(1), 29421.02648438959, places=1)
        self.assertAlmostEqual(ha_b3_to_gpa(900), 26478923.83595063, places=-2)

    def test_ry_b_to_ev_a(self):
        self.assertAlmostEqual(ry_b_to_ev_a(1), 25.71104309541616, places=4)
        self.assertAlmostEqual(ry_b_to_ev_a(900), 23139.930180659605, places=2)

    def test_ha_b_to_ev_a(self):
        self.assertAlmostEqual(ha_b_to_ev_a(1), 51.42208619083232, places=4)
        self.assertAlmostEqual(ha_b_to_ev_a(900), 46279.86036472072, places=1)

    def test_ry_to_kj_mol(self):
        self.assertAlmostEqual(ry_to_kj_mol(1), 1312.7498191426082)
        self.assertAlmostEqual(ry_to_kj_mol(900), 1181474.8372283475)

    def test_vectorize(self):
        """
        All the unit conversion functions are ``Numpy.ufunc`` objects, so this method just test
        whether they are mappable to 1D and 2D arrays.
        """
        vector = np.linspace(0, 100, num=50)
        grid = np.random.randint(0, 1000, size=(3, 3))

        def isufunc(obj):
            if type(obj) is np.ufunc:
                return True
            return False

        all_ufuncs: List[np.ufunc] = [obj[1] for obj in getmembers(qha.unit_conversion, isufunc)]
        for ufunc in all_ufuncs:
            self.assertEqual(ufunc(vector).size, 50)
            self.assertEqual(ufunc(grid).shape, (3, 3))
