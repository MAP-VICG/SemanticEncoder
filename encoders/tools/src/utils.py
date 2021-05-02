"""
Contains auxiliary functions to for SAE (Semantic Auto-encoder). This approach was proposed by
Elyor Kodirov, Tao Xiang, and Shaogang Gong in the paper "Semantic Autoencoder for Zero-shot Learning"
published in CVPR 2017. Code originally written in Matlab and is here transformed to Python.

@author: Damares Resende
@contact: damaresresende@usp.br
@since: Apr 21, 2020

@organization: University of Sao Paulo (USP)
    Institute of Mathematics and Computer Science (ICMC)
    Laboratory of Visualization, Imaging and Computer Graphics (VICG)
"""
import numpy as np
from scipy import stats
from scipy.stats import zscore
from numpy.linalg import matrix_power
from scipy.linalg import solve_sylvester
from scipy.spatial.distance import cdist


class ZSL:
    @staticmethod
    def sub2ind(shape, rows, cols):
        """
        Convert subscripts to linear indices by returning the linear indices corresponding to the row and column
        subscripts for a matrix of size m, n

        @param shape: shape of matrix (m, n)
        @param rows: array of row indexes
        @param cols: array of column indexes
        @return: list with linear indices for row and columns
        """
        rows = np.array(rows)
        cols = np.array(cols)
        ind = cols * shape[0] + rows
        return [int(value) for value in ind]

    @staticmethod
    def is_member(data):
        """
        Computes all available labels in the data set, and if the array of indexes that correspond
        to the index of the latest occurrence of each label.

        @param data: list of labels
        @return: tuple with list of indexes per label and unique labels
        """
        k = -1
        data_dict = dict()
        idx = np.zeros(len(data))

        for i, value in enumerate(data):
            if value not in data_dict.keys():
                k += 1
                data_dict[value] = k
            idx[i] = int(data_dict[value])

        return np.array(idx, dtype=int), np.array(list(data_dict.keys()), dtype=int)

    @staticmethod
    def label_matrix(labels):
        """
        Converts the label vector to label matrix.

        :param labels: 1xN, N is the number of samples.
        :return: Nxc matrix, where c is the number of classes.
        """
        indexes, unique_labels = ZSL.is_member(labels)
        rows = np.array(range(len(labels)), dtype=int)

        shape = (len(labels), len(unique_labels))
        lb_mat = np.array([0] * shape[0] * shape[1])
        lb_mat[ZSL.sub2ind(shape, rows, indexes)] = 1

        return np.reshape(lb_mat, (shape[1], shape[0]))

    @staticmethod
    def dimension_reduction(x_tr, x_te, labels):
        """
        Reduces the dimensionality of training and test data from (X, 1024) to (X, 150) by taking the main
        components of the data based on the given classification.

        @param x_tr: training data
        @param x_te: test data
        @param labels: data labels
        @return: tuple with training data and test data with 150 attributes only
        """
        m, n = x_tr.transpose().dot(x_tr).shape
        y = ZSL.label_matrix(labels).transpose()
        w = matrix_power(x_tr.transpose().dot(x_tr) + 50 * np.eye(m, n), -1).dot(x_tr.transpose()).dot(y)

        return x_tr.dot(w), x_te.dot(w)

    @staticmethod
    def sae(vis_data, sem_data, lambda_):
        """
        Computes the weight matrix that estimates the latent space of the Semantic Auto-encoder.

        @param vis_data: dxN data matrix
        @param sem_data: kxN semantic matrix
        @param lambda_: regularisation parameter
        @return: kxd projection matrix
        """
        a = sem_data.dot(sem_data.transpose())
        b = lambda_ * vis_data.dot(vis_data.transpose())
        c = (1 + lambda_) * sem_data.dot(vis_data.transpose())

        return solve_sylvester(a, b, c)

    @staticmethod
    def zsl_el(s_est, s_temp, test_labels, temp_labels, hit_k, z_score=False):
        """
        Compute distance between each sample estimated and the samples in the given template,
        then compares the estimated class with it's true value and computes the classification
        accuracy for the whole set.

        :param s_est: estimated semantic data
        :param s_temp: semantic data template
        :param test_labels: data true classification
        :param temp_labels: template labels
        :param hit_k: number of close neighbors to take into account
        :param z_score: if true, computes zscore of distance vector
        :return: tuple with classification accuracy and hit_k distance
        """
        dist = 1 - (cdist(s_est, s_temp, metric='cosine'))
        y_hit_k = np.zeros((dist.shape[0], hit_k))

        if z_score:
            dist = zscore(dist)

        for i in range(dist.shape[0]):
            prx = np.argsort(dist[i, :])
            prx = [prx[x] for x in range(len(prx) - 1, 0, -1)]
            y_hit_k[i, :] = stats.mode(temp_labels[prx[0:hit_k]]).mode[0]

        n = 0
        for i in range(dist.shape[0]):
            if test_labels[i] in y_hit_k[i, :]:
                n += 1
        zsl_accuracy = n / dist.shape[0]

        return zsl_accuracy, y_hit_k
