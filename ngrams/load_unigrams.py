from google_ngram_downloader import readline_google_store
from string import punctuation
import re
import csv

punct = punctuation+'«»—…“”*–'
russian = "[А-Яа-я]+"


def load_unigrams(my_index):

    tags = ("_ADJ", "_ADP", "_ADV", "_CONJ", "_NOUN", "_NUM", "_PRT", "_VERB", "_X")
    fname, url, records = next(readline_google_store(ngram_len=1, lang='rus', indices=my_index))
    record = next(records)
    count = 0

    with open('unigrams_' + my_index + '.tsv', 'w') as f:
        writer = csv.writer(f, delimiter='\t')
        while True:
            try:
                if record.year < 1918:
                    record = next(records)
                else:
                    if len(record.ngram.strip(punct)) > 2 \
                            and re.search(russian, record.ngram) \
                            and not record.ngram.endswith(tags):
                        writer.writerow([record.ngram,
                                        record.year,
                                        record.match_count,
                                        record.volume_count])
                        count += 1
                        record = next(records)
                    else:
                        record = next(records)
            except StopIteration:
                break

    print(str(count) + " " + my_index + " ngrams saved")
    return 0


def main():
    unigram_indices = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9',
                       'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j',
                       'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't',
                       'u', 'v', 'w', 'x', 'y', 'z', 'other']
    for indx in unigram_indices:
        load_unigrams(indx)
    return 0

if __name__ == '__main__':
    main()

