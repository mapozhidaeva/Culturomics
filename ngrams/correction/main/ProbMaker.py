import pandas as pd
from Levenshtein import editops, distance
from collections import Counter
from sklearn.metrics import confusion_matrix
import numpy as np

class probMaker(object):
    
    def __init__(self, error_df, counts):
        self.counts = counts
        self.error_df = error_df
        self.sub_mtrx, self.sub_labels = confusion_mtrx('replace')
        self.ins_mtrs, self.ins_labels = confusion_mtrx('insert')
        self.del_mtrx, self.del_labels = confusion_mtrx('delete')
        
    def P_w(w):
        '''Calculate P(word)'''
        
        N = sum(counts.values())
        return counts[w] / N

    def P_ew(editop, e, w):
        '''Calculate P(e|w)'''
        
        if editop=='replace':
            return check_cofusion_mtrx(self.sub_labels,self.sub_mtrx,ew)
        elif editop=='insert':
            return check_cofusion_mtrxx(ins_labels,confusion_matrix(correct_ins_elements, error_ins_elements),ew)
        elif editop=='delete':
            return check_cofusion_mtrx(ins_labels,confusion_matrix(correct_dels_elements, error_dels_elements),ew)
        else:
            return 0.0001 # костыль

    def check_cofusion_mtrx(labels,cm,e, w):
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

    def confusion_mtrx(editop):
        '''Building confusion matrices of the checked partition of data'''
               
        df = pd.concat([self.error_df[error_df['editop']==editop], \
                        self.error_df[error_df['editop']=='equal']], axis=0, ignore_index=True)
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
        return np.add(1, confusion_matrix(correct_elements, error_elements)),\ # with smoothing
               sorted(list(set(correct_elements+error_elements))) 