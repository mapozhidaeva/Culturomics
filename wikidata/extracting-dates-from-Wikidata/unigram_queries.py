import pandas as pd
from math import ceil
from collections import OrderedDict
import requests
import os


def getPaths():
    return [i for i in os.listdir(".") if i.startswith("norm-unigrams")]


def updateDict(dict_, ngrams, Q):  
    if isinstance(ngrams, str):
        ngram = ngrams
        if ngram not in dict_:
            dict_[ngram] = {Q}
        else:
            dict_[ngram].add(Q)
    if isinstance(ngrams, list):
        for ngram in ngrams:
            if ngram not in dict_:
                dict_[ngram] = {Q}
            else:
                dict_[ngram].add(Q)
    return 0


def parting(lst, parts): # функция делит список на указанное число частей
    part_len = ceil(len(lst)/parts)
    return [lst[part_len*k:part_len*(k+1)] for k in range(parts)]


# сначала прочтем нормализованные Викиданные из файла
def createUnigramDict():
    with open("norm-wikidata.tsv", "r", encoding="UTF-8") as f:
        f = f.readlines()

    norm_data = []
    for line in f:
        line = line.strip('\n').split(' | ')
        norm_data.append(line)
   
   #создадим словарь униграмм (сначала для тех сущностей в Викиданных, у которых 1 название из 1 слова)
    unigram_dict = {}
    for line in norm_data:
        if len(line[1:]) == 1 and len(line[1].split()) == 1:
            Q, unigram = line[0], line[1]
            updateDict(unigram_dict, unigram, Q)
        elif len(line[1:]) > 1:
            for entity_name in line[1:]:
                entity_name_split = entity_name.split()
                if len(entity_name_split) == 1:
                    Q, unigram = line[0], entity_name_split[0]
                    updateDict(unigram_dict, unigram, Q)
    return unigram_dict


# напишем функции запросов
def getSimpleTriplets(unigram, q_numbers):
    
    url = "https://query.wikidata.org/sparql"
    
    query = """SELECT ?item ?itemLabel ?predicate ?propertyLabel ?date
    WHERE
    {
      VALUES (?item) {(...)}
  
      ?item ?predicate ?date. 
      FILTER(DATATYPE(?date) = xsd:dateTime).
      MINUS { ?item schema:dateModified ?date. }
      MINUS { ?item wikibase:timestamp ?date. }
  
      BIND( IRI(REPLACE( STR(?predicate),"prop/direct/","entity/" )) AS ?property). 
      SERVICE wikibase:label { bd:serviceParam wikibase:language "ru, en". }
    }
    ORDER BY ?item ?date
    """
        
    query = query.replace('(...)', q_numbers)
    r = requests.get(url, params = {'format': 'json', 'query': query})
    data = []
    try:
        data = r.json()
    except:
        pass

    dates = []
    
    if data != []:
        for item in data['results']['bindings']:
            dates.append(OrderedDict({
                'Unigram' : unigram,
                '#Q':  item['item']['value'].split("/")[-1],
                'Subject': item['itemLabel']['value'],
                '#P': item['predicate']['value'].split("/")[-1],
                'Predicate': item['propertyLabel']['value'],
                'Object': '',
                'Organization': '',
                'Just Date': str(item['date']['value'])[:-10],
                'Time Point' : '',
                'Start Time' : '',
                'End Time' : ''})) 
            
    if dates != []:
        for date in dates:
            if date["Object"].startswith("http"): # удаляем предикаты с ссылками
                dates.remove(date)
        df = pd.DataFrame(dates)
        return df



def getStartEnd(unigram, q_numbers):
    
    url = "https://query.wikidata.org/sparql"
    
    query = """SELECT ?item ?itemLabel ?ps ?propertyLabel ?objectLabel (DATATYPE(?object) AS ?datatype_obj) ?organizationLabel ?starttime ?endtime
    WHERE {
      VALUES (?item) {(...)}
  
      ?item ?predicate ?statement .  
      ?statement ?ps ?object. 
      OPTIONAL {?statement pq:P642 ?organization}.
      ?statement ( pq:P580 | pq:P2031 ) ?starttime.
      OPTIONAL {?statement ( pq:P582 | pq:P2032 ) ?endtime}. 
      
      BIND (STR(DATATYPE(?object)) AS ?datatype_obj) .

      FILTER(?ps NOT IN ( ps:P1448, ps:P395, ps:P190, 
                          ps:P155, ps:P26, ps:P102, ps:P551, 
                          ps:P1279, ps:P172, ps:P3761, 
                          ps:P1198, ps:P484, ps:P605, 
                          ps:P2397, ps:P2002, ps:P27,
                          ps:P1037, ps:P108, ps:P1038, 
                          ps:P451, ps:P5008, ps:P150,
                          ps:P2325, ps:P5573, ps:P2586,
                          ps:P195, ps:P305, ps:P156, ps:P836,
                          ps:P185, ps:P421, ps:P3361, ps:P184,
                          ps:P1705, ps:P901, ps:P1813, ps:P529, 
                          ps:P197, ps:P1429
                          ) )
      
      ?property wikibase:statementProperty ?ps .
  
      SERVICE wikibase:label { bd:serviceParam wikibase:language "ru, en" }
    }
    ORDER BY ?itemLabel ?propertyLabel
    """
    
    query = query.replace('(...)', q_numbers)
    r = requests.get(url, params = {'format': 'json', 'query': query})
    data = []
    try:
        data = r.json()
    except:
        pass
    
    dates = []
    
    if data != []:
        for item in data['results']['bindings']:
            dates.append(OrderedDict({
                'Unigram' : unigram,
                '#Q':  item['item']['value'].split("/")[-1],
                'Subject': item['itemLabel']['value'],
                '#P': item['ps']['value'].split("/")[-1],
                'Predicate': item['propertyLabel']['value'],
                'Object': item['objectLabel']['value'],
                'Organization': item['organizationLabel']['value'] if 'organizationLabel' in item else '',
                'Just Date': '',
                'Time Point' : '',
                'Start Time' : str(item['starttime']['value'])[:-10],
                'End Time' : str(item['endtime']['value'])[:-10] if 'endtime' in item else ''
            })) 
            
    if dates != []:
        for date in dates:
            if date["Object"].startswith("http"): # удаляем предикаты с ссылками
                dates.remove(date)
        df = pd.DataFrame(dates)
        return df


