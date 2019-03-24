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
import tensorflow as tf
from keras.utils import normalize
from sklearn.model_selection import train_test_split
from keras.backend.tensorflow_backend import set_session

from core.featuresparser import FeaturesParser
from core.annotationsparser import PredicateType
from core.vsautoencoder import VSAutoencoder


def main():
    
    fls_path = os.path.join(os.getcwd(), '_files/awa2')
    fts_path = os.path.join(fls_path, 'features/ResNet101')
    res_path = os.path.join(fls_path, 'results')
    ann_path = os.path.join(fls_path, 'base')
    
    parser = FeaturesParser(fts_path)
    vis_fts = parser.get_visual_features()
    sem_fts = normalize(parser.get_semantic_features(ann_path, 
                                                     PredicateType.CONTINUOUS) + 1, 
                                                     order=1, axis=1)
    
    Y = parser.get_labels()
    X = parser.concatenate_features(vis_fts, sem_fts)
    x_train, x_test, _, _ = train_test_split(X, Y, stratify=Y, test_size=0.2)
    
    ae = VSAutoencoder()
    history = ae.run_autoencoder(x_train, enc_dim=32, nepochs=150)
    ae.plot_loss(history.history, os.path.join(res_path, 'ae_loss.png'))
    ae.plot_error(x_test, os.path.join(res_path, 'ae_error.png'))

if __name__ == '__main__':
    
    config = tf.ConfigProto(log_device_placement=True)
    config.gpu_options.per_process_gpu_memory_fraction = 0.3
    set_session(tf.Session(config=config))
    
    main()