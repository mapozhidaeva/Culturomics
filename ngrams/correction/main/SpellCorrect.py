from ProbMaker import probMaker
import pybktree
from Levenshtein import editops, distance

class spellCorrect(object):
    """A class to correct non-dictionary words in Google Ngrams using Noisy Channel Model, Error Confusion Matrix, Damerau-Levenshtein Edit Distance and a Char Language model to help define real-word non-dictionary tokens
Usage:
Input: 'астроном1я'
Response: астрономия"""
    def __init__(self):
        """Constructor method to load external probMaker class, load dictionary and words counts """
        self.vocab = self.load_vocab()
        self.counts = self.load_counts()
        self.trie = pybktree.BKTree(distance, vocab)
        self.error_df = self.load_error_df()
        self.pm = probMaker(self.error_df, self.counts)
        
    
    def load_vocab(self):
        """Method to load dictionary from external data file."""
        print "Loading dictionary from data file"
        vocabulary = open('vocabulary.txt', 'r').read() # pre-reform word forms
        russian_dic= open('normal_vocabulary', 'r').read() #normal word forms
        return list(set([word.lower() for word in vocabulary.split("\n")+russian_dic.split("\n") if len(word)>4]))
    
    def load_error_df(self)
        """Method to load a dataframe containing  from external data file."""
        error_df = pd.read_csv('error_df.csv')
        
    def gen_candidates(self, word):
        """Method to generate set of candidates for a given word using Damerau-Levenshtein Edit Distance of 1 and 2"""
        return tree.find(word, 2)
    
    def get_best(self, error, candidates):
        """Method to calculate channel model probability for errors."""
        p = [0]*len(candidates)
        for i, candidate in enumerate(candidates):
            editop, w_idx, e_idx = editops(candidate[-1],error)
            if editop == 'replace':
                e=pair[1][e_idx]
                w=pair[0][w_idx]
            elif editop == 'insert':
                e=pair[1][e_idx-1:e_idx+1]
                w=pair[0][w_idx-1]
            elif editop == 'delete':
                if idxx!=0:
                    e=pair[1][e_idx-1]
                    w=pair[0][w_idx-1:w_idx+1]
                else:
                    e=pair[1][e_idx]
                    w=pair[0][w_idx:w_idx+2]
            p[i] = self.pm.P_w(candidate)*self.P_ew(editop,e,w)
            return(max(p))