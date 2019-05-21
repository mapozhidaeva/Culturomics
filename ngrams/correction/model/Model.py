"""
Character Language Model for generating probabilities of sequences
"""
import sys
import torch
import torch.nn as nn
import torch.nn.utils
import torch.nn.functional as F
from torch.utils.data.dataset import Dataset
from torch.utils.data.dataloader import DataLoader


class CharLM(nn.Module):
    """ Character Language Model:
        - Embedding Layer
        - Unidirection LSTM Layer
        - Fully Connected Layer
    """
    def __init__(self, vocab, embed_dim=27,
                 hidden_dim=128, drop_prob=0.2, n_layers=2):
        """ Init Language Model.

        @param embed_dim (int): Embedding size (dimensionality)
        @param hidden_dim (int): Hidden Size (dimensionality)
        @param vocab (Vocab): Vocabulary object containing src and tgt languages
                              See Vocab.py for documentation.
        @param drop_prob (float): Dropout probability, for lstm
        """
        super(CharLM, self).__init__()
        self.embed_dim = embed_dim
        self.hidden_dim = hidden_dim
        self.drop_prob = drop_prob
        self.vocab = vocab
        self.n_layers = n_layers

        self.emb = nn.Embedding(vocab.vocab_size, emb_dim)
        self.lstm = nn.LSTM(self.embed_dim, hidden_dim, num_layers=n_layers, batch_first=True)
        self.fc = nn.Linear(in_features=hidden_dim*vocab.pad_len, out_features=vocab.vocab_size*vocab.pad_len)

    def forward(self, input_seq):
        """ Take a mini-batch of source and target sentences, compute the log-likelihood of
        target sentences under the language models learned by the NMT system.

        @param imput_seq: source sentence tokens, wrapped by `^` and `$` (start and end of word)

        @returns scores (Tensor): a tensor of shape (batch size, vocab size, word len)
        """
        # torch.Size([64, 27])
        embeded = self.emb(input_seq).view(-1, self.vocab.pad_len, self.emb_dim)
        # torch.Size([64, 27, 27]) or torch.Size([1, 27, 27])
        out, hidden = self.lstm(embeded)
        # torch.Size([64, 27, 1024])
        batch_size, seq_size, hidden_size = out.shape
        out = out.contiguous().view(batch_size, seq_size * hidden_size)
        # torch.Size([64, 13824])
        out = self.output(out).view(-1, self.vocab.pad_len, self.vocab.vocab_size)
        # torch.Size([64, 27, 55])
        final = F.softmax(out, dim=-1)
        # torch.Size([64, 27,55])
        return final

    @property
    def device(self) -> torch.device:
        """ Determine which device to place the Tensors upon, CPU or GPU.
        """
        return torch.device('cuda:0' if torch.cuda.is_available() else 'cpu')

    @staticmethod
    def load(model_path: str='old_rus_lm.pth'):
        """ Load the model from a file.
        @param model_path (str): path to model
        """
        params = torch.load(model_path, map_location=lambda storage, loc: storage)
        args = params['args']
        model = CharLM(vocab=params['vocab'], **args)
        model.load_state_dict(params['state_dict'])

        return model

    def save(self, path: str='old_rus_lm.pth'):
        """ Save the odel to a file.
        @param path (str): path to the model
        """
        print('save model parameters to [%s]' % path, file=sys.stderr)

        params = {
            'args': dict(embed_dim=self.embed_dim, hidden_dim=self.hidden_dim,
                         drop_prob=self.drop_prob, n_layers=self.n_layers),
            'vocab': self.vocab,
            'state_dict': self.state_dict()
        }

        torch.save(params, path)
