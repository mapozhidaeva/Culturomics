from google_ngram_downloader import readline_google_store
from string import punctuation
import re
import csv
import prefixTrie

# функция,выгружающая нграмы до и после 1918 года в разные таблицы
# на вход подаются параметры, определяющие длину нграм, язык и индекс

def normalize(ngram):
    if '_' in ngram:
        index = ngram.find('_')
        ngram = ngram[: index]
        
    return(ngram)

# Не меняем все нерусские и находящиеся в словаре слова
def to_check(string):
    
    s = re.sub("["+punctuation+"]", '', string)
    charRe = re.compile(r'[^0-9а-яА-ЯiіІIѣ]')
#     charRe = re.compile(r'(^iI)|([a-zA-Z])')
    st = charRe.search(s)
    if bool(st):
        if len(s)>4:
            if bool(re.compile(r'[^0-9а-яА-ЯiіІIѣѵ]').search(s.replace(st.group(),''))):
                return string
        else:
            return string
    else:
        if find_prefix(root, s.lower())[0]:
            return (string)
        else:
            return ''

def load_ngrams(table_name, my_len, my_lang, my_indices, before_1918=False):
    fname, url, records = next(readline_google_store(ngram_len=my_len, lang=my_lang, indices=my_indices))
    record = next(records)
    e = 0
    count = 0
    with open('unigrams_' + my_index + '.tsv', 'w') as f:
        writer = csv.writer(f, delimiter='\t')
        while True:
            try:
                if not before_1918:
                    if record.year < 1918:
                        record = next(records)
                    elif record.year >= 1918:
                        ngram = record.ngram
                        normalized = normalize(ngram)
                        writer.writerow([my_indices,
                                         ngram,
                                         normalized,
                                         record.year,
                                         record.match_count,
                                         record.volume_count]) #(idx, raw_n_gram, n_gram, year, match_count, volume_count)"
                        if e%1000==0:
                            print('loaded: ' + str(e))  # чтобы видеть количество загрузок
                        e += 1
                        record = next(records)
                else:
                    if record.year >= 1918:
                        record = next(records)
                    elif record.year < 1918:
                        ngram = record.ngram
                        normalized = normalize(ngram)
                        new_ngram = to_check(normalized)
                        writer.writerow([my_indices,
                                         ngram,
                                         normalized,
                                         record.year,
                                         record.match_count,
                                         record.volume_count,
                                         '', #new_idx
                                        False, #is_bastard
                                        new_ngram #new_ngram]) 
                        #`idx`, `raw_n_gram`, `n_gram`, `year`, `match_count`, `volume_count`, `new_idx`, `is_bastard`, `new_ngram`
                        if e%1000==0:
                            print('loaded: ' + str(e)) # чтобы видеть количество загрузок
                        e += 1
                        record = next(records)
                 print(str(count) + " " + my_indices + " ngrams saved")
                                         
            except StopIteration:
                break
                print("StopIteration")
    
                

def load_unigrams(my_index):

    punct = punctuation+'«»—…“”*–'
    russian = "[А-Яа-я]+"
    tags = ("_ADJ", "_ADP", "_ADV", "_CONJ", "_NOUN", "_NUM", "_PRT", "_VERB", "_X")
    
    fname, url, records = next(readline_google_store(ngram_len=1, lang='rus', indices=my_index))
    record = next(records)
    count = 0

    with open('unigrams_' + my_index + '.tsv', 'w') as f:
        writer = csv.writer(f, delimiter='\t')
        while True:
            try:
                if record.year > 1918:
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
                                         
    vocabulary = open('vocabulary.txt', 'r').read() # pre-reform word forms
    russian_dic= open('russian.dic', 'r').read() #normal word forms (just in case)
    root = TrieNode('*')
                                         
    for line in vocabulary+russian_dic.split("\n"):
        add(root, line)
                                         
    for idx in unigram_indices:
        load_unigrams(idx)
        
    return 0

if __name__ == '__main__':
    main()