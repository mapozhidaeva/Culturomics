import numpy as np
import pandas as pd
from Levenshtein import editops, distance
from collections import Counter
from sklearn.metrics import confusion_matrix

class probMaker(object):
    
    def __init__(self, error_df, counts):
        self.counts = counts
        self.error_df = error_df
        self.sub_mtrx, self.sub_labels = self.confusion_mtrx('replace')
        self.ins_mtrx, self.ins_labels = self.confusion_mtrx('insert')
        self.del_mtrx, self.del_labels = self.confusion_mtrx('delete')
        
    def P_w(self, w):
        '''Calculate P(word)'''
        
        N = sum(list(map(int,self.counts.values())))
        if w in self.counts:
            return (int(self.counts[w]) + 1) / (N + len(self.counts)) # лаплассовское сглаживание?
        else:
            return 1/(N + len(self.counts))

    def P_ew(self, editop, e, w):
        '''Calculate P(e|w)'''
        
        if editop=='replace':
            return self.check_cofusion_mtrx(self.sub_labels,self.sub_mtrx,e,w)
        elif editop=='insert':
            return self.check_cofusion_mtrx(self.ins_labels,self.ins_mtrx,e,w)
        elif editop=='delete':
            return self.check_cofusion_mtrx(self.del_labels,self.del_mtrx,e,w)
        else:
            return 0.0001 # костыль

    def check_cofusion_mtrx(self,labels,cm,e, w):
        if e in labels:
            if w in labels:
                e_idx = labels.index(e)
                w_idx= labels.index(w)
                return(cm[w_idx, e_idx]/(sum(cm[w_idx,:])))
        else:
            if w in labels:
                w_idx= labels.index(w)
                return(1/(sum(cm[:, w_idx])))
        return(1/(cm.shape[0]*cm.shape[1])) 

    def confusion_mtrx(self, editop):
        '''Building confusion matrices of the checked partition of data'''
        error_df = self.error_df       
        df = pd.concat([error_df[error_df['editop']==editop], \
                        error_df[error_df['editop']=='equal']], axis=0, ignore_index=True)
        correct_tokens = [list(word[:int(df.idxw.iloc[[i]])]) + \
                          [df['e|w'].iloc[[i]][i][df['e|w'].iloc[[i]][i].find('|')+1:]] + \
                          list(word[int(df.idxw.iloc[[i]]) + \
                                    len(df['e|w'].iloc[[i]][i][df['e|w'].iloc[[i]][i].find('|')+1:]):]) \
                          for i, word in enumerate(df['correction'].astype(str).tolist())]
               
        correct_elements = [el for token in correct_tokens for el in token if el]
               
        error_tokens = [list(word[:int(df.idxe.iloc[[i]])]) + \
                        [df['e|w'].iloc[[i]][i][:df['e|w'].iloc[[i]][i].find('|')]] + \
                        list(word[int(df.idxe.iloc[[i]])+len(df['e|w'].iloc[[i]][i][:df['e|w'].iloc[[i]][i].find('|')]):]) \
                        for i, word in enumerate(df['error'].astype(str).tolist())]
        error_elements = [el for token in error_tokens for el in token if el]
        return np.add(1, confusion_matrix(correct_elements, error_elements)),\
               sorted(list(set(correct_elements+error_elements))) # with smoothing