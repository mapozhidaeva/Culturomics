from pymystem3 import Mystem
import pandas as pd
from string import punctuation
import os

morph = Mystem()
punct_and_numbers = punctuation + '«»—…“”""*–' + '1234567890'


def get_paths():
	return ["./ngrams/" + i for i in os.listdir("./ngrams/") if i.startswith("2grams")]


def read_file(path):

	f = open(path, "r", encoding="UTF-8")
	bigrams = []
	try:
		bigrams = f.readlines()
	except UnicodeDecodeError:
		pass
	f.close()
	
	if path.endswith("0.tsv"):
		for i, line in enumerate(bigrams):
			bigrams[i] = line.strip().split("\t")
			bigrams[i][0] = ("о" + bigrams[i][0][1:])
		
	elif path.endswith("3.tsv"):
		for i, line in enumerate(bigrams):
			bigrams[i] = line.strip().split("\t")
			bigrams[i][0] = ("З" + bigrams[i][0][1:])
	else:
		for i, line in enumerate(bigrams):
			bigrams[i] = line.strip().split("\t")

	print(bigrams[:20])
	
	return bigrams


def create_lemmas_dict(bigrams):

    unique_bigrams = list({line[0] for line in bigrams if "_X" not in line[0] and "_END" not in line[0]})
    lemmas_dict = {}

    for bigram in unique_bigrams:
        clean_bigram = bigram.strip(punct_and_numbers).strip().replace(".", ' ')
        length = len([w for w in clean_bigram.split() if w])
        if length == 2:
            clean_bigram = ''.join(morph.lemmatize(clean_bigram)).strip().lower()
            lemmas_dict[bigram] = clean_bigram
            
    print("got lemmas_dict")
    
    return lemmas_dict


def lemmatize(bigrams, lemmas_dict):
	lemmatized_bigrams = []
	for line in bigrams:
		if line[0] in lemmas_dict.keys():
			line[0] = lemmas_dict[line[0]]
			lemmatized_bigrams.append(line)
	return lemmatized_bigrams


def sum_counts(lemmatized_bigrams, path):
	df = pd.DataFrame(lemmatized_bigrams, columns = ["bigram", "year", "page_count", "volume_count"])
	df[["page_count", "volume_count"]] = df[["page_count", "volume_count"]].astype(int)
	df_grouped = df.groupby(["bigram", "year"]).sum()
	directory, filename = os.path.split(path)
	new_filename = filename.split(".")[0]
	new_path = os.path.join(directory, "norm-" + new_filename + ".pkl")
	df_grouped.to_pickle(new_path)
	return 0 


def main():
	for path in get_paths():
		bigrams = read_file(path)
		lemmas_dict = create_lemmas_dict(bigrams)
		lemmatized_bigrams = lemmatize(bigrams, lemmas_dict)
		sum_counts(lemmatized_bigrams, path)
		print(path + " normalized")
	return 0


if __name__ == '__main__':
	main()
