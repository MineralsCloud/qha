import unittest

import numpy as np
from qha.v2p import v2p, v2p_new


class TestV2P(unittest.TestCase):
    def setUp(self):
        self.gtp = np.loadtxt('./data/si/g_tp_ry.txt')
        self.gtv = np.loadtxt('./data/si/g_tv_ry.txt')
        self.ptv = np.loadtxt('./data/si/p_tv_au.txt')
        self.DESIRED_PRESSURES = np.loadtxt('./data/si/DESIRED_PRESSURES.txt')
        self.gtp_new = v2p_new(self.gtv, self.ptv, self.DESIRED_PRESSURES)

    def test_v2p(self):
        print(np.abs(self.gtp-self.gtp_new).max())
        np.testing.assert_array_almost_equal(self.gtp, self.gtp_new, decimal=5)
        self.assertLessEqual((self.gtp-self.gtp_new).max(),1.0e-8)
