"""
Tests for module awa_demo

@author: Damares Resende
@contact: damaresresende@usp.br
@since: Apr 25, 2020

@organization: University of Sao Paulo (USP)
    Institute of Mathematics and Computer Science (ICMC)
    Laboratory of Visualization, Imaging and Computer Graphics (VICG)
"""
import unittest
import numpy as np

from ..src.awa_demo import AWA


class AWATests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """
        Initializes variables to be used in the tests
        """
        cls.awa = AWA('../../Datasets/SAE/awa_demo_data.mat')

    def test_v2s_projection(self):
        """
        Tests if the returned accuracy is the expected one
        """
        self.assertEqual(0.84676, np.around(self.awa.v2s_projection(), decimals=5))

    def test_s2v_projection(self):
        """
        Tests if the returned accuracy is the expected one
        """
        self.assertEqual(0.83997, np.around(self.awa.s2v_projection(), decimals=5))
