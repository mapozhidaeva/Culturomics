# -*- coding: utf-8 -*-

from ProbMaker import probMaker
import pybktree
from Levenshtein import editops, distance
import pandas as pd
import re
from string import punctuation
from functools import reduce

class spellCorrect(object):
    """A class to correct non-dictionary words in Google Ngrams using Noisy Channel Model, Error Confusion Matrix, Damerau-Levenshtein Edit Distance and a Char Language model to help define real-word non-dictionary tokens
Usage:
Input: 'астроном1я'
Response: астрономія"""
    def __init__(self):
        """Constructor method to load external probMaker class, load dictionary and words counts """
        self.vocab = self.load_vocab()
        self.counts = self.load_counts()
        self.trie = pybktree.BKTree(distance, self.vocab)
        self.error_df = self.load_error_df()
        self.pm = probMaker(self.error_df, self.counts)
        self.l = 0
    
    def load_vocab(self):
        """Method to load dictionary from external data file."""
        print ("Loading dictionary from data file")
        vocabulary = open('vocabulary.txt', 'r').read()  # pre-reform word forms
        russian_dic = open('normal_vocabulary.txt', 'r').read()  #normal word forms
        return list(set([word.lower() for word in vocabulary.split("\n")+russian_dic.split("\n") if len(word)>4]))

    def load_counts(self):
        """Method to load counts from external data file."""
        print("Loading counts")
        counts = {}
        lines = open('counts.txt', 'r').read().split("\n")
        for line in lines:
            if line:
                l = line.split()
                key, value = l[0],l[1]
                counts[key] = value
        return counts

    def load_error_df(self):
        """Method to load a dataframe containing  from external data file."""
        print("Loading error dataframe")
        error_df = pd.read_csv('error_df.csv')
        return error_df

    def gen_candidates(self, word):
        """Method to generate set of candidates for a given word using Damerau-Levenshtein Edit Distance of 1 and 2"""
        return self.trie.find(word.lower(), 2)
    
    def get_best(self, error):
        """Method to calculate channel model probability for errors."""
        candidates = self.gen_candidates(error)
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
    
    def to_check(self, string):
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
    #         if s.lower() in vocab:
                return string
            else:
                if self.l>0:
                    if seqProb(s.lower())>self.l:
                        return string
                    else:
                        return self.return_upper(self.get_best(string),string)
                else:
                    return self.return_upper(self.get_best(string),string)
                # why not lower? because upper and lower characters look differently 
                # and can be recognised as different symbols
                
    def return_upper(self,w,e):
        if e.isupper():
            return w.upper()
        else:
            if e[0].isupper():
                return w[0].upper()+w[1:]
            else:
                return w