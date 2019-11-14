'''
Unit tests for normalization module

@author: Damares Resende
@contact: damaresresende@usp.br
@since: Nov 13, 2019

@organization: University of Sao Paulo (USP)
    Institute of Mathematics and Computer Science (ICMC) 
    Laboratory of Visualization, Imaging and Computer Graphics (VICG)
'''

import os
import unittest

from src.core.featuresparser import FeaturesParser
from src.utils.normalization import Normalization


class NormalizationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        '''
        Initializes model for all tests
        '''
        cls.parser = FeaturesParser(fts_dir=os.path.join('features', 'mock'), console=True)
        
    def test_norm_zero_one(self):
        '''
        Tests if dataset is normalized to values between zero and one
        '''
        sem_fts = self.parser.get_semantic_features(subset=False, binary=False)
        norm = Normalization(sem_fts)
        
        self.assertEqual(100, norm.max_global)
        self.assertEqual(-1, norm.min_global)
        
        norm.normalize_zero_one_global(sem_fts)
        
        self.assertEqual(1, sem_fts.max())
        self.assertEqual(0, sem_fts.min())
        
    def test_norm_visual(self):
        '''
        Tests if visual features dataset is normalized between zero and one by column
        '''
        sem_fts = self.parser.get_semantic_features(subset=False, binary=False)
        norm = Normalization(sem_fts)
        norm.normalize_zero_one_by_column(sem_fts)
        
        for col in range(sem_fts.shape[1]):
            self.assertEqual(1, sem_fts[:,col].max())
            self.assertEqual(0, sem_fts[:,col].min())