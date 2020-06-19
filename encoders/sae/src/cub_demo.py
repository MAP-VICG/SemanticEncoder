"""
Contains demo for running SAE (Semantic Auto-encoder) for CUB200 dataset. This approach was proposed by
Elyor Kodirov, Tao Xiang, and Shaogang Gong in the paper "Semantic Autoencoder for Zero-shot Learning"
published in CVPR 2017. Code originally written in Matlab and is here transformed to Python.

@author: Damares Resende
@contact: damaresresende@usp.br
@since: Apr 25, 2020

@organization: University of Sao Paulo (USP)
    Institute of Mathematics and Computer Science (ICMC)
    Laboratory of Visualization, Imaging and Computer Graphics (VICG)
"""
import numpy as np
from scipy.io import loadmat
from sklearn.preprocessing import normalize

from encoders.tools.src.utils import ZSL


class CUB200:
    def __init__(self, data_path):
        """
        Defines parameters, loads data and computes weights using SAE

        :param data_path: string with path with .mat file with data set
        """
        self.hit_k = 1
        self.lambda_ = .2
        self.z_score = True
        self.s_tr = None
        self.w = None

        self.data = loadmat(data_path)
        self.temp_labels = np.array([int(x) for x in self.data['te_cl_id']])
        self.test_labels = np.array([int(x) for x in self.data['test_labels_cub']])

        labels = list(map(int, self.data['train_labels_cub']))
        self.x_tr, self.x_te = ZSL.dimension_reduction(self.data['X_tr'], self.data['X_te'], labels)

    def reset_weights(self):
        """
        Set w to None so it can be computed before calculating the feature space projection

        :return: None
        """
        self.w = None

    def set_semantic_data(self, sem_data=None):
        """
        Replaces the default semantic data by the given array if it has similar shape with the original one

        :param sem_data: array of shape (8855, 312)
        :return: None
        """
        if self.s_tr is None and sem_data is None:
            self.s_tr = self.data['S_tr']
        elif sem_data is not None:
            if sem_data.shape == (8855, 312):
                self.s_tr = sem_data
            else:
                raise ValueError('Data provided is invalid. It should be of shape (8855, 312)')

    def _compute_weights(self):
        """
        Computes the weights that estimates the latent space using SAE

        :return: a 2D numpy array with the matrix of weights computed
        """
        s_tr = normalize(self.s_tr, norm='l2', axis=1, copy=False)
        return ZSL.sae(self.x_tr.transpose(), s_tr.transpose(), self.lambda_).transpose()

    def v2s_projection(self):
        """
        Applies zero shot learning in the estimated data, classifies each test sample with the class of the closest
        neighbor and computes the accuracy of classification comparing the estimated class with the one stated in the
        template array. The projection goes from the feature space (visual features extracted from a CNN) to the
        semantic space.

        :return: float number with the accuracy of the ZSL classification
        """
        if self.w is None:
            self.w = self._compute_weights()

        s_est = self.x_te.dot(self.w)
        acc, _ = ZSL.zsl_el(s_est, self.data['S_te_pro'], self.test_labels, self.temp_labels, self.hit_k, self.z_score)
        return acc

    def s2v_projection(self):
        """
        Applies zero shot learning in the estimated data, classifies each test sample with the class of the closest
        neighbor and computes the accuracy of classification comparing the estimated class with the one stated in the
        template array. The projection goes from the semantic space to the feature space (visual features extracted
        from a CNN).

        :return: float number with the accuracy of the ZSL classification
        """
        if self.w is None:
            self.w = self._compute_weights()

        x_te_pro = self.data['S_te_pro'].dot(self.w.transpose())
        acc, _ = ZSL.zsl_el(self.x_te, x_te_pro, self.test_labels, self.temp_labels, self.hit_k, self.z_score)
        return acc


if __name__ == '__main__':
    cub = CUB200('../../../../Datasets/SAE/cub_demo_data.mat')
    cub.set_semantic_data()
    print('\n[1] CUB ZSL accuracy [V >>> S]: %.1f%%\n' % (cub.v2s_projection() * 100))
    print('[2] CUB ZSL accuracy [S >>> V]: %.1f%%\n' % (cub.s2v_projection() * 100))
