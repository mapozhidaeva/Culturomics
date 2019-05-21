import math
import sys
import time

import numpy as np
from tqdm import tqdm
from Utils import read_corpus, CharDataset
from Vocab import Vocabulary
from Model import CharLM

import torch
import torch.nn.utils


class MaskedLoss(nn.Module):
    def __init__(self, base_criterion=nn.CrossEntropyLoss()):
        super(MaskedLoss, self).__init__()
        self.base_criterion = base_criterion

    def forward(self, predict, target, mask):
        batch_size = predict.shape[0]
        loss = []
        for batch_id in torch.arange(batch_size):
            word_len = mask[batch_id][0]

            word_loss = torch.stack([
                self.base_criterion(
                    predict[batch_id:batch_id + 1, idx, :],
                    target[batch_id:batch_id + 1, idx]
                ) for idx in torch.arange(word_len)
            ])

            word_loss = torch.mean(word_loss)
            loss.append(word_loss)
        loss = torch.mean(torch.stack(loss))
        return loss

def train():
    """ Train the NMT Model.
    @param args (Dict): args from cmd line
    """
    criterion = nn.CrossEntropyLoss()
    loss_func = MaskedLoss(criterion)
    optimizer = opt.Adam(lr=0.001, params=model.parameters())
    lr_sched = opt.lr_scheduler.ReduceLROnPlateau(optimizer, patience=7, verbose=True, threshold=0.001)

    train_dataset = CharDataset(V.words[:int(0.995 * (len(V.words)))], V)
    val_dataset = CharDataset(V.words[int(0.995 * (len(V.words))):], V)

    train_losses = []
    train_perplexes = []

    dev_losses = []
    dev_perplexes = []

    early_stopping_values = [999]
    early_stopping_count = 0
    early_stopping_trigger = 7

    batch_size = 64
    n_epochs = 200
    train_loader = DataLoader(dataset=train_dataset, batch_size=batch_size, num_workers=20)
    val_loader = DataLoader(dataset=val_dataset, batch_size=batch_size, num_workers=4)

    for ep in range(n_epochs):
        model.train()
        epoch_loss = []
        epoch_perplexes = []
        for x, y, mask in tqdm(train_loader, desc='Training'):
            x = x.to(device)
            y = y.to(device)
            word = model(x)
            loss = loss_func(word, y, mask)
            loss.backward()
            optimizer.step()
            optimizer.zero_grad()

            loss_value = loss.detach().cpu().numpy()
            perplexity_value = torch.pow(loss.detach(), 2).cpu().numpy()

            epoch_loss.append(loss_value)
            epoch_perplexes.append(perplexity_value)

        mean_train_loss = np.mean(epoch_loss)
        mean_train_perplexity = np.mean(epoch_perplexes)

        val_losses = []
        val_perplexes = []
        model.eval()
        with torch.no_grad():
            for x, y, mask in tqdm(val_loader, desc='Validating'):
                x = x.to(device)
                y = y.to(device)

                word = model(x)
                loss = loss_func(word, y, mask)

                loss_value = loss.cpu().numpy()
                perplexity_value = torch.pow(loss, 2).cpu().numpy()

                val_losses.append(loss_value)
                val_perplexes.append(perplexity_value)

        mean_val_loss = np.mean(val_losses)
        mean_val_perplexity = np.mean(val_perplexes)

        lr_sched.step(mean_val_loss)

        if mean_val_loss <= min(early_stopping_values):
            early_stopping_values.append(mean_val_loss)
            print("Quality improved. Saving Model.")
            torch.save(model.state_dict(), model_filename)

            early_stopping_count = 0
        else:
            early_stopping_count += 1
            early_stopping_values.append(mean_val_loss)
            if early_stopping_count >= early_stopping_trigger:
                print(f"Early stopping triggered, minimal loss reached = {min(early_stopping_values)}")
                break

        train_perplexes.append(mean_train_perplexity)
        train_losses.append(mean_train_loss)
        dev_perplexes.append(mean_val_perplexity)
        dev_losses.append(mean_val_loss)

        print(f"Epoch {ep}:\n train_loss={mean_train_loss:.5f}," \
              f" train_perplexity={mean_train_perplexity:.5f},\n" \
              f" val_loss={mean_val_loss:.5f}," \
              f" val_perplexity={mean_val_perplexity:.5f}")

def main():
    """ Main func.
    """
    # Check pytorch version
    assert (torch.__version__ == "0.4.1"), "This code is for PyTorch of version 0.4.1. You have {}".format(
        torch.__version__)

    modeOn = sys.argv[1:] or False

    # seed the random number generators
    seed = 42
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed(seed)
    np.random.seed(seed)

    data = read_corpus('../data/vocabulary.txt')
    V = Vocabulary(data)

    device = torch.device('cuda:0' if torch.cuda.is_available() else 'cpu')
    # device = torch.device('cpu')
    model = CharLM(V.vocab_size, word_len=V.pad_len, emb_dim=128, hidden_size=128)
    model.to(device)

    model_filename = "old_rus_lm.pth"

    if modeOn:
        train()
    else:
        # uncomment this line after training
        # model.load('../data/' + model_filename)
        print('Loading a model')

        model.load_state_dict(torch.load('../data/' + model_filename))

        print('Done')


if __name__ == '__main__':
    main()