def getTimePoint(unigram, q_numbers):
    
    url = "https://query.wikidata.org/sparql"
    
    query = """SELECT ?item ?itemLabel ?property ?propertyLabel (DATATYPE(?object) AS ?datatype_obj) ?objectLabel ?organizationLabel ?point_in_time
    WHERE {
      VALUES (?item) {(...)}
  
      ?item ?predicate ?statement .  
      ?statement ?ps ?object . 
      OPTIONAL {?statement pq:P642 ?organization}.
      ?statement (pq:P585 | pq:P571 | pq:P2031 ) ?point_in_time .
      

      FILTER(DATATYPE(?point_in_time) = xsd:dateTime ) .
      BIND (STR(DATATYPE(?object)) AS ?datatype_obj) .


      FILTER(?ps NOT IN ( ps:P1448, ps:P395, ps:P190, 
                          ps:P155, ps:P26, ps:P102, ps:P551, 
                          ps:P1279, ps:P172, ps:P3761, 
                          ps:P1198, ps:P484, ps:P605, 
                          ps:P2397, ps:P2002, ps:P27,
                          ps:P1037, ps:P108, ps:P1038, 
                          ps:P451, ps:P5008, ps:P150,
                          ps:P2325, ps:P5573, ps:P2586,
                          ps:P195, ps:P305, ps:P156, ps:P836,
                          ps:P185, ps:P421, ps:P3361, ps:P184,
                          ps:P1705, ps:P901, ps:P1813, ps:P529, 
                          ps:P197, ps:P1429
                          ) )
  
      ?property wikibase:statementProperty ?ps .
  
      SERVICE wikibase:label { bd:serviceParam wikibase:language "ru,en" }
      
      }

    ORDER BY ?itemLabel ?propertyLabel ?point_in_time      

    """
    
    query = query.replace('(...)',q_numbers)
    r = requests.get(url, params = {'format': 'json', 'query': query})
    data = []
    try:
        data = r.json()
    except:
        pass
    
    dates = []
    
    if data != []:
        for item in data['results']['bindings']:
            dates.append(OrderedDict({
                'Unigram' : unigram,
                '#Q':  item['item']['value'].split("/")[-1],
                'Subject': item['itemLabel']['value'],
                '#P': item['property']['value'].split("/")[-1],
                'Predicate': item['propertyLabel']['value'],
                'Object': item['objectLabel']['value'],
                'Organization': item['organizationLabel']['value'] if 'organizationLabel' in item else '',
                'Just Date': '',
                'Time Point' : str(item['point_in_time']['value'])[:-10],
                'Start Time' : '',
                'End Time' : ''
            })) 
            
    if dates != []:
        for date in dates:
            if date["Object"].startswith("http"): # удаляем предикаты с ссылками
                dates.remove(date)
        df = pd.DataFrame(dates)
        return df




def getDates(path, unigram_dict):

    df = pd.read_pickle(path)
    df.reset_index(inplace=True)
    unique = df["unigram"].unique()
    unique = unique.tolist()
    # найдем соответствия между униграмами и сущностями в Викиданных
    unigrams_with_Q = {}
    for word in unique:
        if word in unigram_dict:
            unigrams_with_Q[word] = unigram_dict[word]
    print("Expected number of queries: " + str(len(unigrams_with_Q)))

    # преобразуем значения словаря в формат для SPARQL
    for k, v in unigrams_with_Q.items():
        v = ["(wd:{})".format(Q) for Q in list(v)]
        if len(v) <= 10:
            unigrams_with_Q[k] = [' '.join(v)]
        else:
            parts = int(str(len(v))[0]) + 1
            unigrams_with_Q[k] = [' '.join(i) for i in parting(v, parts)]

    results = pd.DataFrame(columns = ["Unigram", "#Q", "Subject", "#P", "Predicate", "Object", "Organization", 
                                  "Just Date","Time Point", "Start Time", "End Time"])
    
    for k, v in unigrams_with_Q.items():
        for qs in v:
            results = pd.concat([results, getSimpleTriplets(k, qs)],sort=False)
            results = pd.concat([results, getStartEnd(k, qs)],sort=False)
            results = pd.concat([results, getTimePoint(k, qs)],sort=False)
        

    new_path = "./dates-unigrams_" + path.split('.')[0][-1] + ".tsv"  
    results.to_csv(new_path, sep = '\t', index=False)

    print("got dates for " + path)
    return 0


def main():
    unigram_dict = createUnigramDict()
    for path in getPaths():
        getDates(path, unigram_dict)
    return 0


if __name__ == '__main__':
    main()
