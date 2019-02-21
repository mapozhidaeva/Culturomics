import ijson
LINES = 5000


def write_tsv(items): 
    with open("entities-5000.tsv", "w", encoding = "UTF-8") as wf:
        n_lines = 0
        for item in items:
            if item["type"] == "item" and n_lines < LINES:    
                label = ''
                try:
                    label = item["labels"]["ru"]["value"]
                except KeyError:
                    pass
                   
                aliases = ''
                try:
                    if len(item["aliases"]["ru"]) == 1:
                        aliases = item["aliases"]["ru"][0]['value']
                    if len(item["aliases"]["ru"]) > 1:
                        aliases = "|".join([i["value"] for i in item["aliases"]["ru"]])
                except KeyError:
                    pass 
                
                if label != '':
                    n_lines += 1
                    id_ = item["id"]
                    wf.write('{}\t{}\t{}\n'.format(id_, label, aliases))
                                       
            elif item["type"] == "item" and n_lines == LINES:
                break
                
    return 0


def main():
    with open("20150420.json", "r", encoding="UTF-8") as f:
        items = ijson.items(f, "item")            
        write_tsv(items)
    return 0
  
                             
if __name__ == '__main__':
    main()         
