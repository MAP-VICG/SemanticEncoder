"""
Encodes visual and semantic features of images

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
import tensorflow as tf
import tensorflow.python.keras.backend as K

from utils.src.configparser import ConfigParser
from utils.src.normalization import Normalization
from utils.src.logwriter import LogWriter, MessageType
from featureextraction.src.dataparsing import DataParser
from encoding.src.encoder import ModelType, Autoencoder
from encoding.src.plotter import Plotter


def main():
    init_time = time.time()
    
    if len(sys.argv) > 1 and sys.argv[1] == '--config':
        config_path = sys.argv[2]
    else:
        config_path = os.path.join(os.getcwd(), 'config.xml')
        
    config = ConfigParser(config_path)
    config.read_configuration()
    log = LogWriter(log_path=config.results_path, log_name='semantic_encoder', console=config.console)

    log.write_message('Configuration file: %s' % str(config.configfile), MessageType.INF)
    log.write_message('Data set: n %s' % str(config.dataset), MessageType.INF)
    log.write_message('Results path: %s' % str(config.results_path), MessageType.INF)
    log.write_message('Number of epochs: %s' % str(config.epochs), MessageType.INF)
    log.write_message('Encoding size: %s' % str(config.encoding_size), MessageType.INF)

    log.write_message('x_train path is %s' % config.x_train_path, MessageType.INF)
    log.write_message('y_train path is %s' % config.y_train_path, MessageType.INF)
    log.write_message('x_test path is %s' % config.x_test_path, MessageType.INF)
    log.write_message('y_test path is %s' % config.y_test_path, MessageType.INF)

    log.write_message('Visual features baseline: %f' % config.baseline['vis'], MessageType.INF)
    log.write_message('Stacked model baseline: %f' % config.baseline['stk'], MessageType.INF)
    log.write_message('Tuning model baseline: %f' % config.baseline['tnn'], MessageType.INF)
    log.write_message('PCA baseline: %f' % config.baseline['pca'], MessageType.INF)

    try:
        # Read features
        x_train = DataParser.get_features(config.x_train_path)
        y_train = DataParser.get_labels(config.y_train_path)

        x_test = DataParser.get_features(config.x_test_path)
        y_test = DataParser.get_labels(config.y_test_path)

        # Normalize data
        Normalization.normalize_zero_one_by_column(x_train)
        Normalization.normalize_zero_one_by_column(x_test)

        # Encode features
        ae = Autoencoder(ModelType.SIMPLE_AE, x_train.shape[1], config.encoding_size, x_train.shape[1], config.baseline)
        ae.run_ae_model(x_train, y_train, x_test, y_test, config.epochs, njobs=-1)

        # Save all results
        log.write_message('Train Accuracies %s' % str(ae.accuracies['train']), MessageType.INF)
        log.write_message('Test Accuracies %s' % str(ae.accuracies['test']), MessageType.INF)
        log.write_message('Best Accuracy %s' % str(ae.best_accuracy), MessageType.INF)
        log.write_message('Best SVM Parameters %s' % str(ae.svm_best_parameters), MessageType.INF)

        ae.define_best_models(x_train, y_train, os.path.join(config.results_path, 'ae_weights.h5'))

        pt = Plotter(ae, config.results_path, config.chosen_classes, config.classes_names)
        pt.plot_evaluation(x_test, y_test, ae.baseline)

        log.write_message('Execution has finished successfully', MessageType.INF)
    except (IOError, FileNotFoundError) as e:
        log.write_message('Could not read data set. %s' % str(e), MessageType.ERR)
    except ValueError as e:
        log.write_message('There are invalid values in the data. %s' % str(e), MessageType.ERR)

    elapsed = time.time() - init_time
    hours, rem = divmod(elapsed, 3600)
    minutes, seconds = divmod(rem, 60)
    time_elapsed = '{:0>2}:{:0>2}:{:05.2f}'.format(int(hours), int(minutes), seconds)

    log.write_message('Elapsed time is %s' % time_elapsed, MessageType.INF)
    
    
if __name__ == '__main__':
    config = tf.compat.v1.ConfigProto(log_device_placement=True)
    config.gpu_options.per_process_gpu_memory_fraction = 0.3
    K.set_session(tf.compat.v1.Session(config=config))
    
    main()
