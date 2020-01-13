"""
Autoencoder for visual and semantic features of images

@author: Damares Resende
@contact: damaresresende@usp.br
@since: Mar 27, 2019

@organization: University of Sao Paulo (USP)
    Institute of Mathematics and Computer Science (ICMC) 
    Laboratory of Visualization, Imaging and Computer Graphics (VICG)
"""
import os
from sklearn.svm import LinearSVC
from sklearn.model_selection import GridSearchCV
from sklearn.metrics import classification_report

from utils.src.logwriter import LogWritter, MessageType


class SVMClassifier:
    def __init__(self, console=False):
        """
        Setting tuning parameters
        
        @param console: if True, prints debug in console
        """
        self.model = None
        self.logger = LogWritter(console=console)
        self.tuning_params = {'C': [0.1, 0.3, 0.6, 1, 10]}
        self.results_path = os.path.join(os.path.join(os.path.join(os.getcwd().split('SemanticEncoder')[0],
                                                                   'SemanticEncoder'), '_files'), 'results')
        
        if not os.path.isdir(self.results_path):
            os.mkdir(self.results_path)
            
        self.logger.write_message('SVM tuning parameters are %s.' % str(self.tuning_params), MessageType.INF)
        
    def run_classifier(self, x_train, y_train, nfolds=5, njobs=None):
        """
        Builds and trains classification model based on grid search
        
        @param x_train: 2D numpy array training set
        @param y_train: 1D numpy array test labels
        @param nfolds: number of folds in cross validation
        @param njobs: number of jobs to run in parallel on Grid Search
        """
        if nfolds < 2:
            raise ValueError('Number of folds cannot be less than 2')
        
        self.model = GridSearchCV(LinearSVC(verbose=0, max_iter=1000), 
                                  self.tuning_params, cv=nfolds, 
                                  iid=False, scoring='recall_macro', n_jobs=njobs)
        
        self.model.fit(x_train, y_train)
    
    def predict(self, x_test, y_test):
        """
        Tests model performance on test set and saves classification results
        
        @param x_test: 2D numpy array with test set
        @param y_test: 1D numpy array test labels
        @return tuple with dictionary with prediction results and string with 
        full prediction table
        """
        y_true, y_pred = y_test, self.model.best_estimator_.predict(x_test)
        prediction = classification_report(y_true, y_pred)

        keys = ['precision', 'recall', 'f1-score', 'support']
        pred_dict = {'accuracy': {key: None for key in keys},
                     'macro avg': {key: None for key in keys[-2:]},
                     'weighted avg': {key: None for key in keys}}
        row = -1
        values = -1
        try:
            for row in prediction.split('\n')[-4:-1]:
                values = row.split()
                
                if values[0] == 'accuracy':
                    pred_dict[values[0]]['f1-score'] = float(values[-2])
                    pred_dict[values[0]]['support'] = float(values[-1])
                else:
                    for idx, key in enumerate(keys):
                        pred_dict[values[0] + ' ' + values[1]][key] = float(values[idx + 2])
                    
        except KeyError:
            self.logger.write_message('Could not retrieve prediction values from %s: %s'
                                      % (str(row), str(values)), MessageType.ERR)
               
        self.logger.write_message('SVM Prediction result is %s' % str(pred_dict), MessageType.INF) 
        return pred_dict, prediction

    def run_svm(self, x_train, y_train, x_test, y_test, tag=None, nfolds=5, njobs=None):
        """
        Runs SVM and saves results
         
        @param x_train: 2D numpy array training set
        @param y_train: 1D numpy array test labels
        @param x_test: 2D numpy array with test set
        @param y_test: 1D numpy array test labels
        @param nfolds: number of folds in cross validation
        @param tag: string with folder name to saver results under
        @param njobs: number of jobs to run in parallel on Grid Search
        @return dictionary with svm results
        """
        self.logger.write_message('Training set shape %s' % str(x_train.shape), MessageType.INF)
        self.logger.write_message('Test set shape %s' % str(x_test.shape), MessageType.INF)
        
        self.run_classifier(x_train, y_train, nfolds, njobs)
         
        self.model.best_estimator_.fit(x_train, y_train)
        pred_dict, prediction = self.predict(x_test, y_test)
        self.save_results(prediction, pred_dict, tag)
         
        return pred_dict
        
    def save_results(self, prediction, appendix=None, tag=''):
        """
        Saves classification results
        
        @param prediction: string with full prediction table
        @param tag: string with folder name to saver results under
        @param appendix: dictionary with extra data to save to results file
        """
        if tag and isinstance(tag, str):
            result_file = os.path.join(self.results_path, tag)
            if not os.path.isdir(result_file):
                os.mkdir(result_file)

            result_file = os.path.join(result_file, 'svm_prediction.txt')
        else:
            result_file = os.path.join(self.results_path, 'svm_prediction.txt')

        try:
            with open(result_file, 'w+') as f:
                f.write(prediction)
                f.write('\nbest parameters: %s' % str(self.model.best_params_))
                
                if appendix:
                    for key in appendix.keys():
                        f.write('\n%s: %s' % (key, str(appendix[key])))
                    
        except (IsADirectoryError, OSError):
            self.logger.write_message('Could not save prediction results under %s.' % result_file, MessageType.ERR)
