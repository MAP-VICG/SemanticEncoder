'''
Autoencoder for visual and semantic features of images

@author: Damares Resende
@contact: damaresresende@usp.br
@since: Mar 23, 2019

@organization: University of Sao Paulo (USP)
    Institute of Mathematics and Computer Science (ICMC) 
    Laboratory of Visualization, Imaging and Computer Graphics (VICG)
'''

import os
import numpy as np
from random import randint
from keras.models import Model
from keras.layers import Input, Dense
from keras.callbacks import LambdaCallback

from matplotlib import pyplot as plt
from sklearn.manifold import TSNE
from sklearn.decomposition import PCA
from sklearn.decomposition import LatentDirichletAllocation

from core.vsclassifier import SVMClassifier


class VSAutoencoder:
    
    def __init__(self, x_train, y_train, cv, njobs):
        '''
        Initialize all models and runs grid search on SVM
        '''
        self.svm = None
        self.encoder = None
        self.decoder = None
        self.autoencoder = None
        self.svm_history = []
    
        self.x_train = x_train
        self.y_train = y_train
         
        self.svm = SVMClassifier()
        self.svm.run_classifier(self.x_train, self.y_train, cv, njobs)
        
    def run_autoencoder(self, enc_dim, nepochs, results_path):
        '''
        Builds and trains autoencoder model
        
        @param enc_dim: encoding size
        @param nepochs: number of epochs
        @param results_path: string with path to svm save results under
        @return object with training details and history
        '''
        
        def svm_callback(epoch, logs):
            '''
            Runs SVM and saves prediction results
            
            @param epoch: default callback parameter. Epoch index
            @param logs:default callback parameter. Loss result
            '''
            self.svm.model.best_estimator_.fit(self.x_train, self.y_train)
            pred_dict, prediction = self.svm.predict(self.x_train, self.y_train)
            self.svm_history.append(pred_dict)
            
            if epoch == nepochs - 1:
                self.svm.save_results(prediction, results_path, 
                                      {'epoch': epoch + 1, 'AE Loss': logs})
    
        input_fts = Input(shape=(self.x_train.shape[1],))
        
        encoded = Dense(1426, activation='relu')(input_fts)
        encoded = Dense(732, activation='relu')(encoded)
        encoded = Dense(328, activation='relu')(encoded)
        
        encoded = Dense(enc_dim, activation='relu')(encoded)
        
        decoded = Dense(328, activation='relu')(encoded)
        decoded = Dense(732, activation='relu')(decoded)
        decoded = Dense(1426, activation='relu')(decoded)
        decoded = Dense(self.x_train.shape[1], activation='relu')(decoded)

        self.autoencoder = Model(inputs=input_fts, outputs=decoded)
        self.autoencoder.compile(optimizer='adam', loss='mse')
        
        svm = LambdaCallback(on_epoch_end=svm_callback)
        
        history =  self.autoencoder.fit(self.x_train, 
                                        self.x_train,
                                        epochs=nepochs,
                                        batch_size=256,
                                        shuffle=True,
                                        verbose=1,
                                        validation_split=0.2,
                                        callbacks=[svm])
        
        encoded_input = Input(shape=(enc_dim,))
        decoder_layer = self.autoencoder.layers[-4](encoded_input)
        decoder_layer = self.autoencoder.layers[-3](decoder_layer)
        decoder_layer = self.autoencoder.layers[-2](decoder_layer)
        decoder_layer = self.autoencoder.layers[-1](decoder_layer)
        
        self.encoder = Model(input_fts, encoded)
        self.decoder = Model(encoded_input, decoder_layer)
        
        return history
    
    def plot_loss(self, history, results_path):
        '''
        Plots loss and validation loss along training
        
        @param history: dictionary with training history
        @param results_path: string with path to save results under
        '''
        try:
            plt.figure()
            plt.rcParams.update({'font.size': 10})
            
            plt.plot(history['loss'])
            plt.plot(history['val_loss'])
            plt.title('Autoencoder Loss')
            
            plt.xlabel('Epochs')
            plt.ylabel('Loss (MSE)')
            plt.legend(['train', 'test'], loc='upper right')
            
            root_path = os.sep.join(results_path.split(os.sep)[:-1])
            if not os.path.isdir(root_path):
                os.mkdir(root_path)
            
            plt.savefig(results_path)
        except OSError:
            print('>> ERROR: Loss image could not be saved under %s' % results_path)
    
    def plot_encoding(self, input_set, encoding, output_set, results_path):
        '''
        Plots input example vs encoded example vs decoded example of 5 random examples
        in test set
        
        @param input_set: autoencoder input
        @param encoding: autoencoder encoded features
        @param output_set: autoencoder output
        @param results_path: string with path to save results under
        '''
        ex_idx = set()
        while len(ex_idx) < 5:
            ex_idx.add(randint(0, input_set.shape[0] - 1))
        
        error = output_set - input_set
    
        try:
            plt.figure()
            plt.rcParams.update({'font.size': 6})
            plt.subplots_adjust(wspace=0.4, hspace=0.9)
            
            for i, idx in enumerate(ex_idx):
                ax = plt.subplot(5, 4, 4 * i + 1)
                plt.plot(input_set[idx, :], linestyle='None', marker='o', markersize=1)
                ax.set_title('%d - Input' % idx)
                ax.axes.get_xaxis().set_visible(False)
                
                ax = plt.subplot(5, 4, 4 * i + 2)
                plt.plot(encoding[idx, :], linestyle='None', marker='o', markersize=1)
                ax.set_title('%d - Encoding' % idx)
                ax.axes.get_xaxis().set_visible(False)
                
                ax = plt.subplot(5, 4, 4 * i + 3)
                plt.plot(output_set[idx, :], linestyle='None', marker='o', markersize=1)
                ax.set_title('%d - Output' % idx)
                ax.axes.get_xaxis().set_visible(False)
                
                ax = plt.subplot(5, 4, 4 * i + 4)
                plt.plot(error[idx, :], linestyle='None', marker='o', markersize=1)
                ax.set_title('Error')
                ax.axes.get_xaxis().set_visible(False)
            
            root_path = os.sep.join(results_path.split(os.sep)[:-1])
            if not os.path.isdir(root_path):
                os.mkdir(root_path)
            
            plt.savefig(results_path)
        except OSError:
            print('>> ERROR: Error image could not be saved under %s' % results_path)
            
    def plot_spatial_distribution(self, input_set, encoding, output_set, labels, results_path):
        '''
        Plots the spatial distribution of input, encoding and output using PCA, TSNE and LDA
        
        @param input_set: autoencoder input
        @param encoding: autoencoder encoded features
        @param output_set: autoencoder output
        @param labels: data set labels
        @param results_path: string with path to save results under
        ''' 
        plt.figure()
        plt.rcParams.update({'font.size': 8})
             
        try:    
            plt.subplots_adjust(wspace=0.5, hspace=0.5)
            pca = PCA(n_components=2)
             
            ax = plt.subplot(331)
            ax.set_title('PCA - Input')
            input_fts = pca.fit_transform(input_set)
            plt.scatter(input_fts[:,0], input_fts[:,1], c=labels, cmap='hsv')
            
            ax = plt.subplot(332)
            ax.set_title('PCA - Encoding')
            encoding_fts = pca.fit_transform(encoding)
            plt.scatter(encoding_fts[:,0], encoding_fts[:,1], c=labels, cmap='hsv')
             
            ax = plt.subplot(333)
            ax.set_title('PCA - Output')
            output_fts = pca.fit_transform(output_set)
            plt.scatter(output_fts[:,0], output_fts[:,1], c=labels, cmap='hsv')
        except ValueError:
            print('>> ERROR: PCA could not be computed')
            
        try:
            tsne = TSNE(n_components=2)
             
            ax = plt.subplot(334)
            ax.set_title('TSNE - Input')
            input_fts = tsne.fit_transform(input_set)
            plt.scatter(input_fts[:,0], input_fts[:,1], c=labels, cmap='hsv')

            ax = plt.subplot(335)
            ax.set_title('TSNE - Encoding')
            encoding_fts = tsne.fit_transform(encoding)
            plt.scatter(encoding_fts[:,0], encoding_fts[:,1], c=labels, cmap='hsv')
                         
            ax = plt.subplot(336)
            ax.set_title('TSNE - Output')
            output_fts = tsne.fit_transform(output_set)
            plt.scatter(output_fts[:,0], output_fts[:,1], c=labels, cmap='hsv')  
        except ValueError:
            print('>> ERROR: TSNE could not be computed')
            
        try:
            lda = LatentDirichletAllocation(n_components=2)
            
            ax = plt.subplot(337)
            ax.set_title('LDA - Input')
            input_fts = lda.fit_transform(input_set)
            plt.scatter(input_fts[:,0], input_fts[:,1], c=labels, cmap='hsv')
            
            ax = plt.subplot(338)
            ax.set_title('LDA - Encoding')
            encoding_fts = lda.fit_transform(encoding)
            plt.scatter(encoding_fts[:,0], encoding_fts[:,1], c=labels, cmap='hsv')
            
            ax = plt.subplot(339)
            ax.set_title('LDA - Output')
            output_fts = lda.fit_transform(output_set)
            plt.scatter(output_fts[:,0], output_fts[:,1], c=labels, cmap='hsv')
        except ValueError:
            print('>> ERROR: LDA could not be computed')
        
        try:
            root_path = os.sep.join(results_path.split(os.sep)[:-1])
            if not os.path.isdir(root_path):
                os.mkdir(root_path)

            plt.savefig(results_path)
        except OSError:
            print('>> ERROR: Scatter plots could not be saved under %s' % results_path)
            
    def plot_pca_vs_encoding(self, input_set, encoding, results_path):
        '''
        Plots PCA against encoding components
        
        @param input_set: autoencoder input
        @param encoding: autoencoder encoded features
        @param results_path: string with path to save results under
        ''' 
        ex_idx = set()
        while len(ex_idx) < 5:
            ex_idx.add(randint(0, input_set.shape[0] - 1))
            
        pca = PCA(n_components=encoding.shape[1])
        input_fts = pca.fit_transform(input_set)
    
        try:
            plt.figure()
            plt.rcParams.update({'font.size': 6})
            plt.subplots_adjust(wspace=0.4, hspace=0.9)
            
            for i, idx in enumerate(ex_idx):
                ax = plt.subplot(5, 2, 2 * i + 1)
                plt.plot(input_fts[idx, :], linestyle='None', marker='o', markersize=3)
                ax.set_title('%d - PCA' % idx)
                ax.axes.get_xaxis().set_visible(False)
                
                ax = plt.subplot(5, 2, 2 * i + 2)
                plt.plot(encoding[idx, :], linestyle='None', marker='o', markersize=3)
                ax.set_title('%d - Encoding' % idx)
                ax.axes.get_xaxis().set_visible(False)
            
            root_path = os.sep.join(results_path.split(os.sep)[:-1])
            if not os.path.isdir(root_path):
                os.mkdir(root_path)
            
            plt.savefig(results_path)
        except (OSError, ValueError):
            print('>> ERROR: PCA vs Encoding image could not be saved under %s' % results_path)