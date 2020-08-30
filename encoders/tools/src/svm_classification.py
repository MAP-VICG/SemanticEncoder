import os
import numpy as np
from enum import Enum
from scipy.io import loadmat

from sklearn.svm import SVC
from sklearn.decomposition import PCA
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import normalize
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import StratifiedKFold
from sklearn.metrics import balanced_accuracy_score

from encoders.tools.src.utils import ZSL
from encoders.sec.src.encoder import Encoder
from encoders.tools.src.sem_degradation import SemanticDegradation


class DataType(Enum):
    CUB = "CUB"
    AWA = "AWA"


class SVMClassifier:
    def __init__(self, data_type, ae_type, folds, epochs, degradation_rate=0.0):
        if type(data_type) != DataType:
            raise ValueError("Invalid data type.")

        self.data_type = data_type
        if self.data_type == DataType.AWA:
            self.lambda_ = 500000
        elif self.data_type == DataType.CUB:
            self.lambda_ = .2

        self.n_folds = folds
        self.epochs = epochs
        self.ae_type = ae_type
        self.degradation_rate = degradation_rate

    def get_te_sem_data(self, data):
        if self.data_type == DataType.AWA:
            lbs = {data['param']['testclasses_id'][0][0][i][0]: attrs for i, attrs in enumerate(data['S_te_pro'])}
            return np.array([lbs[label[0]] for label in data['param']['test_labels'][0][0]])
        elif self.data_type == DataType.CUB:
            lbs = {data['te_cl_id'][i][0]: attributes for i, attributes in enumerate(data['S_te_pro'])}
            return np.array([lbs[label[0]] for label in data['test_labels_cub']])
        else:
            raise ValueError("Invalid data type.")

    def get_data(self, data_path):
        data = loadmat(data_path)
        vis_data = np.vstack((data['X_tr'], data['X_te']))
        sem_data = np.vstack((data['S_tr'], self.get_te_sem_data(data)))

        if self.data_type == DataType.AWA:
            lbs_data = np.vstack((data['param']['train_labels'][0][0], data['param']['test_labels'][0][0]))
        elif self.data_type == DataType.CUB:
            lbs_data = np.vstack((data['train_labels_cub'], data['test_labels_cub']))
        else:
            raise ValueError("Invalid data type.")

        return vis_data, lbs_data, sem_data

    def classify_vis_data(self, vis_data, labels, reduce_dim=False):
        accuracies = []
        skf = StratifiedKFold(n_splits=self.n_folds, random_state=None, shuffle=True)

        for train_index, test_index in skf.split(vis_data, labels):
            tr_data, te_data = vis_data[train_index], vis_data[test_index]
            tr_labels, te_labels = labels[train_index][:, 0], labels[test_index][:, 0]

            if reduce_dim:
                tr_data, te_data = ZSL.dimension_reduction(tr_data, te_data, list(tr_labels))

            clf = make_pipeline(StandardScaler(), SVC(gamma='auto', C=1.0, kernel='linear'))
            clf.fit(tr_data, tr_labels)
            prediction = clf.predict(te_data)

            accuracies.append(balanced_accuracy_score(te_labels, prediction))

        return accuracies

    def classify_sem_data(self, sem_data, labels):
        accuracies = []
        skf = StratifiedKFold(n_splits=self.n_folds, random_state=None, shuffle=True)

        for train_index, test_index in skf.split(sem_data, labels):
            tr_data = normalize(sem_data[train_index], norm='l2', axis=1, copy=True)

            te_data = normalize(sem_data[test_index], norm='l2', axis=1, copy=True)
            te_data = SemanticDegradation.kill_semantic_attributes(te_data, self.degradation_rate)
            te_data = normalize(te_data, norm='l2', axis=1, copy=True)

            tr_labels, te_labels = labels[train_index][:, 0], labels[test_index][:, 0]

            clf = make_pipeline(StandardScaler(), SVC(gamma='auto', C=1.0, kernel='linear'))
            clf.fit(tr_data, tr_labels)
            prediction = clf.predict(te_data)

            accuracies.append(balanced_accuracy_score(te_labels, prediction))

        return accuracies

    def classify_concat_data(self, vis_data, sem_data, labels):
        accuracies = []
        skf = StratifiedKFold(n_splits=self.n_folds, random_state=None, shuffle=True)

        for train_index, test_index in skf.split(vis_data, labels):
            tr_vis, te_vis = vis_data[train_index], vis_data[test_index]
            tr_sem = normalize(sem_data[train_index], norm='l2', axis=1, copy=True)

            te_sem = normalize(sem_data[test_index], norm='l2', axis=1, copy=True)
            te_sem = SemanticDegradation.kill_semantic_attributes(te_sem, self.degradation_rate)
            te_sem = normalize(te_sem, norm='l2', axis=1, copy=True)

            tr_data, te_data = np.hstack((tr_vis, tr_sem)), np.hstack((te_vis, te_sem))
            tr_labels, te_labels = labels[train_index][:, 0], labels[test_index][:, 0]

            clf = make_pipeline(StandardScaler(), SVC(gamma='auto', C=1.0, kernel='linear'))
            clf.fit(tr_data, tr_labels)
            prediction = clf.predict(te_data)

            accuracies.append(balanced_accuracy_score(te_labels, prediction))

        return accuracies

    def classify_concat_pca_data(self, vis_data, sem_data, labels):
        accuracies = []
        pca = PCA(n_components=sem_data.shape[1])
        skf = StratifiedKFold(n_splits=self.n_folds, random_state=None, shuffle=True)

        for train_index, test_index in skf.split(vis_data, labels):
            tr_vis, te_vis = vis_data[train_index], vis_data[test_index]
            tr_sem = normalize(sem_data[train_index], norm='l2', axis=1, copy=True)

            te_sem = normalize(sem_data[test_index], norm='l2', axis=1, copy=True)
            te_sem = SemanticDegradation.kill_semantic_attributes(te_sem, self.degradation_rate)
            te_sem = normalize(te_sem, norm='l2', axis=1, copy=True)

            tr_data, te_data = np.hstack((tr_vis, tr_sem)), np.hstack((te_vis, te_sem))
            tr_labels, te_labels = labels[train_index][:, 0], labels[test_index][:, 0]

            clf = make_pipeline(StandardScaler(), SVC(gamma='auto', C=1.0, kernel='linear'))
            clf.fit(pca.fit_transform(tr_data), tr_labels)
            prediction = clf.predict(pca.fit_transform(te_data))

            accuracies.append(balanced_accuracy_score(te_labels, prediction))

        return accuracies

    def estimate_sae_data(self, tr_vis_data, te_vis_data, tr_sem_data, tr_labels):
        if self.data_type == DataType.CUB:
            tr_vis, te_vis = ZSL.dimension_reduction(tr_vis_data, te_vis_data, tr_labels)
            tr_sem = normalize(tr_sem_data, norm='l2', axis=1, copy=True)

            sae_w = ZSL.sae(tr_vis.transpose(), tr_sem.transpose(), self.lambda_).transpose()
            tr_sem, te_sem = tr_vis.dot(sae_w), te_vis.dot(sae_w)
        else:
            tr_vis = normalize(tr_vis_data.transpose(), norm='l2', axis=1, copy=True).transpose()
            sae_w = ZSL.sae(tr_vis.transpose(), tr_sem_data.transpose(), self.lambda_)

            tr_sem = tr_vis.dot(normalize(sae_w, norm='l2', axis=1, copy=True).transpose())
            te_sem = te_vis_data.dot(normalize(sae_w, norm='l2', axis=1, copy=True).transpose())

        return tr_sem, te_sem

    def classify_sae_data(self, vis_data, sem_data, labels):
        accuracies = []
        skf = StratifiedKFold(n_splits=self.n_folds, random_state=None, shuffle=True)

        for tr_idx, te_idx in skf.split(vis_data, labels):
            tr_labels, te_labels = labels[tr_idx][:, 0], labels[te_idx][:, 0]

            tr_sem, te_sem = self.estimate_sae_data(vis_data[tr_idx], vis_data[te_idx], sem_data[tr_idx], tr_labels)

            clf = make_pipeline(StandardScaler(), SVC(gamma='auto', C=1.0, kernel='linear'))
            clf.fit(tr_sem, tr_labels)
            prediction = clf.predict(te_sem)

            accuracies.append(balanced_accuracy_score(te_labels, prediction))

        return accuracies

    def estimate_sec_data(self, tr_vis_data, te_vis_data, tr_sem_data, te_sem_data, save_weights, res_path):
        tr_sem_data = normalize(tr_sem_data, norm='l2', axis=1, copy=True)
        tr_vis_data = normalize(tr_vis_data, norm='l2', axis=1, copy=True)
        te_vis_data = normalize(te_vis_data, norm='l2', axis=1, copy=True)

        te_sem_data = normalize(te_sem_data, norm='l2', axis=1, copy=True)
        te_sem_data = SemanticDegradation.kill_semantic_attributes(te_sem_data, self.degradation_rate)
        te_sem_data = normalize(te_sem_data, norm='l2', axis=1, copy=True)

        input_length = output_length = tr_vis_data.shape[1] + tr_sem_data.shape[1]
        ae = Encoder(input_length, tr_sem_data.shape[1], output_length, self.ae_type, self.epochs, res_path)
        tr_sem, te_sem = ae.estimate_semantic_data(tr_vis_data, te_vis_data, tr_sem_data, te_sem_data, save_weights)

        return tr_sem, te_sem

    def classify_sec_data(self, vis_data, sem_data, labels, save_results, results_path='.'):
        fold = 0
        accuracies = []
        skf = StratifiedKFold(n_splits=self.n_folds, random_state=None, shuffle=True)

        results_path = os.path.join(results_path, 'sec')
        if save_results and results_path != '.' and not os.path.isdir(results_path):
            os.mkdir(results_path)

        for tr_idx, te_idx in skf.split(vis_data, labels):
            tr_labels, te_labels = labels[tr_idx][:, 0], labels[te_idx][:, 0]

            res_path = os.path.join(results_path, 'f' + str(fold).zfill(3))
            tr_sem, te_sem = self.estimate_sec_data(vis_data[tr_idx], vis_data[te_idx], sem_data[tr_idx],
                                                    sem_data[te_idx], save_results, res_path)

            clf = make_pipeline(StandardScaler(), SVC(gamma='auto', C=1.0, kernel='linear'))
            clf.fit(tr_sem, tr_labels)
            prediction = clf.predict(te_sem)

            fold += 1
            accuracies.append(balanced_accuracy_score(te_labels, prediction))

        return accuracies

    def classify_sae2sec_data(self, vis_data, sem_data, labels, save_results, results_path='.'):
        fold = 0
        accuracies = []
        skf = StratifiedKFold(n_splits=self.n_folds, random_state=None, shuffle=True)

        results_path = os.path.join(results_path, 's2s')
        if save_results and results_path != '.' and not os.path.isdir(results_path):
            os.mkdir(results_path)

        for tr_idx, te_idx in skf.split(vis_data, labels):
            tr_vis, te_vis = vis_data[tr_idx], vis_data[te_idx]
            tr_labels, te_labels = labels[tr_idx][:, 0], labels[te_idx][:, 0]

            res_path = os.path.join(results_path, 'f' + str(fold).zfill(3))

            tr_sem, te_sem = self.estimate_sae_data(tr_vis, te_vis, sem_data[tr_idx], tr_labels)
            tr_sem, te_sem = self.estimate_sec_data(tr_vis, te_vis, tr_sem, te_sem, save_results, res_path)

            clf = make_pipeline(StandardScaler(), SVC(gamma='auto', C=1.0, kernel='linear'))
            clf.fit(tr_sem, tr_labels)
            prediction = clf.predict(te_sem)

            fold += 1
            accuracies.append(balanced_accuracy_score(te_labels, prediction))

        return accuracies
