import os
import json
import logging

from encoders.tools.src.svm_classification import SVMClassifier, DataType


class Classification:
    def __init__(self, folds, epochs, results_path, save=True):
        self.save = save
        self.folds = folds
        self.epochs = epochs
        self.results_path = results_path
        self.result = {'i_cub': dict(), 'r_cub': dict(), 'i_awa': dict(), 'r_awa': dict()}

    def run_classification(self, data_path, label, data_type, rate=0.0):
        rate_label = str(int(rate * 100)).zfill(3)
        results_path = os.sep.join([self.results_path, label, rate_label])

        if self.save and not os.path.isdir(results_path):
            os.makedirs(results_path)

        logging.info('Classifying dataset %s' % label)
        svm = SVMClassifier(data_type, self.folds, self.epochs, self.save, results_path, rate)
        vis_data, lbs_data, sem_data = svm.get_data(data_path)

        # self.result[label]['sem'] = svm.classify_sem_data(sem_data, lbs_data)
        # self.result[label]['vis'] = svm.classify_vis_data(vis_data, lbs_data)
        # self.result[label]['sae'] = svm.classify_sae_data(vis_data, sem_data, lbs_data)
        # self.result[label]['cat'] = svm.classify_concat_data(vis_data, sem_data, lbs_data)
        # self.result[label]['pca'] = svm.classify_concat_pca_data(vis_data, sem_data, lbs_data)
        self.result[label]['vse'] = svm.classify_vse_data(vis_data, sem_data, lbs_data)
        # self.result[label]['s2s'] = svm.classify_sae2vse_data(vis_data, sem_data, lbs_data)

        rate_label = str(int(rate * 100))
        with open(os.path.join(self.results_path, 'classification_results_%s.json' % rate_label.zfill(3)), 'w+') as f:
            json.dump(self.result, f, indent=4, sort_keys=True)

    def classify_all(self, rate):
        logging.info('Running classification for degradation rate of %.2f' % rate)
        self.run_classification('../Datasets/SAE/cub_demo_data.mat', 'i_cub', DataType.CUB, rate=rate)
        # self.run_classification('../Datasets/SAE/awa_demo_data.mat', 'i_awa', DataType.AWA, rate=rate)
        # self.run_classification('../Datasets/SAE/cub_demo_data_resnet.mat', 'r_cub', DataType.CUB, rate=rate)
        # self.run_classification('../Datasets/SAE/awa_demo_data_resnet.mat', 'r_awa', DataType.AWA, rate=rate)


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG,
                        filename='classify_svm.log',
                        format='%(asctime)s %(levelname)s [%(module)s, %(funcName)s]: %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S')

    for degradation_rate in [0.3]:
        klass = Classification(5, 50, 'results_test_3', save=False)
        klass.classify_all(degradation_rate)
