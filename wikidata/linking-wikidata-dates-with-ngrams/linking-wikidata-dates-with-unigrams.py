import pandas as pd
import numpy as np
from matplotlib import pyplot as plt
from sklearn.preprocessing import scale

ABS_FREQ = pd.read_csv('relative_frequencies.csv')

def read_normalized_ngrams(path:str):
	df = pd.read_pickle(path)
	df.reset_index(inplace = True)
	df = df.groupby(['unigram', 'year']).page_count.sum().unstack().reset_index()

	# save ngrams which sum > 40
	df = df.fillna(0)
	df['freq_sum'] = df.iloc[:,1:].sum(axis=1)
	df = df[df["freq_sum"] > 40]
	df = df.sort_values('freq_sum', ascending=False).reset_index(drop=True)
	return df


def get_relative_counts(df):
	year_columns = list(df.columns[1:-1])
	abs_counts = ABS_FREQ[ABS_FREQ.year.isin(year_columns)]
	abs_counts = list(abs_counts.match_count)
	rel_counts = df.iloc[:, 1:-1] / abs_counts
	for i in rel_counts:
		df[i] = rel_counts[i]
	return df


def apply_window_mean_and_get_z_scores(df):
	window_mean = df.iloc[:, 1:-1].rolling(window=5, axis=1).mean()
	diff_window_mean = window_mean.diff(axis=1)
	diff_window_mean = diff_window_mean[diff_window_mean > 0]
	z_scores = diff_window_mean.apply(lambda ngram: scale(ngram,
												 			axis=0,
															with_mean=True, 
															with_std=True,
															copy=False),
														axis=1)
	z_scores_df = pd.DataFrame.from_records(z_scores, 
											columns = list(window_mean.columns))
	return z_scores_df


def filter_outlier_years(z_scores_df, norm_df):

	z_scores_df = z_scores_df[z_scores_df > 1.65] 
	z_scores_window_mean_df = pd.concat([norm_df.iloc[:, 0], z_scores_df, norm_df.iloc[:, -1]], axis=1)
	z_scores_window_mean_df.fillna(0, inplace=True)
	
	filtered_unigrams = {i:[] for i in list(z_scores_window_mean_df.unigram)}
	
	for i in z_scores_window_mean_df.index:
		years_df = z_scores_window_mean_df.iloc[i, 1:-1][z_scores_window_mean_df.iloc[i, 1:-1] != 0]
		years = list(years_df.index)
		filtered_unigrams[z_scores_window_mean_df.iloc[i, 0]] = years
			
	return filtered_unigrams


def filter_periods(norm_df, filtered_unigrams:dict):
	
	window_mean = norm_df.iloc[:, 1:-1].rolling(window=5, axis=1).mean()
	diff_window_mean = window_mean.diff(axis=1)
	positive_diff = diff_window_mean[diff_window_mean > 0]
	positive_diff.fillna(0, inplace=True)
	positive_diff_df = pd.concat([norm_df.iloc[:, 0], 
								 positive_diff, 
								 norm_df.iloc[:, -1]], axis=1)
	
	# join years of frequency growth in periods

	for i in positive_diff_df.index:
	
		target_years = []
		years_df = positive_diff_df.iloc[i, 1:-1][positive_diff_df.iloc[i, 1:-1] != 0]
		years = [int(i) for i in list(years_df.index)[::-1]]

		# код ниже позволяет объединить годы, 
		# где есть положительная разница относительных частот, 
		# в связки, и потом в периоды (с ... по ...)
		
		j = 0
		current_period = []
		while j < len(years)-1:
			if years[j] - years[j+1] == 1:
				current_period.append(years[j])
			elif years[j] - years[j+1] > 1:
				current_period.append(years[j])
				if current_period != []:
					target_years.append(current_period)
				current_period = []
			j += 1
		if j == len(years)-1:
			if current_period != [] and ( current_period[-1] - years[len(years)-1] == 1):
				current_period.append(years[len(years)-1])
				target_years.append(current_period)
				current_period = []
			else:
				current_period.append(years[len(years)-1])
		if current_period != []:
			target_years.append(current_period)  
				
		result_years = []
		for years in target_years:
			if len(years) > 1:
				start_year, end_year = years[-1], years[0]
				result_years.append([start_year, end_year])

		filtered_unigrams[positive_diff_df.iloc[i, 0]].append(result_years)

	return filtered_unigrams


def delete_empty_values(filtered_unigrams:dict):

	to_del = []
	for k,v in filtered_unigrams.items():
		if v == [[]]:
			to_del.append(k)
	for i in to_del:
		del filtered_unigrams[i]

	return filtered_unigrams

