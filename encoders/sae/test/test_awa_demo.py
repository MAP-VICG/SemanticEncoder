"""
Tests for module awa_demo

@author: Damares Resende
@contact: damaresresende@usp.br
@since: Apr 25, 2020

@organization: University of Sao Paulo (USP)
    Institute of Mathematics and Computer Science (ICMC)
    Laboratory of Visualization, Imaging and Computer Graphics (VICG)
"""
import os
import unittest
import numpy as np

from ..src.awa_demo import AWA


class AWATests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """
        Initializes variables to be used in the tests
        """
        cls.data_tr = os.sep.join([os.getcwd().split('/encoders')[0], 'data', 'awa_data_inceptionV1_tr.pbz2'])
        cls.data_te = os.sep.join([os.getcwd().split('/encoders')[0], 'data', 'awa_data_inceptionV1_te.pbz2'])

        cls.awa = AWA(cls.data_tr, cls.data_te)
        cls.awa.set_semantic_data()

    def test_set_semantic_data(self):
        """
        Tests if semantic data for training can be replaced
        """
        dummy_data = np.zeros((24295, 85))
        dummy_awa = AWA(self.data_tr, self.data_te)

        dummy_awa.set_semantic_data(dummy_data)
        self.assertEqual(0.08236, np.around(dummy_awa.v2s_projection(), decimals=5))

    def test_reset_weights(self):
        """
        Tests if weights can be properly reset so projection accuracy would change appropriately
        """
        dummy_awa = AWA(self.data_tr, self.data_te)
        dummy_awa.set_semantic_data()

        self.assertIsNone(dummy_awa.w)
        self.assertEqual(0.84676, np.around(dummy_awa.v2s_projection(), decimals=5))

        dummy_awa.reset_weights()
        self.assertIsNone(dummy_awa.w)

        dummy_data = np.zeros((24295, 85))
        dummy_awa.set_semantic_data(dummy_data)
        self.assertEqual(0.08236, np.around(dummy_awa.v2s_projection(), decimals=5))

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
