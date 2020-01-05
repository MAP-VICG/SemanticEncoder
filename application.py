"""
Model to encode visual and semantic features of images

@author: Damares Resende
@contact: damaresresende@usp.br
@since: Mar 23, 2019

@organization: University of Sao Paulo (USP)
    Institute of Mathematics and Computer Science (ICMC) 
    Laboratory of Visualization, Imaging and Computer Graphics (VICG)
"""
import os
import sys
import time
import numpy as np
import tensorflow as tf
import tensorflow.python.keras.backend as K
from sklearn.model_selection import train_test_split

from src.core.encoder import SemanticEncoder
from src.core.classifier import SVMClassifier
from src.utils.normalization import Normalization
from src.parser.featuresparser import FeaturesParser
from src.utils.logwriter import LogWritter, MessageType
from src.parser.configparser import ConfigParser, AttributesType


def main():
    init_time = time.time()
    
    if len(sys.argv) > 1 and sys.argv[1] == '--config':
        configpath = sys.argv[2]
    else:
        configpath = os.path.join(os.path.join(os.getcwd(), '_files'), 'config.xml')
        
    config = ConfigParser(configpath)
    config.read_configuration()
    
    log = LogWritter(logpath=config.results_path, console=config.console)
    parser = FeaturesParser(fts_dir=config.features_path)
        
    log.write_message('Noise rate %s' % str(config.noise_rate), MessageType.INF)
    
    # if config.attributes_type == AttributesType.IND:
    #     log.write_message('Computing indexed semantic features', MessageType.INF)
    #     sem_fts = parser.get_semantic_features(subset=False, binary=True)
    #     sem_fts = np.multiply(sem_fts, np.array([v for v in range(1, sem_fts.shape[1] + 1)]))
    # else:
    #     log.write_message('Retrieving continuous semantic features', MessageType.INF)
    #     sem_fts = parser.get_semantic_features(subset=False, binary=False)

    # Y = parser.get_labels()
    # X = parser.concatenate_features(parser.get_visual_features(), sem_fts + abs(sem_fts.min()))
    # x_train, x_test, y_train, y_test = train_test_split(X, Y, stratify=Y, random_state=42, test_size=0.2)

    with open(os.sep.join(['_files', 'base', 'Birds-train-test-mask.txt'])) as f:
        mask = list(map(int, f.readlines()))

    with open(os.sep.join(['_files', 'features', 'Birds-labels.txt'])) as f:
        Y = list(map(int, f.readlines()))

    vis_fts = []
    sem_fts = []
    with open(os.sep.join(['_files', 'features', 'Birds-features.txt'])) as f:
        for line in f.readlines():
            vis_fts.append(list(map(float, line.split(','))))

    with open(os.sep.join(['_files', 'base', 'Birds-predicate-set.txt'])) as f:
        for line in f.readlines():
            sem_fts.append(list(map(float, line.split(','))))

    x_train = []
    y_train = []
    x_test = []
    y_test = []
    for i, value in enumerate(mask):
        if value == 1:
            a = vis_fts[i][:]
            b = sem_fts[i][:]
            a.extend(b)
            x_train.append(a)
            y_train.append(Y[i])
        else:
            a = vis_fts[i][:]
            b = sem_fts[i][:]
            a.extend(b)
            x_test.append(a)
            y_test.append(Y[i])

    with open(os.sep.join(['_files', 'base', 'Birds-predicate-set.txt'])) as f:
        aug_sem_fts = f.readlines()

    with open(os.sep.join(['_files', 'features', 'Birds-labels.txt'])) as f:
        Y_aug = list(map(int, f.readlines()))

    with open(os.sep.join(['_files', 'features', 'Birds-features-augmented.txt'])) as f:
        for i, line in enumerate(f.readlines()):
            a = list(map(float, line.split(',')))
            b = list(map(float, aug_sem_fts[i].split(',')))
            a.extend(b)
            x_train.append(a)
            y_train.append(Y_aug[i])

    x_train = np.array(x_train)
    x_test = np.array(x_test)
    y_train = np.array(y_train)
    y_test = np.array(y_test)

    norm_sem = Normalization(x_train[:, 2048:])
    norm_sem.normalize_zero_one_by_column(x_train[:, 2048:])
    norm_sem.normalize_zero_one_by_column(x_test[:, 2048:])

    norm_vis = Normalization(x_train[:, :2048])
    norm_vis.normalize_zero_one_by_column(x_train[:, :2048])
    norm_vis.normalize_zero_one_by_column(x_test[:, :2048])

    if config.save_test_set:
        with open('test_set.txt', 'w') as f:
            for row in x_test:
                f.write(', '.join(map(str, list(row))) + '\n')

        with open('test_labels.txt', 'w') as f:
            f.write(', '.join(map(str, list(y_test))))

    log.write_message('Starting Semantic Encoder Application', MessageType.INF)
    log.write_message('Autoencoder encoding dimension is %d' % config.encoding_size, MessageType.INF)
    log.write_message('The model will be trained for %d epochs' % config.epochs, MessageType.INF)

    results = dict()
    # svm = SVMClassifier()
    # results['REF'] = svm.run_svm(x_train=x_train[:, :2048], x_test=x_test[:, :2048],
    #                              y_train=y_train, y_test=y_test, njobs=-1)

    enc = SemanticEncoder(config.epochs, config.encoding_size)

    log.write_message('Running ALL', MessageType.INF)
    results['ALL'] = enc.run_encoder('ALL', x_train=enc.pick_semantic_features('ALL', x_train, opposite=False, noise_rate=config.noise_rate),
                                     x_test=enc.pick_semantic_features('ALL', x_test, opposite=False, noise_rate=config.noise_rate),
                                     y_train=y_train, y_test=y_test, baseline=0.02, noise_factor=config.ae_noise_factor)

    enc.save_results(results)
    elapsed = time.time() - init_time
    hours, rem = divmod(elapsed, 3600)
    minutes, seconds = divmod(rem, 60)
    time_elapsed = '{:0>2}:{:0>2}:{:05.2f}'.format(int(hours), int(minutes), seconds)

    log.write_message('Execution has finished successfully', MessageType.INF)
    log.write_message('Elapsed time is %s' % time_elapsed, MessageType.INF)
    
    
if __name__ == '__main__':
    config = tf.compat.v1.ConfigProto(log_device_placement=True)
    config.gpu_options.per_process_gpu_memory_fraction = 0.3
    K.set_session(tf.compat.v1.Session(config=config))
    
    main()
