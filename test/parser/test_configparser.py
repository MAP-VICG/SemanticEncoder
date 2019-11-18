'''
Tests for module configparser

@author: Damares Resende
@contact: damaresresende@usp.br
@since: Nov 17, 2019

@organization: University of Sao Paulo (USP)
    Institute of Mathematics and Computer Science (ICMC) 
    Laboratory of Visualization, Imaging and Computer Graphics (VICG)
'''
import os
import unittest

from src.parser.configparser import ConfigParser, AttributesType


class ConfigParsertTests(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        '''
        Initializes parser for all tests
        '''
        configfile = os.sep.join([os.getcwd().split('test')[0], 'test', '_mockfiles', 'config.xml'])
        cls.parser = ConfigParser(configfile)
        cls.parser.read_configuration()
        
    def test_init_parser_invalid_file(self):
        '''
        Tests is ValueError exception is raised when XML file is invalid
        '''
        self.assertRaises(ValueError, ConfigParser, os.getcwd())
        
    def test_mock_flag(self):
        '''
        Tests if the correct mock value was found
        '''
        self.assertTrue(self.parser.mock)
        
    def test_num_epochs(self):
        '''
        Tests if the correct number of epochs value was found
        '''
        self.assertEqual(5, self.parser.epochs)
        
    def test_encoding_size(self):
        '''
        Tests if the correct encoding size value was found
        '''
        self.assertEqual(128, self.parser.encoding_size)
        
    def test_noise_rate(self):
        '''
        Tests if the correct noise rate value was found
        '''
        self.assertEqual(0.15, self.parser.noise_rate)
    
    def test_attributes_type(self):
        '''
        Tests if the correct attributes type value was found
        '''
        self.assertEqual(AttributesType.CON, self.parser.attributes_type)
        
    def test_node_not_found(self):
        '''
        Tests if AttributeError exception is raised when node was not found in XML
        '''
        configfile = os.sep.join([os.getcwd().split('test')[0], 'test', '_mockfiles', 'config_node_err.xml'])
        parser = ConfigParser(configfile)
        
        self.assertRaises(AttributeError, parser.read_configuration)
            
    def test_invalid_noise_rate_less(self):
        '''
        Tests if ValueError exception is raised when noise rate is less than 0
        '''
        configfile = os.sep.join([os.getcwd().split('test')[0], 'test', '_mockfiles', 'config_inv_rate_le.xml'])
        parser = ConfigParser(configfile)
        
        self.assertRaises(ValueError, parser.read_configuration)

    def test_invalid_noise_rate_greater(self):
        '''
        Tests if ValueError exception is raised when noise rate is greater than 1
        '''
        configfile = os.sep.join([os.getcwd().split('test')[0], 'test', '_mockfiles', 'config_inv_rate_gt.xml'])
        parser = ConfigParser(configfile)
        
        self.assertRaises(ValueError, parser.read_configuration)

    def test_invalid_attribute_type(self):
        '''
        Tests if ValueError exception is raised when attribute type is not continuous, binary or indexed
        '''
        configfile = os.sep.join([os.getcwd().split('test')[0], 'test', '_mockfiles', 'config_inv_att.xml'])
        parser = ConfigParser(configfile)
        
        self.assertRaises(ValueError, parser.read_configuration)
        