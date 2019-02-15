import ijson


f = open("20150420.json", "r", encoding="UTF-8")
items = ijson.items(f, "item")


def write_tsv(items, lines = 500): #пока возьмем только 500 сущностей из Викиданных
    n_lines = 0

    for item in items:
        if item["type"] == "item" and n_lines < lines:
            n_lines += 1

            id_ = item["id"]

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
            
            with open("entities.tsv", "a", encoding = "UTF-8") as wf:
                wf.write('%s\t%s\t%s\n' % (id_, label, aliases))
        if item["type"] == "item" and n_lines == lines:
            break
           

write_tsv(items)
f = f.close()

#этот код выполняется примерно 27 секунд
