"""
Tests for module configparser

@author: Damares Resende
@contact: damaresresende@usp.br
@since: Nov 17, 2019

@organization: University of Sao Paulo (USP)
    Institute of Mathematics and Computer Science (ICMC) 
    Laboratory of Visualization, Imaging and Computer Graphics (VICG)
"""
import os
import unittest

from utils.src.configparser import ConfigParser


class ConfigParserTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """
        Initializes parser for all tests
        """
        configfile = os.sep.join(['mockfiles', 'configfiles', 'config.xml'])
        cls.parser = ConfigParser(configfile)
        cls.parser.read_configuration()
        
    def test_init_parser_invalid_file(self):
        """
        Tests is ValueError exception is raised when XML file is invalid
        """
        self.assertRaises(ValueError, ConfigParser, os.getcwd())
        
    def test_console_flag(self):
        """
        Tests if the correct console value was found
        """
        self.assertTrue(self.parser.console)
        
    def test_num_epochs(self):
        """
        Tests if the correct number of epochs value was found
        """
        self.assertEqual(5, self.parser.epochs)

    def test_noise_factor(self):
        """
        Tests if the correct noise factor value was found
        """
        self.assertEqual(0.1, self.parser.ae_noise_factor)
        
    def test_encoding_size(self):
        """
        Tests if the correct encoding size value was found
        """
        self.assertEqual(128, self.parser.encoding_size)
        
    def test_noise_rate(self):
        """
        Tests if the correct noise rate value was found
        """
        self.assertEqual(0.15, self.parser.noise_rate)
        
    def test_results_path(self):
        """
        Tests if the correct results path value was found
        """
        self.assertEqual('_files/results/', self.parser.results_path)
        
    def test_features_path(self):
        """
        Tests if the correct features path value was found
        """
        self.assertEqual('_files/mockfiles/awa2features/', self.parser.features_path)

    def test_x_train_path(self):
        """
        Tests if the correct features path value was found
        """
        self.assertEqual('../Datasets/Birds/features/birds_x_train.txt', self.parser.x_train_path)

    def test_y_train_path(self):
        """
        Tests if the correct features path value was found
        """
        self.assertEqual('../Datasets/Birds/features/birds_y_train.txt', self.parser.y_train_path)

    def test_x_test_path(self):
        """
        Tests if the correct features path value was found
        """
        self.assertEqual('../Datasets/Birds/features/birds_x_test.txt', self.parser.x_test_path)

    def test_y_test_path(self):
        """
        Tests if the correct features path value was found
        """
        self.assertEqual('../Datasets/Birds/features/birds_y_test.txt', self.parser.y_test_path)
        
    def test_node_not_found(self):
        """
        Tests if AttributeError exception is raised when node was not found in XML
        """
        configfile = os.sep.join(['mockfiles', 'configfiles', 'config_node_err.xml'])
        parser = ConfigParser(configfile)
         
        self.assertRaises(AttributeError, parser.read_configuration)
             
    def test_invalid_noise_rate_less(self):
        """
        Tests if ValueError exception is raised when noise rate is less than 0
        """
        configfile = os.sep.join(['mockfiles', 'configfiles', 'config_inv_rate_le.xml'])
        parser = ConfigParser(configfile)
         
        self.assertRaises(ValueError, parser.read_configuration)
 
    def test_invalid_noise_rate_greater(self):
        """
        Tests if ValueError exception is raised when noise rate is greater than 1
        """
        configfile = os.sep.join(['mockfiles', 'configfiles', 'config_inv_rate_gt.xml'])
        parser = ConfigParser(configfile)
         
        self.assertRaises(ValueError, parser.read_configuration)

    def test_chosen_classes(self):
        """
        Tests if the correct chosen_classes value was found
        """
        self.assertEqual([50, 9, 7, 31, 38], self.parser.chosen_classes)

    def test_classes_names(self):
        """
        Tests if the correct classes_names value was found
        """
        self.assertEqual(['dolphin', 'blue+whale', 'horse', 'giraffe', 'zebra'], self.parser.classes_names)
