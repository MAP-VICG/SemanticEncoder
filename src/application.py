'''
Model to encode visual and semantic features of images

@author: Damares Resende
@contact: damaresresende@usp.br
@since: Mar 23, 2019

@organization: University of Sao Paulo (USP)
    Institute of Mathematics and Computer Science (ICMC) 
    Laboratory of Visualization, Imaging and Computer Graphics (VICG)
'''

import os
import time
import numpy as np
import tensorflow as tf
from sklearn.decomposition import PCA
from sklearn.model_selection import train_test_split
from tensorflow.compat.v1.keras.backend import set_session

from core.vsclassifier import SVMClassifier
from core.vsencoder import SemanticEncoder
from core.featuresparser import FeaturesParser
from utils.logwriter import LogWritter, MessageType


def main():
    init_time = time.time()
    
    mock = True
    
    epochs = 50
    enc_dim = 128
    simple = False
    batch_norm = False
    
    if mock:
        log = LogWritter(console=True)
        parser = FeaturesParser(fts_dir=os.path.join('features', 'mock'))
        epochs = 5
    else:
        log = LogWritter(console=False)
        parser = FeaturesParser()
    
    log.write_message('Mock %s' % str(mock), MessageType.INF)
    log.write_message('Simple %s' % str(simple), MessageType.INF)
    log.write_message('Batch Norm %s' % str(batch_norm), MessageType.INF)
    
    sem_fts = parser.get_semantic_features()
    sem_fts = np.multiply(sem_fts, np.array([v for v in range(1, sem_fts.shape[1] + 1)]))
    
    Y = parser.get_labels()
    X = parser.concatenate_features(parser.get_visual_features(), sem_fts)
    x_train, x_test, y_train, y_test = train_test_split(X, Y, stratify=Y, random_state=42, test_size=0.2)
    
#     from sklearn.model_selection import KFold
#     kf = KFold(n_splits=10)
#     index = 0
#     
#     def save_set(namex, datax, namey, datay):
#         with open(namex, 'w') as f:
#             for row in datax:
#                 f.write(', '.join(map(str, list(row))) + '\n')
#          
#         with open(namey, 'w') as f:
#             f.write(', '.join(map(str, list(datay))))
# 
#     for train_index, test_index in kf.split(X):
#         save_set('x_train_f' + str(index) + '.txt', X[train_index], 'y_train_f' + str(index) + '.txt', Y[train_index])
#         save_set('x_test_f' + str(index) + '.txt', X[test_index], 'y_test_f' + str(index) + '.txt', Y[test_index])
#         index += 1

    if not mock:
        with open('test_set.txt', 'w') as f:
            for row in x_test:
                f.write(', '.join(map(str, list(row))) + '\n')
        
        with open('test_labels.txt', 'w') as f:
            f.write(', '.join(map(str, list(y_test))))
    
    log.write_message('Starting Semantic Encoder Application', MessageType.INF)
    log.write_message('Autoencoder encoding dimension is %d' % enc_dim, MessageType.INF)
    log.write_message('The model will be trained for %d epochs' % epochs, MessageType.INF)
    
    results = dict()
    
    # classifying visual features
    svm = SVMClassifier()
    enc = SemanticEncoder(epochs, enc_dim)
    
    log.write_message('Running ALL', MessageType.INF)
    pca = PCA(n_components=enc_dim)
    results['ALL_pca'] = svm.run_svm(x_train=pca.fit_transform(enc.pick_semantic_features('ALL', x_train, opposite=False)), 
                                 x_test=pca.fit_transform(enc.pick_semantic_features('ALL', x_test, opposite=False)), 
                                 y_train=y_train, y_test=y_test, tag='ALL', njobs=-1)
    
    log.write_message('Running COLOR', MessageType.INF)
    pca = PCA(n_components=enc_dim)
    results['COLOR_pca'] = svm.run_svm(x_train=pca.fit_transform(enc.pick_semantic_features('COLOR', x_train, opposite=False)), 
                                 x_test=pca.fit_transform(enc.pick_semantic_features('COLOR', x_test, opposite=False)), 
                                 y_train=y_train, y_test=y_test, tag='COLOR', njobs=-1)
    
    log.write_message('Running PARTS', MessageType.INF)
    pca = PCA(n_components=enc_dim)
    results['PARTS_pca'] = svm.run_svm(x_train=pca.fit_transform(enc.pick_semantic_features('PARTS', x_train, opposite=False)), 
                                 x_test=pca.fit_transform(enc.pick_semantic_features('PARTS', x_test, opposite=False)), 
                                 y_train=y_train, y_test=y_test, tag='PARTS', njobs=-1)
     
    log.write_message('Running SHAPE', MessageType.INF)
    pca = PCA(n_components=enc_dim)
    results['SHAPE_pca'] = svm.run_svm(x_train=pca.fit_transform(enc.pick_semantic_features('SHAPE', x_train, opposite=False)), 
                                 x_test=pca.fit_transform(enc.pick_semantic_features('SHAPE', x_test, opposite=False)), 
                                 y_train=y_train, y_test=y_test, tag='SHAPE', njobs=-1)
     
    log.write_message('Running TEXTURE', MessageType.INF)
    pca = PCA(n_components=enc_dim)
    results['TEXTURE_pca'] = svm.run_svm(x_train=pca.fit_transform(enc.pick_semantic_features('TEXTURE', x_train, opposite=False)), 
                                 x_test=pca.fit_transform(enc.pick_semantic_features('TEXTURE', x_test, opposite=False)), 
                                 y_train=y_train, y_test=y_test, tag='TEXTURE', njobs=-1)
     
    log.write_message('Running not COLOR', MessageType.INF)
    pca = PCA(n_components=enc_dim)
    results['_COLOR_pca'] = svm.run_svm(x_train=pca.fit_transform(enc.pick_semantic_features('COLOR', x_train, opposite=True)), 
                                 x_test=pca.fit_transform(enc.pick_semantic_features('COLOR', x_test, opposite=True)), 
                                 y_train=y_train, y_test=y_test, tag='not_COLOR', njobs=-1)
     
    log.write_message('Running not PARTS', MessageType.INF)
    pca = PCA(n_components=enc_dim)
    results['_PARTS_pca'] = svm.run_svm(x_train=pca.fit_transform(enc.pick_semantic_features('PARTS', x_train, opposite=True)), 
                                 x_test=pca.fit_transform(enc.pick_semantic_features('PARTS', x_test, opposite=True)), 
                                 y_train=y_train, y_test=y_test, tag='not_PARTS', njobs=-1)
     
    log.write_message('Running not SHAPE', MessageType.INF)
    pca = PCA(n_components=enc_dim)
    results['_SHAPE_pca'] = svm.run_svm(x_train=pca.fit_transform(enc.pick_semantic_features('SHAPE', x_train, opposite=True)), 
                                 x_test=pca.fit_transform(enc.pick_semantic_features('SHAPE', x_test, opposite=True)), 
                                 y_train=y_train, y_test=y_test, tag='not_SHAPE', njobs=-1)
     
    log.write_message('Running not TEXTURE', MessageType.INF)
    pca = PCA(n_components=enc_dim)
    results['_TEXTURE_pca'] = svm.run_svm(x_train=pca.fit_transform(enc.pick_semantic_features('TEXTURE', x_train, opposite=True)), 
                                 x_test=pca.fit_transform(enc.pick_semantic_features('TEXTURE', x_test, opposite=True)), 
                                 y_train=y_train, y_test=y_test, tag='not_TEXTURE', njobs=-1)
     
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
    set_session(tf.compat.v1.Session(config=config))
    
    main()