import torch


class CharDataset(Dataset):
    def __init__(self, data, V):
        super(Dataset).__init__()
        self.V = V
        self.chars = V.chars
        self.data = data
        self.pad_len = V.pad_len

    def __len__(self):
        return len(self.data)

    def __getitem__(self, idx):
        word = self.data[idx]
        indices = self.V.transform_one(word)
        x = torch.ones((self.pad_len), dtype=torch.int64)
        y = torch.ones((self.pad_len), dtype=torch.int64)
        mask = torch.zeros((1,), dtype=torch.int64)
        word_len = min(len(indices), self.pad_len - 1)
        for idx_i, i in enumerate(indices[:word_len - 1]):
            x[idx_i + 1] = i

        for idx_i, i in enumerate(indices[:word_len]):
            y[idx_i] = i

        mask[0] = word_len + 1

        x[0] = self.V.char2idx["^"]
        y[word_len] = self.V.char2idx["$"]

        return x, y, mask

    def gen_input_tensor(self, letters):
        indices = self.V.transform_one(letters)
        tensor = torch.ones((self.pad_len), dtype=torch.int64)
        word_len = min(len(indices), self.pad_len)
        for idx_i, i in enumerate(indices[:word_len]):
            tensor[idx_i + 1] = i

        tensor[0] = 0

        return tensor

    def resized(self, new_size):
        return CharDataset(data=self.data[:new_size], V=self.V)

def read_corpus(file_path):
    """ Read file, where each word is dilineated by a `\n`.
    @param file_path (str): path to file containing vocabulary
    """
    vocabulary = open(file_path, 'r').read()
    data = [word for word in vocabulary.split('\n')]

    return data