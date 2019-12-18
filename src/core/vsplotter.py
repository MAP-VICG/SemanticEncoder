'''
Contains methods to plot results

@author: Damares Resende
@contact: damaresresende@usp.br
@since: Jun 8, 2019

@organization: University of Sao Paulo (USP)
    Institute of Mathematics and Computer Science (ICMC) 
    Laboratory of Visualization, Imaging and Computer Graphics (VICG)
'''
import os
import numpy as np
from random import randint
import matplotlib
matplotlib.use('Agg')
from matplotlib import pyplot as plt

from sklearn.manifold import TSNE
from sklearn.decomposition import PCA
from sklearn.decomposition import LatentDirichletAllocation

from src.utils.logwriter import LogWritter, MessageType


class Plotter:
    def __init__(self, enc_dim, console=False):
        '''
        Initializes logger and string for results path

        @param enc_dim: autoencoder encoding size
        @param console: if True, prints debug in console
        '''
        self.enc_dim = enc_dim
        self.logger = LogWritter(console=console)
        self.results_path = os.path.join(os.path.join(os.path.join(os.getcwd().split('SemanticEncoder')[0], 
                                                           'SemanticEncoder'), '_files'), 'results')
        if not os.path.isdir(self.results_path):
            os.mkdir(self.results_path)
    
    def plot_encoding(self, input_set, encoding, output_set, tag=None):
        '''
        Plots input example vs encoded example vs decoded example of 5 random examples
        in test set
        
        @param input_set: autoencoder input
        @param encoding: autoencoder encoded features
        @param output_set: autoencoder output
        @param tag: string with folder name to saver results under
        '''
        ex_idx = set()
        while len(ex_idx) < 5:
            ex_idx.add(randint(0, input_set.shape[0] - 1))
        
        error = output_set - input_set
    
        fig = plt.figure()
        plt.rcParams.update({'font.size': 6})
        plt.subplots_adjust(wspace=0.4, hspace=0.9)
        
        if tag and isinstance(tag, str):
            root = os.path.join(self.results_path, tag)
            file_name = os.path.join(root, 'ae_encoding.png')
            if not os.path.isdir(root):
                os.mkdir(root)
        else:
            file_name = os.path.join(self.results_path, 'ae_encoding.png')
            
        try:
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
            
            plt.savefig(file_name)
        except OSError:
            self.logger.write_message('Error image could not be saved under %s.' % file_name, MessageType.ERR)
            plt.close(fig)
            
            
    def plot_spatial_distribution(self, input_set, encoding, output_set, classes, tag=None):
        '''
        Plots the spatial distribution of input, encoding and output using PCA and TSNE
        
        @param input_set: autoencoder input
        @param encoding: autoencoder encoded features
        @param output_set: autoencoder output
        @param classes: data set classes
        @param tag: string with folder name to saver results under
        '''
        def plot_labels(plt, ax, features):
            for k, label in enumerate(chosen_classes):
                    plot_mask = [False] * len(labels)
                    for i in range(len(labels)):
                        if labels[i] == label:
                            plot_mask[i] = True
                
                    plt.scatter(features[plot_mask,0], features[plot_mask,1], c=colors[k], 
                                s=np.ones(labels[plot_mask].shape), label=classes_names[k])
            ax.legend(prop={'size': 3})
            
        fig = plt.figure()
        plt.rcParams.update({'font.size': 8})
        chosen_classes = [50, 9, 7, 31, 38]
        colors = ['tab:blue', 'tab:orange', 'tab:green', 'tab:red', 'tab:pink']
        # classes_names = ['dolphin', 'blue+whale', 'horse', 'giraffe', 'zebra']
        classes_names = ['Eared_Grebe', 'Brewer_Blackbird', 'Parakeet_Auklet', 'Black_billed_Cuckoo', 'Great_Crested_Flycatcher']
        
        mask = [False] * len(classes)
        for i in range(len(classes)):
            if  classes[i] in chosen_classes:
                mask[i] = True
        
        labels = classes[mask]        
        if tag and isinstance(tag, str):
            root = os.path.join(self.results_path, tag)
            file_name = os.path.join(root, 'ae_distribution.png')
            if not os.path.isdir(root):
                os.mkdir(root)
        else:
            file_name = os.path.join(self.results_path, 'ae_distribution.png')
             
        try:    
            plt.subplots_adjust(wspace=0.5, hspace=0.5)
            pca = PCA(n_components=2)
             
            ax = plt.subplot(331)
            ax.set_title('PCA - Input')
            input_fts = pca.fit_transform(input_set[mask, :])
            plot_labels(plt, ax, input_fts)
            
            ax = plt.subplot(332)
            ax.set_title('PCA - Encoding')
            encoding_fts = pca.fit_transform(encoding[mask, :])
            plot_labels(plt, ax, encoding_fts)
             
            ax = plt.subplot(333)
            ax.set_title('PCA - Output')
            output_fts = pca.fit_transform(output_set[mask, :])
            plot_labels(plt, ax, output_fts)
        except ValueError:
            self.logger.write_message('PCA could not be computed.', MessageType.ERR)
            
        try:
            tsne = TSNE(n_components=2)
             
            ax = plt.subplot(334)
            ax.set_title('TSNE - Input')
            input_fts = tsne.fit_transform(input_set[mask, :])
            plot_labels(plt, ax, input_fts)

            ax = plt.subplot(335)
            ax.set_title('TSNE - Encoding')
            encoding_fts = tsne.fit_transform(encoding[mask, :])
            plot_labels(plt, ax, encoding_fts)
                         
            ax = plt.subplot(336)
            ax.set_title('TSNE - Output')
            output_fts = tsne.fit_transform(output_set[mask, :])
            plot_labels(plt, ax, output_fts)  
        except ValueError:
            self.logger.write_message('TSNE could not be computed.', MessageType.ERR)
        
        try:
            lda = LatentDirichletAllocation(n_components=2)

            ax = plt.subplot(337)
            ax.set_title('LDA - Input')
            input_fts = lda.fit_transform(input_set[mask, :])
            plot_labels(plt, ax, input_fts)

            ax = plt.subplot(338)
            ax.set_title('LDA - Encoding')
            encoding_fts = lda.fit_transform(encoding[mask, :])
            plot_labels(plt, ax, encoding_fts)

            ax = plt.subplot(339)
            ax.set_title('LDA - Output')
            output_fts = lda.fit_transform(output_set[mask, :])
            plot_labels(plt, ax, output_fts)
        except ValueError:
            self.logger.write_message('LDA could not be computed.', MessageType.ERR)
            
        try:    
            if not os.path.isdir(self.results_path):
                os.mkdir(self.results_path)
                
            plt.savefig(file_name)
        except OSError:
            self.logger.write_message('Scatter plots could not be saved under %s.' 
                                      % file_name, MessageType.ERR)
        plt.close(fig)
            
    def plot_pca_vs_encoding(self, input_set, encoding, tag=None):
        '''
        Plots PCA against encoding components
        
        @param input_set: autoencoder input
        @param encoding: autoencoder encoded features
        @param tag: string with folder name to saver results under
        ''' 
        ex_idx = set()
        while len(ex_idx) < 5:
            ex_idx.add(randint(0, input_set.shape[0] - 1))
            
        pca = PCA(n_components=encoding.shape[1])
        input_fts = pca.fit_transform(input_set)
    
        fig = plt.figure()
        plt.rcParams.update({'font.size': 6})
        plt.subplots_adjust(wspace=0.4, hspace=0.9)
        
        if tag and isinstance(tag, str):
            root = os.path.join(self.results_path, tag)
            file_name = os.path.join(root, 'ae_components.png')
            if not os.path.isdir(root):
                os.mkdir(root)
        else:
            file_name = os.path.join(self.results_path, 'ae_components.png')
            
        try:        
            for i, idx in enumerate(ex_idx):
                ax = plt.subplot(5, 2, 2 * i + 1)
                plt.plot(input_fts[idx, :], linestyle='None', marker='o', markersize=3)
                ax.set_title('%d - PCA' % idx)
                ax.axes.get_xaxis().set_visible(False)
                
                ax = plt.subplot(5, 2, 2 * i + 2)
                plt.plot(encoding[idx, :], linestyle='None', marker='o', markersize=3)
                ax.set_title('%d - Encoding' % idx)
                ax.axes.get_xaxis().set_visible(False)
            
            plt.savefig(file_name)
        except (OSError, ValueError):
            self.logger.write_message('PCA vs Encoding image could not be saved under %s.' 
                                      % file_name, MessageType.ERR)
        plt.close(fig)

    def plot_evaluation(self, history, svm_history, encoding, tag='', baseline=0):
        '''
        Plots classification accuracy, training error, and code covariance matrix, 
        standard deviation and mean
        
        @return None
        '''
        fig = plt.figure(figsize=(14, 12))
        plt.rcParams.update({'font.size': 12})
        plt.subplots_adjust(wspace=0.4, hspace=0.9)
        
        if tag and isinstance(tag, str):
            root = os.path.join(self.results_path, tag)
            file_name = os.path.join(root, 'ae_evaluation.png')
            if not os.path.isdir(root):
                os.mkdir(root)
        else:
            file_name = os.path.join(self.results_path, 'ae_evaluation.png')
            
        try:
            ax = plt.subplot(221)
            ax.set_title('SVM Accuracy')
            plt.plot([acc['accuracy']['f1-score'] for acc in svm_history['train']])
            plt.plot([acc['accuracy']['f1-score'] for acc in svm_history['test']])
            
            if baseline != 0:
                plt.plot([baseline for _ in range(len(svm_history['train']))], linestyle='dashed', 
                         linewidth=2, color='k')
            
            plt.xlabel('Epochs')
            plt.ylabel('F1-Score')
            plt.legend(['train', 'test', 'baseline'])
            
            ax = plt.subplot(222)
            ax.set_title('AE Loss')
            plt.plot(history['loss'])
            plt.plot(history['val_loss'])
            
            plt.xlabel('Epochs')
            plt.ylabel('MSE')
            plt.legend(['train', 'val'])
            
            ax = plt.subplot(223)
            ax.set_title('Covariance Matrix')
            code_cov = np.cov(np.array(encoding).transpose())
            ax = plt.matshow(code_cov, fignum=False, cmap='plasma')
            cb = plt.colorbar()
            cb.ax.tick_params(labelsize=14)
            ax.axes.get_xaxis().set_visible(False)
            
            ax = plt.subplot(224)
            ax.set_title('Code mean and std')
            
            count = 0
            for value in np.mean(encoding, axis=0):
                if abs(value) <= 0.05:
                    count += 1
                
            plt.errorbar([x for x in range(self.enc_dim)], encoding[0], encoding[1], fmt='o')
            plt.legend(['Number of zeros: %d' % count], loc='upper right')
            plt.xlabel('Encoding Dimension', fontsize=12)
            plt.ylabel('Amplitude', fontsize=12)
            
            plt.tight_layout()
            plt.savefig(file_name)
            plt.close(fig)
        except OSError:
            self.logger.write_message('Evaluation image could not be saved under %s.' % file_name, MessageType.ERR)
        plt.close(fig)