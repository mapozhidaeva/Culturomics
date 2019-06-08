# -*- coding: utf-8 -*-
### TODO: определить model, dataset,

from ProbMaker import probMaker
import sys
sys.path[0:0] = ['../model']
from SeqProb import seq_prob
import pybktree
from Levenshtein import editops, distance
import pandas as pd
import re
from string import punctuation
from functools import reduce
from Utils import read_corpus, CharDataset

class spellCorrect(object):
    """A class to correct non-dictionary words in Google Ngrams using Noisy Channel Model, Error Confusion Matrix, Damerau-Levenshtein Edit Distance and a Char Language model to help define real-word non-dictionary tokens
Usage:
Input: 'астроном1я'
Response: астрономія"""
    def __init__(self, V=None, model=None):
        """Constructor method to load external probMaker class, load dictionary and words counts """
        self.vocab = self.load_vocab()
        self.counts = self.load_counts()
        self.trie = pybktree.BKTree(distance, self.vocab)
        self.error_df = self.load_error_df()
        self.pm = probMaker(self.error_df, self.counts)
        self.V = V
        self.model = model
    
    def load_vocab(self):
        """Method to load dictionary from external data file."""
        print ("Loading dictionary from data file")
        vocabulary = open('../data/vocabulary.txt', 'r').read()  # pre-reform word forms
        russian_dic = open('../data/normal_vocabulary.txt', 'r').read()  #normal word forms
        return list(set([word.lower() for word in vocabulary.split("\n")+russian_dic.split("\n") if len(word)>4]))

    def load_counts(self):
        """Method to load counts from external data file."""
        print("Loading counts")
        counts = {}
        lines = open('../data/counts.txt', 'r').read().split("\n")
        for line in lines:
            if line:
                l = line.split()
                key, value = l[0],l[1]
                counts[key] = value
        return counts

    def load_error_df(self):
        """Method to load a dataframe containing  from external data file."""
        print("Loading error dataframe")
        error_df = pd.read_csv('../data/error_df.csv')
        return error_df

    def gen_candidates(self, word):
        """Method to generate set of candidates for a given word using Damerau-Levenshtein Edit Distance of 1 and 2"""
        return self.trie.find(word.lower(), 2)
    
    def get_best(self, error):
        """Method to calculate channel model probability for errors."""
        candidates = self.gen_candidates(error.lower())
        p = [0]*len(candidates)
        for i, candidate_ in enumerate(candidates):
            candidate = candidate_[-1]
            p_ew_candidate = []
            for res in editops(candidate,error):
                editop, w_idx, e_idx = res
                if editop == 'replace':
                    e=error[e_idx]
                    w=candidate[w_idx]
                elif editop == 'insert':
                    e=error[e_idx-1:e_idx+1]
                    w=candidate[w_idx-1]
                elif editop == 'delete':
                    if e_idx!=0:
                        e=error[e_idx-1]
                        w=candidate[w_idx-1:w_idx+1]
                    else:
                        e=error[e_idx]
                        w=candidate[w_idx:w_idx+2]
                else:
                    print(editops(candidate,error))
                    return error 
                p_ew_candidate.append(self.pm.P_ew(editop,e,w))
            p[i] = self.pm.P_w(candidate)*reduce(lambda x, y: x*y, p_ew_candidate)/len(p_ew_candidate)
        try:    
            best_idx = p.index(max(p))
            return(candidates[best_idx][-1])
        except ValueError:
            return error
            print(editops(candidate,error))
    
    def to_check(self, string, seqprob, upper_boundary=0, lower_boundary=0):
        '''Rid of non-cyrilic words, 
        words with len < 5, 
        dictionary words 
        and words with probability>? of being a non-error word given by the language model'''

        if len(string)<5:
            return string
        # alphanumeric words stay the same
        s = re.sub("[.,:\'-]", '', string)
        charRe = re.compile(r'[^a-zA-Z0-9.]')
        st = charRe.search(s)

        if not bool(st):
            return string
        else:
            # vocab words stay the same
            if self.trie.find(s.lower(), 0):
                return string
            else:
                if upper_boundary>0 and lower_boundary>0:
                    if not seqprob:
                        dataset = CharDataset([string], V=self.V)
                        seqprob = seq_prob(self.model, dataset, self.V)
                        
                    if seqprob<=upper_boundary or seqprob>=lower_boundary:
                        self.correction = self.return_upper(self.get_best(string),string)
                        return self.correction
                    else:
                        self.correction = self.return_upper(self.get_best(string),string)
                        if self.rules(self.correction, string):
                            return self.correction
                        else:
                            return string
                else:
                    return self.return_upper(self.get_best(string),string)
                
    def return_upper(self,w,e):
        if e.isupper():
            return w.upper()
        else:
            if e[0].isupper():
                return w[0].upper()+w[1:]
            else:
                return w
            
    def rules(self, w, e):
        if len(e)>4:
            rule1 = e[-1] in 'шщцЦШЩ'
            rule2 = any(i.isdigit() for i in e)
            rule3 = e[-2] in 'щшцЩШЦ' and e[-1] in 'июяИЮЯ'
            rule4 = 'ѣ' or 'Ѣ'  in w
            if rule1 or rule2 or rule3 or rule4:
              return True
        return False
