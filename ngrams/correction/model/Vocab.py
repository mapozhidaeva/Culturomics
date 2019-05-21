import re

class Vocabulary:
    def __init__(self, data):
        self.AUXILIARY = ["^", "<pad>", "$", "<unk>"]
        self.data = data
        self.chars, self.char2idx, self.idx2char = self.fit(data)
        self.words, self.num_words = self.distinct_words(data)
        self.vocab_size = len(self.chars)
        self.pad_len = self.define_pad()

    def fit(self, data):
        """Extract unique symbols from the data, make itos (item to string) and stoi (string to index) objects"""
        chars = list(set(list(',-.0123456789í́абвгдеёжзийклмнопрстуфхцчшщъыьэюяіѣѳѵ') + \
                         [char for word in data for char in word if not self.not_russian(word)]))
        chars = self.AUXILIARY + sorted(chars)
        char2idx = {s: i for i, s in enumerate(chars)}
        idx2char = {i: s for i, s in enumerate(chars)}

        return chars, char2idx, idx2char

    def distinct_words(self, data):
        print('Estimating cospus size')
        words = list(set([word for word in data if len(word) > 4 and not self.not_russian(word)]))
        num_words = len(words)
        print('Done!')
        print('You can checkout the number of corpus words and the words themselves with commands .num_words, .words')
        return (words, num_words)

    def transform_all(self, words):
        """Transform list of data to list of indices
        Input:
            - data, list of strings
        Output:
            - list of lists of char indices
        """
        return [self.transform_one(word) for word in words]

    def transform_one(self, word):
        """Transform data to indices
        Input:
            - data, string
        Output:
            - list of char indices
        """
        return [self.char2idx[char] if char in self.chars else self.char2idx["<unk>"] for char in word.lower()]

    def transform_vecs(self, vecs):
        """Transform list of indices to list of data
        Input:
            - list of lists of char indices
        Output:
            - data, list of strings
        """
        return [self.transform_vec(vec) for vec in vecs]

    def transform_vec(self, vec):
        """Transform indices to data
        Input:
            - list of char indices
        Output:
            - data, string
        """
        return "".join([self.idx2char[int(idx)] for idx in vec])

    def define_pad(self):
        word_lens = [len(x) for x in self.transform_all(self.words)]
        return (max(word_lens))

    def not_russian(self, string):
        s = re.sub("[.,:\'-]", '', string)
        charRe = re.compile(r'[a-zA-Z0-9.]')
        st = charRe.search(s)
        return bool(st) or bool(re.search(r'\d', s) or bool(re.search(r'[^a-zа-яё ]+', string)))
