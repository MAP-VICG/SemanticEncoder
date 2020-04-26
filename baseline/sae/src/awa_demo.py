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

from baseline.sae.src.utils import ZSL


class AWA:
    def __init__(self, data_path):
        """
        Defines parameters, loads data and computes weights using SAE

        :param data_path: string with path with .mat file with data set
        """
        self.hit_k = 1
        self.lambda_ = 500000
        self.z_score = False

        self.data = loadmat(data_path)
        self.temp_labels = np.array([int(x) for x in self.data['param']['testclasses_id'][0][0]])
        self.test_labels = np.array([int(x) for x in self.data['param']['test_labels'][0][0]])

        self.x_tr = self._normalize(self.data['X_tr'].transpose()).transpose()
        self.x_te = np.array(self.data['X_te'])
        self.w = self._compute_weights().transpose()

    def _compute_weights(self):
        """
        Computes the weights that estimates the latent space using SAE

        :return: a 2D numpy array with the matrix of weights computed
        """
        return ZSL.sae(self.x_tr.transpose(), self.data['S_tr'].transpose(), self.lambda_).transpose()

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
        s_est = self.x_te.dot(self._normalize(self.w).transpose())
        s_te_gt = self._normalize(self.data['S_te_gt'].transpose()).transpose()
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
        x_te_pro = self._normalize(self.data['S_te_pro'].transpose()).transpose().dot(self._normalize(self.w))
        x_te_pro = self._normalize(x_te_pro.transpose()).transpose()
        acc, _ = ZSL.zsl_el(self.x_te, x_te_pro, self.test_labels, self.temp_labels, self.hit_k, self.z_score)
        return acc


if __name__ == '__main__':
    awa = AWA('../../../../Datasets/SAE/awa_demo_data.mat')
    print('\n[1] AwA ZSL accuracy [V >>> S]: %.1f%%\n' % (awa.v2s_projection() * 100))
    print('[2] AwA ZSL accuracy [S >>> V]: %.1f%%\n' % (awa.s2v_projection() * 100))
