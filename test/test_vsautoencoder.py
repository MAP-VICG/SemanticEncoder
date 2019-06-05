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

from core.featuresparser import FeaturesParser, PredicateType
from core.vsautoencoder import VSAutoencoderSingleInput, VSAutoencoderDoubleInput, VSAutoencoderUNet


class VSAutoencoderTests(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        '''
        Initializes model for all tests
        '''
        fls_path = os.path.join(os.getcwd(), '_mockfiles/awa2')
        fts_path = os.path.join(fls_path, 'features/ResNet101')
        cls.res_path = os.path.join(fls_path, 'results')
        ann_path = os.path.join(fls_path, 'base')
    
        parser = FeaturesParser(fts_path)
        vis_fts = parser.get_visual_features()
        
        sem_fts = normalize(parser.get_semantic_features(ann_path, 
                                                         PredicateType.BINARY) + 1, 
                                                         order=1, 
                                                         axis=1)
        
        X = parser.concatenate_features(vis_fts, sem_fts)
        Y = parser.get_labels()
        x_train, cls.x_test, y_train, cls.y_test = train_test_split(X, Y, stratify=Y, test_size=0.2)
        
        cls.enc_dim = 32
        cls.nexamples = x_train.shape[0]
        
        cls.ae = VSAutoencoderSingleInput(cv=2, njobs=2, x_train=x_train, x_test=cls.x_test, 
                                        y_train=y_train, y_test=cls.y_test)
        cls.history = cls.ae.run_autoencoder(cls.enc_dim, 15, os.path.join(cls.res_path, 
                                                                            'ae_svm_classification.txt'))
            
        cls.ae_double = VSAutoencoderDoubleInput(cv=2, njobs=2, x_train=x_train, x_test=cls.x_test, 
                                                 y_train=y_train, y_test=cls.y_test, split=2048)
        cls.ae_double_history = cls.ae_double.run_autoencoder(cls.enc_dim, 15, 
                                                              os.path.join(cls.res_path, 
                                                                           'ae_svm_classification.txt'))
        
        cls.ae_unet = VSAutoencoderUNet(cv=2, njobs=2, x_train=x_train, x_test=cls.x_test, 
                                                 y_train=y_train, y_test=cls.y_test, split=2048)
        cls.ae_unet_history = cls.ae_unet.run_autoencoder(cls.enc_dim, 15, 
                                                          os.path.join(cls.res_path, 
                                                                       'ae_svm_classification.txt'))
         
    def test_build_autoencoder(self):
        '''
        Tests if autoencoder is built correctly
        '''
        middle = floor(len(self.ae.autoencoder.layers) / 2)
             
        # input
        self.assertEqual((None, 2133), self.ae.autoencoder.layers[0].input_shape)
             
        # encoding
        self.assertEqual((None,  self.enc_dim), self.ae.autoencoder.layers[middle].output_shape)
             
        # output
        self.assertEqual((None, 2133), self.ae.autoencoder.layers[-1].output_shape)
            
    def test_train_autoencoder(self):
        '''
        Tests if autoencoder can be trained
        '''
        self.assertEqual(self.history.params['epochs'], len(self.history.epoch))
        self.assertEqual(self.history.params['epochs'], len(self.history.history['val_loss']))
        self.assertEqual(self.history.params['epochs'], len(self.history.history['loss']))
        self.assertEqual(floor(self.nexamples * 0.8), self.history.params['samples'])
        self.assertTrue(self.history.params['do_validation'])
         
    def test_build_autoencoder_double(self):
        '''
        Tests if autoencoder is built correctly
        '''
        middle = floor(len(self.ae_double.autoencoder.layers) / 2) + 2
           
        # input
        self.assertEqual((None, 85, 1), self.ae_double.autoencoder.layers[1].input_shape)
        self.assertEqual((None, 2048), self.ae_double.autoencoder.layers[2].input_shape)
           
        # encoding
        self.assertEqual((None,  self.enc_dim), self.ae_double.autoencoder.layers[middle].output_shape)
           
        # output
        self.assertEqual((None, 2133), self.ae_double.autoencoder.layers[-1].output_shape)
                 
    def test_train_autoencoder_double(self):
        '''
        Tests if autoencoder can be trained
        '''
        self.assertEqual(self.ae_double_history.params['epochs'], len(self.ae_double_history.epoch))
        self.assertEqual(self.ae_double_history.params['epochs'], len(self.ae_double_history.history['val_loss']))
        self.assertEqual(self.ae_double_history.params['epochs'], len(self.ae_double_history.history['loss']))
        self.assertEqual(floor(self.nexamples * 0.8), self.ae_double_history.params['samples'])
        self.assertTrue(self.ae_double_history.params['do_validation'])
        
    def test_build_autoencoder_unet(self):
        '''
        Tests if autoencoder is built correctly
        '''
        middle = floor(len(self.ae_unet.autoencoder.layers) / 2)
             
        # input
        self.assertEqual((None, 2133), self.ae_unet.autoencoder.layers[0].input_shape)
             
        # encoding
        self.assertEqual((None,  self.enc_dim), self.ae_unet.autoencoder.layers[middle].output_shape)
             
        # output
        self.assertEqual((None, 2133), self.ae_unet.autoencoder.layers[-1].output_shape)
                 
    def test_train_autoencoder_unet(self):
        '''
        Tests if autoencoder can be trained
        '''
        self.assertEqual(self.ae_unet_history.params['epochs'], len(self.ae_unet_history.epoch))
        self.assertEqual(self.ae_unet_history.params['epochs'], len(self.ae_unet_history.history['val_loss']))
        self.assertEqual(self.ae_unet_history.params['epochs'], len(self.ae_unet_history.history['loss']))
        self.assertEqual(floor(self.nexamples * 0.8), self.ae_unet_history.params['samples'])
        self.assertTrue(self.ae_unet_history.params['do_validation'])
         
    def test_plot_loss(self):
        '''
        Tests if loss and validation loss are plot and saved to ae_loss.png
        '''
        file_name = os.path.join(self.res_path, 'ae_loss.png')
             
        if os.path.isfile(file_name):
            os.remove(file_name)
             
        self.ae.plot_loss(self.history.history, os.path.join(self.res_path, 'ae_loss.png'))
        self.assertTrue(os.path.isfile(file_name))
          
    def test_plot_encoding(self):
        '''
        Tests if encoding results is plot to ae_encoding.png
        '''
        file_name = os.path.join(self.res_path, 'ae_encoding.png')
             
        if os.path.isfile(file_name):
            os.remove(file_name)
          
        encoded_fts = self.ae.encoder.predict(self.x_test)
        decoded_fts = self.ae.decoder.predict(encoded_fts)
             
        self.ae.plot_encoding(self.x_test, encoded_fts, decoded_fts, 
                              os.path.join(self.res_path, 'ae_encoding.png'))
        self.assertTrue(os.path.isfile(file_name))
          
    def test_plot_spatial_distribution(self):
        '''
        Tests if LDA, TSNE and PCA results are plot to ae_distribution.png
        '''
        file_name = os.path.join(self.res_path, 'ae_distribution.png')
             
        if os.path.isfile(file_name):
            os.remove(file_name)
              
        encoded_fts = self.ae.encoder.predict(self.x_test)
        decoded_fts = self.ae.decoder.predict(encoded_fts)
             
        self.ae.plot_spatial_distribution(self.x_test, encoded_fts, decoded_fts, 
                                          self.y_test, os.path.join(self.res_path, 'ae_distribution.png'))
        self.assertTrue(os.path.isfile(file_name))
          
    def test_plot_pca_vs_encoding(self):
        '''
        Tests if PCA components and encoding components are plot to ae_components.png
        '''
        file_name = os.path.join(self.res_path, 'ae_components.png')
             
        if os.path.isfile(file_name):
            os.remove(file_name)
              
        encoded_fts = self.ae.encoder.predict(self.x_test)
             
        self.ae.plot_pca_vs_encoding(self.x_test, encoded_fts, os.path.join(self.res_path, 'ae_components.png'))
        self.assertTrue(os.path.isfile(file_name))