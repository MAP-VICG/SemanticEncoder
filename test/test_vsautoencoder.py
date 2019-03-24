'''
Tests for module vsautoencoder

@author: Damares Resende
@contact: damaresresende@usp.br
@since: Mar 23, 2019

@organization: University of Sao Paulo (USP)
    Institute of Mathematics and Computer Science (ICMC) 
    Laboratory of Visualization, Imaging and Computer Graphics (VICG)
'''

import os
import unittest
from math import floor
from keras.utils import normalize
from sklearn.model_selection import train_test_split

from core.vsautoencoder import VSAutoencoder
from core.featuresparser import FeaturesParser, PredicateType


class VSAutoencoderTests(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        '''
        Initializes model for all tests
        '''
        cls.fls_path = os.path.join(os.getcwd(), '_mockfiles/awa2')
        fts_path = os.path.join(cls.fls_path, 'features/ResNet101')
        ann_path = os.path.join(cls.fls_path, 'base')
    
        parser = FeaturesParser(fts_path)
        vis_fts = parser.get_visual_features()
        
        sem_fts = normalize(parser.get_semantic_features(ann_path, 
                                                         PredicateType.CONTINUOUS) + 1, 
                                                         order=1, 
                                                         axis=1)
        
        X = parser.concatenate_features(vis_fts, sem_fts)
        Y = parser.get_labels()
        x_train, cls.x_test, _, _ = train_test_split(X, Y, stratify=Y, test_size=0.2)
        
        cls.enc_dim = 32
        cls.io_dim = x_train.shape[1]
        cls.nexamples = x_train.shape[0]
        
        cls.ae = VSAutoencoder()
        cls.history = cls.ae.run_autoencoder(x_train, cls.enc_dim, 15)
        
    def test_build_autoencoder(self):
        '''
        Tests if autoencoder is built correctly
        '''
        middle = floor(len(self.ae.autoencoder.layers) / 2)
           
        # input
        self.assertEqual((None, self.io_dim), self.ae.autoencoder.layers[0].input_shape)
           
        # encoding
        self.assertEqual((None,  self.enc_dim), self.ae.autoencoder.layers[middle].output_shape)
           
        # output
        self.assertEqual((None, self.io_dim), self.ae.autoencoder.layers[-1].output_shape)
          
    def test_train_autoencoder(self):
        '''
        Tests if autoencoder can be trained
        '''
        self.assertEqual(self.history.params['epochs'], len(self.history.epoch))
        self.assertEqual(self.history.params['epochs'], len(self.history.history['val_loss']))
        self.assertEqual(self.history.params['epochs'], len(self.history.history['loss']))
        self.assertEqual(floor(self.nexamples * 0.8), self.history.params['samples'])
        self.assertTrue(self.history.params['do_validation'])
        
    def test_plot_loss(self):
        '''
        Tests if loss and validation loss are plot and saved to ae_loss.png
        '''
        res_path = os.path.join(self.fls_path, 'results')
        file_name = os.path.join(res_path, 'ae_loss.png')
           
        if os.path.isfile(file_name):
            os.remove(file_name)
           
        self.ae.plot_loss(self.history.history, os.path.join(res_path, 'ae_loss.png'))
        self.assertTrue(os.path.isfile(file_name))
        
    def test_plot_error(self):
        '''
        Tests if error is plot to ae_error.png
        '''
        res_path = os.path.join(self.fls_path, 'results')
        file_name = os.path.join(res_path, 'ae_error.png')
           
        if os.path.isfile(file_name):
            os.remove(file_name)
           
        self.ae.plot_error(self.x_test, os.path.join(res_path, 'ae_error.png'))
        self.assertTrue(os.path.isfile(file_name))