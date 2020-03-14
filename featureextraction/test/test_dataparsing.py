"""
Tests for module dataparsing

@author: Damares Resende
@contact: damaresresende@usp.br
@since: Jan 5, 2020

@organization: University of Sao Paulo (USP)
    Institute of Mathematics and Computer Science (ICMC)
    Laboratory of Visualization, Imaging and Computer Graphics (VICG)
"""
import unittest
import numpy as np
from os import path, remove
from featureextraction.src.dataparsing import CUB200Data, AWA2Data, DataIO


class AWA2DataTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """
        Initializes variables to be used in the tests
        """
        cls.base_path = path.join('mockfiles', 'AWA2')
        cls.data = AWA2Data(cls.base_path)

    def test_get_semantic_attributes(self):
        """
        Tests if the shape of the numpy array returned is the expected one
        """
        sem_fts = self.data.get_semantic_attributes()
        self.assertEqual((50, 85), sem_fts.shape)

    def test_get_images_list(self):
        """
        Tests if images listed in the files were read in the correct format and order
        """
        images = self.data.get_images_list()
        self.assertEqual(30, len(images))
        self.assertEqual('antelope/antelope_10002.jpg', images[0])
        self.assertEqual('gorilla/gorilla_10037.jpg', images[14])
        self.assertEqual('wolf/wolf_10094.jpg', images[29])

    def test_get_images_class(self):
        """
        Tests if the id of the class returned is correct
        """
        for i, klass in enumerate(self.data.get_images_class()):
            if i == 0:
                self.assertEqual(1, klass)
            elif i == 14:
                self.assertEqual(20, klass)
            elif i == 29:
                self.assertEqual(32, klass)

    def test_build_birds_data(self):
        """
        Tests if shape of returned arrays and number of images per set is correct
        """
        train_fts, test_fts, train_class, test_class = self.data.build_data()
        self.assertEqual((20, 2133), train_fts.shape)
        self.assertEqual((10, 2133), test_fts.shape)
        self.assertEqual(20, len(train_class))
        self.assertEqual(10, len(test_fts))


class CUB200DataTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """
        Initializes variables to be used in the tests
        """
        cls.base_path = path.join('mockfiles', 'CUB200')
        cls.data = CUB200Data(cls.base_path)

    def test_get_images_list(self):
        """
        Tests if images listed in the files were read in the correct format and order
        """
        images = self.data.get_images_list()
        self.assertEqual(30, len(images))
        self.assertEqual('013.Bobolink/Bobolink_0056_9080.jpg', images[0])
        self.assertEqual('112.Great_Grey_Shrike/Great_Grey_Shrike_0050_797012.jpg', images[14])
        self.assertEqual('200.Common_Yellowthroat/Common_Yellowthroat_0090_190503.jpg', images[29])

    def test_get_semantic_attributes(self):
        """
        Tests if the shape of the numpy array returned is the expected one
        """
        sem_fts = self.data.get_semantic_attributes()
        self.assertEqual((200, 312), sem_fts.shape)

    def test_get_visual_attributes(self):
        """
        Tests if the shape of the numpy array returned is the expected one
        """
        self.assertEqual((30, 2048), self.data.get_visual_attributes(self.data.get_images_list()).shape)

    def test_get_train_test_masks(self):
        """
        Tests if the shape of the returned mask is the expected one and if the number of images is correct
        """
        mask = self.data._get_train_test_mask()
        self.assertEqual(30, len(mask))
        self.assertEqual(11, sum(np.ones(30)[mask]))
        self.assertEqual(19, sum(np.ones(30)[mask == False]))

    def test_get_images_class(self):
        """
        Tests if the id of the class returned is correct
        """
        for i, klass in enumerate(self.data.get_images_class()):
            if i == 0:
                self.assertEqual(13, klass)
            elif i == 14:
                self.assertEqual(112, klass)
            elif i == 29:
                self.assertEqual(200, klass)

    def test_build_birds_data(self):
        """
        Tests if shape of returned arrays and number of images per set is correct
        """
        train_fts, test_fts, train_class, test_class = self.data.build_data()
        self.assertEqual((11, 2360), train_fts.shape)
        self.assertEqual((19, 2360), test_fts.shape)
        self.assertEqual(11, len(train_class))
        self.assertEqual(19, len(test_fts))


class DataIOTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """
        Initializes variables to be used in the tests
        """
        cls.base_path = path.join('mockfiles', 'CUB200')
        cls.data = CUB200Data(cls.base_path)
        train_fts, test_fts, train_class, test_class = cls.data.build_data()
        DataIO.save_files(cls.base_path, train_fts, train_class, test_fts, test_class, 'CUB200')

    def test_get_features(self):
        """
        Tests if data retrieved from data file is in the correct format and shape
        """
        data = DataIO.get_features(path.join(self.base_path, 'CUB200_x_test.txt'))
        self.assertEqual((19, 2360), data.shape)
        self.assertTrue(isinstance(data[0, 0], float))

    def test_get_labels(self):
        """
        Tests if data retrieved from labels file is in the correct format and shape
        """
        labels = DataIO.get_labels(path.join(self.base_path, 'CUB200_y_test.txt'))
        self.assertEqual((19,), labels.shape)
        self.assertTrue(isinstance(labels[0], np.int64))

    def test_save_files(self):
        """
        Tests if files with data set data are saved
        """
        train_fts, test_fts, train_class, test_class = self.data.build_data()
        DataIO.save_files(self.base_path, train_fts, train_class, test_fts, test_class, 'CUB200')

        self.assertTrue(path.isfile(path.join(self.base_path, 'CUB200_x_train.txt')))
        self.assertTrue(path.isfile(path.join(self.base_path, 'CUB200_y_train.txt')))
        self.assertTrue(path.isfile(path.join(self.base_path, 'CUB200_x_test.txt')))
        self.assertTrue(path.isfile(path.join(self.base_path, 'CUB200_y_test.txt')))

    @classmethod
    def tearDownClass(cls):
        """
        Deletes files that were written by the tests
        """
        if path.isfile(path.join(cls.base_path, 'CUB200_x_train.txt')):
            remove(path.join(cls.base_path, 'CUB200_x_train.txt'))

        if path.isfile(path.join(cls.base_path, 'CUB200_y_train.txt')):
            remove(path.join(cls.base_path, 'CUB200_y_train.txt'))

        if path.isfile(path.join(cls.base_path, 'CUB200_x_test.txt')):
            remove(path.join(cls.base_path, 'CUB200_x_test.txt'))

        if path.isfile(path.join(cls.base_path, 'CUB200_y_test.txt')):
            remove(path.join(cls.base_path, 'CUB200_y_test.txt'))
