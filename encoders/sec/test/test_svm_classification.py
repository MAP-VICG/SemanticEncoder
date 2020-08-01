import unittest
import numpy as np
from scipy.io import loadmat
from ..src.svm_classification import SVMClassifier, DataType


class ClassificationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.svm_cub = SVMClassifier(DataType.CUB)
        cls.svm_awa = SVMClassifier(DataType.AWA)

    def test_get_te_sem_data_awa(self):
        sem_data = self.svm_awa.get_te_sem_data(loadmat('../../Datasets/SAE/awa_demo_data.mat'))
        self.assertEqual((6180, 85), sem_data.shape)
        self.assertEqual(94.6, np.max(sem_data))
        self.assertEqual(0.0, np.min(sem_data))
        self.assertEqual(21.63002965924234, np.mean(sem_data))

    def test_get_te_sem_data_awa_resnet(self):
        sem_data = self.svm_awa.get_te_sem_data(loadmat('../../Datasets/SAE/awa_demo_data_resnet.mat'))
        self.assertEqual((6985, 85), sem_data.shape)
        self.assertEqual(94.6, np.max(sem_data))
        self.assertEqual(0.0, np.min(sem_data))
        self.assertEqual(21.353158836161526, np.mean(sem_data))

    def test_get_te_sem_data_cub_resnet(self):
        sem_data = self.svm_cub.get_te_sem_data(loadmat('../../Datasets/SAE/cub_demo_data_resnet.mat'))
        self.assertEqual((2933, 312), sem_data.shape)
        self.assertEqual(100.0, np.max(sem_data))
        self.assertEqual(0.0, np.min(sem_data))
        self.assertEqual(11.275272524447784, np.mean(sem_data))

    def test_get_te_sem_data_cub(self):
        sem_data = self.svm_cub.get_te_sem_data(loadmat('../../Datasets/SAE/cub_demo_data.mat'))
        self.assertEqual((2933, 312), sem_data.shape)
        self.assertEqual(100.0, np.max(sem_data))
        self.assertEqual(0.0, np.min(sem_data))
        self.assertEqual(11.275272524447782, np.mean(sem_data))

    def test_get_data_awa(self):
        vis_data, lbs_data, sem_data = self.svm_awa.get_data('../../Datasets/SAE/awa_demo_data.mat')
        self.assertEqual((30475, 1024), vis_data.shape)
        self.assertEqual((30475, 1), lbs_data.shape)
        self.assertEqual((30475, 85), sem_data.shape)
        self.assertEqual(24.086204528808594, np.max(vis_data))
        self.assertEqual(50, np.max(lbs_data))
        self.assertEqual(100.0, np.max(sem_data))
        self.assertEqual(0.0, np.min(vis_data))
        self.assertEqual(1, np.min(lbs_data))
        self.assertEqual(0.0, np.min(sem_data))
        self.assertEqual(0.6763227841658257, np.mean(vis_data))
        self.assertEqual(26.237309269893355, np.mean(lbs_data))
        self.assertEqual(20.947125740481585, np.mean(sem_data))

    def test_get_data_awa_resnet(self):
        vis_data, lbs_data, sem_data = self.svm_awa.get_data('../../Datasets/SAE/awa_demo_data_resnet.mat')
        self.assertEqual((37322, 2048), vis_data.shape)
        self.assertEqual((37322, 1), lbs_data.shape)
        self.assertEqual((37322, 85), sem_data.shape)
        self.assertEqual(30.294254, np.max(vis_data))
        self.assertEqual(50, np.max(lbs_data))
        self.assertEqual(100.0, np.max(sem_data))
        self.assertEqual(0.0, np.min(vis_data))
        self.assertEqual(1, np.min(lbs_data))
        self.assertEqual(-1.0, np.min(sem_data))
        self.assertEqual(0.4315834104428318, np.mean(vis_data))
        self.assertEqual(26.472670274904882, np.mean(lbs_data))
        self.assertEqual(20.950078502822805, np.mean(sem_data))

    def test_get_data_cub(self):
        vis_data, lbs_data, sem_data = self.svm_cub.get_data('../../Datasets/SAE/cub_demo_data.mat')
        self.assertEqual((11788, 1024), vis_data.shape)
        self.assertEqual((11788, 1), lbs_data.shape)
        self.assertEqual((11788, 312), sem_data.shape)
        self.assertEqual(12.171259880065918, np.max(vis_data))
        self.assertEqual(200, np.max(lbs_data))
        self.assertEqual(100.0, np.max(sem_data))
        self.assertEqual(0.0, np.min(vis_data))
        self.assertEqual(1, np.min(lbs_data))
        self.assertEqual(0.0, np.min(sem_data))
        self.assertEqual(0.4448367105499011, np.mean(vis_data))
        self.assertEqual(101.12631489650492, np.mean(lbs_data))
        self.assertEqual(2.8263371728213316, np.mean(sem_data))

    def test_get_data_cub_resnet(self):
        vis_data, lbs_data, sem_data = self.svm_cub.get_data('../../Datasets/SAE/cub_demo_data_resnet.mat')
        self.assertEqual((11788, 2048), vis_data.shape)
        self.assertEqual((11788, 1), lbs_data.shape)
        self.assertEqual((11788, 312), sem_data.shape)
        self.assertEqual(26.996128, np.max(vis_data))
        self.assertEqual(200, np.max(lbs_data))
        self.assertEqual(100.0, np.max(sem_data))
        self.assertEqual(0.0, np.min(vis_data))
        self.assertEqual(1, np.min(lbs_data))
        self.assertEqual(0.0, np.min(sem_data))
        self.assertEqual(0.37599693160995384, np.mean(vis_data))
        self.assertEqual(101.12631489650492, np.mean(lbs_data))
        self.assertEqual(11.389787361488784, np.mean(sem_data))

    def test_classify_vis_data(self):
        vis_data, lbs_data, _ = self.svm_cub.get_data('../../Datasets/SAE/cub_demo_data.mat')
        accuracies = self.svm_cub.classify_vis_data(vis_data, lbs_data, 2, True)

        for acc in accuracies:
            self.assertTrue(0 < acc < 1)
        self.assertEqual(2, len(accuracies))

    def test_classify_sem_data(self):
        _, lbs_data, sem_data = self.svm_cub.get_data('../../Datasets/SAE/cub_demo_data.mat')
        accuracies = self.svm_cub.classify_sem_data(sem_data, lbs_data, 2)

        for acc in accuracies:
            self.assertTrue(0 <= acc <= 1)
        self.assertEqual(2, len(accuracies))

    def test_classify_concat_data(self):
        vis_data, lbs_data, sem_data = self.svm_cub.get_data('../../Datasets/SAE/cub_demo_data.mat')
        accuracies = self.svm_cub.classify_concat_data(vis_data, sem_data, lbs_data, 2)

        for acc in accuracies:
            self.assertTrue(0 <= acc <= 1)
        self.assertEqual(2, len(accuracies))
