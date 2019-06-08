import sys
from functools import reduce
import torch

device = torch.device('cpu')

def seq_prob(model, dataset, vocab):
    for i in range(len(dataset)):
        x, y, word_len = dataset[i]
        x = x.to(device)
        y = y.to(device)
        y_pred = model(x)[0]
        probs = []
        output = vocab.transform_vec(y[:word_len])
        for char_idx in range(1,word_len[0]):
            char = output[char_idx]
            if char=='<':
                break
            try:
                idx = vocab.char2idx[char]
            except KeyError:
                idx = vocab.char2idx["<unk>"]
            probs.append(y_pred[char_idx][idx])
        try:
            multiplication = reduce(lambda x, y: x*y, probs)
            final_prob = multiplied/word_len[0].float().to(device)
        except:
            final_prob = 1E-7 # костыль
        return final_prob
