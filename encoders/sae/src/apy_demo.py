"""
Contains demo for running SAE (Semantic Auto-encoder) for aPascal&Yahoo dataset. This approach was proposed by
Elyor Kodirov, Tao Xiang, and Shaogang Gong in the paper "Semantic Autoencoder for Zero-shot Learning"
published in CVPR 2017. Code originally written in Matlab and is here transformed to Python.

@author: Damares Resende
@contact: damaresresende@usp.br
@since: Nov 2, 2020

@organization: University of Sao Paulo (USP)
    Institute of Mathematics and Computer Science (ICMC)
    Laboratory of Visualization, Imaging and Computer Graphics (VICG)
"""
import numpy as np
from scipy.io import loadmat
from sklearn.preprocessing import normalize

from encoders.tools.src.utils import ZSL


class APY:
    def __init__(self, data_path):
        """
        Defines parameters, loads data and computes weights using SAE

        :param data_path: string with path with .mat file with data set
        """
        self.hit_k = 3
        self.lambda_ = 0
        self.z_score = False
        self.s_tr = None
        self.w = None

        self.data = loadmat(data_path)
        tr_mask = [False if img.startswith('Yahoo') else True for img in self.data['img_list']]
        te_mask = [True if img.startswith('Yahoo') else False for img in self.data['img_list']]

        self.temp_labels = self.data['img_class'][:, te_mask].transpose()
        self.test_labels = self.data['img_class'][:, te_mask].transpose()

        self.x_tr = self._normalize(self.data['vis_fts'][tr_mask, :].transpose()).transpose()
        self.x_te = np.array(self.data['vis_fts'][te_mask, :])
        self.data['S_tr'] = self.data['sem_fts'][tr_mask, :].astype(np.float64)
        self.data['S_te'] = self.data['sem_fts'][te_mask, :].astype(np.float64)
        self.data['S_te_pro'] = self.data['prototypes'][te_mask, :].astype(np.float64)

    def reset_weights(self):
        """
        Set w to None so it can be computed before calculating the feature space projection

        :return: None
        """
        self.w = None

    def set_semantic_data(self, sem_data=None):
        """
        Replaces the default semantic data by the given array if it has similar shape with the original one

        :param sem_data: array of shape (6340, 64)
        :return: None
        """
        if self.s_tr is None and sem_data is None:
            self.s_tr = self.data['S_tr']
        elif sem_data is not None:
            if sem_data.shape == (6340, 64):
                self.s_tr = sem_data
            else:
                raise ValueError('Data provided is invalid. It should be of shape (6340, 64)')

    def _compute_weights(self):
        """
        Computes the weights that estimates the latent space using SAE

        :return: a 2D numpy array with the matrix of weights computed
        """
        return ZSL.sae(self.x_tr.transpose(), self.s_tr.transpose(), self.lambda_).transpose()

    @staticmethod
    def _normalize(data):
        """
        Wrapper function to normalize data. Normalized data is copied into another object so values of original data
        are not changed.

        :param data: 2D numpy array with data to be normalized
        :return: normalized data
        """
        return normalize(data, norm='l2', axis=1, copy=True)

    def v2s_projection(self):
        """
        Applies zero shot learning in the estimated data, classifies each test sample with the class of the closest
        neighbor and computes the accuracy of classification comparing the estimated class with the one stated in the
        template array. The projection goes from the feature space (visual features extracted from a CNN) to the
        semantic space.

        :return: float number with the accuracy of the ZSL classification
        """
        if self.w is None:
            self.w = self._compute_weights().transpose()

        s_est = self.x_te.dot(self._normalize(self.w).transpose())
        s_te_gt = self._normalize(self.data['S_te_pro'].transpose()).transpose()
        acc, _ = ZSL.zsl_el(s_est, s_te_gt, self.test_labels, self.temp_labels, self.hit_k, self.z_score)
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
            self.w = self._compute_weights().transpose()

        x_te_pro = self._normalize(self.data['S_te_pro'].transpose()).transpose().dot(self._normalize(self.w))
        x_te_pro = self._normalize(x_te_pro.transpose()).transpose()
        acc, _ = ZSL.zsl_el(self.x_te, x_te_pro, self.test_labels, self.temp_labels, self.hit_k, self.z_score)
        return acc


if __name__ == '__main__':
    apy = APY('../../../../Datasets/apy_data_inceptionv3.mat')
    apy.set_semantic_data()
    print('\n[1] aP&Y ZSL accuracy [V >>> S]: %.1f%%\n' % (apy.v2s_projection() * 100))
    print('[2] aP&Y ZSL accuracy [S >>> V]: %.1f%%\n' % (apy.s2v_projection() * 100))
