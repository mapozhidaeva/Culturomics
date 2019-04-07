# сначала пишем скрипт для нормализации униграм
# потом смотрим на файлы, начинающиеся с цифр, и вообще на нормализованные файлы 
# потом раскладываем по файликам экстра биграмы и триграмы


from pymystem3 import Mystem
import pandas as pd
from string import punctuation
import csv
import os

morph = Mystem()
punct_and_numbers = punctuation + '«»—…“”""*–' + '1234567890'

def get_paths():
	return ["./unigrams/" + i for i in os.listdir("./unigrams/") if i.startswith("unigrams")]


def read_file(path):
	f = open(path, "r", encoding="UTF-8")
	unigrams = []
	try:
		unigrams = f.readlines()
		for i, line in enumerate(unigrams):
			unigrams[i] = line.strip().split("\t")
	except UnicodeDecodeError:
		pass
	f.close()
	return unigrams


def create_lemmas_dict(unigrams):

	unique_unigrams = list({line[0] for line in unigrams})

	lemmas_dict = {}
	extra_bigrams = []
	extra_trigrams = []

	for unigram in unique_unigrams:
		clean_unigram = unigram.strip(punct_and_numbers).replace(".", ' ')
		if len(clean_unigram) > 2:
			length = len(clean_unigram.split())
			if length == 1:
				clean_unigram = ''.join(morph.lemmatize(clean_unigram)).strip().lower()
				lemmas_dict[unigram] = clean_unigram
			elif length == 2:
				extra_bigrams.append(unigram)
			elif length == 3:
				extra_trigrams.append(unigram)

	return lemmas_dict, extra_bigrams, extra_trigrams


def lemmatize(unigrams, lemmas_dict):
	lemmatized_unigrams = []
	for line in unigrams:
		if line[0] in lemmas_dict.keys():
			line[0] = lemmas_dict[line[0]]
			lemmatized_unigrams.append(line)
	return lemmatized_unigrams


def sum_counts(lemmatized_unigrams, path):
	df = pd.DataFrame(lemmatized_unigrams, columns = ["unigram", "year", "page_count", "volume_count"])
	df[["page_count", "volume_count"]] = df[["page_count", "volume_count"]].astype(int)
	df_grouped = df.groupby(["unigram", "year"]).sum()
	directory, filename = os.path.split(path)
	new_path = os.path.join(directory, "norm-" + filename)
	df_grouped.to_csv(new_path, sep='\t')
	return filename, directory 


def write_tsv(path, unigrams, ngrams):
	with open(path, 'w') as f:
		writer = csv.writer(f, delimiter='\t')
		for line in unigrams:
			if line[0] in ngrams:
				line[0] = line[0].strip(punct_and_numbers).replace(".", ' ')
				writer.writerow(line)


def save_extra(unigrams, extra_bigrams, extra_trigrams, filename, directory):
	
	new_filename = "2grams_" + filename.split("_")[-1]
	new_path = os.path.join(directory, 'extra', new_filename)
	write_tsv(new_path, unigrams, extra_bigrams)

	new_filename = "3grams_" + filename.split("_")[-1]
	new_path = os.path.join(directory, 'extra', new_filename)
	write_tsv(new_path, unigrams, extra_trigrams)

	return 0


def main():
	for path in get_paths():
		unigrams = read_file(path)
		lemmas_dict, extra_bigrams, extra_trigrams = create_lemmas_dict(unigrams)
		lemmatized_unigrams = lemmatize(unigrams, lemmas_dict)
		filename, directory = sum_counts(lemmatized_unigrams, path)
		save_extra(unigrams, extra_bigrams, extra_trigrams, filename, directory)
		print(path + " normalized")
	return 0


if __name__ == '__main__':
	main()