def read_wikidata_results(path:str, filtered_unigrams:dict):

	with open(path) as f:
		wikidata = pd.read_csv(f, sep="\t")

	wikidata = wikidata[["Unigram", "#Q", "Subject", "#P", 
				"Predicate", "Object", "Organization", 
				"Just Date", "Start Time", "End Time", "Time Point"]]

	for i in wikidata.index:
		if str(wikidata["Object"][i]).startswith("http:"):
			wikidata = wikidata[wikidata.index != i]

	wikidata = wikidata.sort_values("Unigram")
	wikidata = wikidata[wikidata["Unigram"].isin(filtered_unigrams.keys())]    
	wikidata.fillna(0, inplace=True)
	wikidata_list = wikidata.values.tolist()

	return wikidata_list

def match_dates(filtered_unigrams:dict, wikidata_list:list):
	result_entries = []
	for unigram, dates in filtered_unigrams.items():
		for entry in wikidata_list: 
		# из каждой строки в списке берем только годы, 
		# сравниваем их с годами в словаре, если есть соответствие, 
		# добавляем всю строку Викиданных в новый список
		# погрешность - 2 года: например, рост частотности нграмы в 1965 году, в Викиданных мы смотрим 1965, 1964, 1963
			if unigram == entry[0]:
				only_wiki_years = []
				try:
					only_wiki_years = [int(str(i)[:4]) for i in entry[-4:]]
				except ValueError:
					pass
				for date in dates:
					if isinstance(date, str) and only_wiki_years != []:
						date = int(date)
						for wiki_year in only_wiki_years:
							if date == wiki_year or date-1 == wiki_year or date-2 == wiki_year or date-100 == wiki_year or date-50 == wiki_year:
								result_entries.append([date] + entry)
					if isinstance(date, list) and only_wiki_years != []:
						for date_pair in date:
							year_1, year_2 = date_pair[0], date_pair[1]
							for year in only_wiki_years:
								if int(year_1) <= int(year) < int(year_2):
									result_entries.append([date_pair] + entry)

	result_wiki_dates = pd.DataFrame(result_entries, columns = ["Year or Period", "Unigram", "#Q", "Subject", "#P", "Predicate", "Object", "Organization", 
								  "Just Date", "Start Time", "End Time", "Time Point"])

	result_wiki_dates = result_wiki_dates.drop_duplicates(subset = ["Unigram", "#Q", "Subject", "#P", "Predicate", "Object", "Organization", 
								  "Just Date", "Start Time", "End Time", "Time Point"], keep = "first")

	result_wiki_dates.sort_values("Unigram", inplace=True)
	result_wiki_dates = result_wiki_dates.reset_index(drop=True)

	return result_wiki_dates


def add_growth_speed_values(z_scores_window_mean_df, result_wiki_dates, norm_df):
	z_scores_df = pd.concat([norm_df.iloc[:, 0:2], 
							 z_scores_window_mean_df, 
							 norm_df.iloc[:, -1]], 
							 axis=1)
	result_wiki_dates["growth_speed"] = [None for i in result_wiki_dates.index]
	for i in result_wiki_dates.index:
		val = 0.0
		entry = result_wiki_dates.iloc[i, :].tolist()
		if isinstance(entry[0],int): 
			# one year growth
			val = float(z_scores_df[z_scores_df.unigram == entry[1]].loc[:, str(entry[0])])
		elif isinstance(entry[0], list):
			# period of growth - mean
			years = entry[0]
			val = float(z_scores_df[z_scores_df.unigram == entry[1]].loc[:, str(years[0]):str(years[1])].mean(axis=1))
		result_wiki_dates.iloc[i,-1:] = val

	return result_wiki_dates



def main():
	# dates-unigrams_g.tsv, norm-unigrams_g.pkl
	# items_list = [i for i in "rstufvwxyz"] + [str(i) for i in range(10)]
	items_list = [i for i in "yz"]
	for item in items_list:
		norm_unigrams_path = "norm-unigrams_{}.pkl".format(item)
		try:
			norm_df = read_normalized_ngrams(norm_unigrams_path)
			print("Processing unigrams starting with letter \"{}\"".format(item))
			norm_df = get_relative_counts(norm_df)
			z_scores_df = apply_window_mean_and_get_z_scores(norm_df)
			filtered_unigrams = filter_outlier_years(z_scores_df, norm_df)
			filtered_unigrams = delete_empty_values(filter_periods(norm_df, filtered_unigrams))
			print("Filtered unigrams: {}".format(len(filtered_unigrams)))
			wikidata_path = "dates-unigrams_{}.tsv".format(item)
			wikidata_list = read_wikidata_results(wikidata_path, filtered_unigrams)
			result_wiki_dates = match_dates(filtered_unigrams, wikidata_list)
			result_df = add_growth_speed_values(z_scores_df, result_wiki_dates, norm_df)
			print("{} unique unigrams in final dataframe".format(str(result_df["Unigram"].nunique())))
			result_df.to_csv("unigram-result-dates_{}.tsv".format(item), sep="\t", index = False)
			print("Unigrams saved!")
		except FileNotFoundError:
			continue



if __name__ == '__main__':

	main()         



























