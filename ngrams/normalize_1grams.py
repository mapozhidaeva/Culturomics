# нужно еще лемматизировать extra ngrams
# сложить нграммы 0 с о и 3 с з. 

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
	except UnicodeDecodeError:
		pass
	f.close()

	
	if path.endswith("0.tsv"):
		for i, line in enumerate(unigrams):
			unigrams[i] = line.strip().split("\t")
			unigrams[i][0] = unigrams[i][0].lower().replace("0", "о")
		
	elif path.endswith("3.tsv"):
		for i, line in enumerate(unigrams):
			unigrams[i] = line.strip().split("\t")
			unigrams[i][0] = unigrams[i][0].lower().replace("3", "з")
	else:
		for i, line in enumerate(unigrams):
			unigrams[i] = line.strip().split("\t")

	print(unigrams[:20])
	
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
				print(clean_unigram)
				lemmas_dict[unigram] = clean_unigram
			elif length == 2:
				extra_bigrams.append(unigram)
			elif length == 3:
				extra_trigrams.append(unigram)

	print("got lemmas_dict")

	return lemmas_dict, extra_bigrams, extra_trigrams


def lemmatize(unigrams, lemmas_dict):
	lemmatized_unigrams = []
	for line in unigrams:
		if line[0] in lemmas_dict.keys():
			line[0] = lemmas_dict[line[0]]
			lemmatized_unigrams.append(line)

	print("got lemmatized_unigrams")

	return lemmatized_unigrams


def sum_counts(lemmatized_unigrams, path):
	df = pd.DataFrame(lemmatized_unigrams, columns = ["unigram", "year", "page_count", "volume_count"])
	df[["page_count", "volume_count"]] = df[["page_count", "volume_count"]].astype(int)
	df_grouped = df.groupby(["unigram", "year"]).sum()
	directory, filename = os.path.split(path)
	new_filename = filename.split(".")[0]
	new_path = os.path.join(directory, "norm-" + new_filename + ".pkl")
	df_grouped.to_pickle(new_path)
	return filename, directory 


def write_tsv(path, unigrams, extra_ngrams):
	with open(path, 'w', encoding="UTF-8", newline='') as f:
		writer = csv.writer(f, delimiter='\t')
		for line in unigrams:
			if line[0] in extra_ngrams:
				line[0] = line[0].strip(punct_and_numbers).replace(".", ' ')
				writer.writerow(line)


def save_extra(unigrams, extra_bigrams, extra_trigrams, filename, directory):
	
	new_filename = "2grams-" + filename.split("_")[-1]
	new_path = os.path.join(directory, 'extra', new_filename)
	write_tsv(new_path, unigrams, extra_bigrams)
	print("extra bigrams saved")

	new_filename = "3grams-" + filename.split("_")[-1]
	new_path = os.path.join(directory, 'extra', new_filename)
	write_tsv(new_path, unigrams, extra_trigrams)
	print("extra trigrams saved")


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
