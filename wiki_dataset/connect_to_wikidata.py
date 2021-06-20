# -*- coding: utf-8 -*-

# USE THIS CODE IF IDs IN "./separate_jsons_processed" DO NOT CONTAIN "Q"

import os
import json
import requests

files = os.listdir("./separate_jsons_processed")
files = ['./separate_jsons_processed/' + i for i in files]

def process_dict(dictionary):
    entities = dictionary['listWikiEntity']
    for i, ent in enumerate(entities):
        if "En:" not in ent['title']:
            query = requests.get(
                f"https://ru.wikipedia.org/w/api.php?action=query&prop=pageprops&titles={ent['title']}&format=json")
        else:
            query = requests.get(
                f"https://en.wikipedia.org/w/api.php?action=query&prop=pageprops&titles={ent['title']}&format=json")
        query_text = query.text
        wiki_map_json = json.loads(query_text)
        try:
            add_key = list(wiki_map_json['query']['pages'].keys())[0]
            entities[i]['id'] = wiki_map_json['query']['pages'][add_key]['pageprops']['wikibase_item']
        except:
                entities[i]['id'] = -1

    dictionary['listWikiEntity'] = entities
    return dictionary

counter = 0

for f in files:

    print(f)
    with open(f) as inp:
        new_file = json.load(inp)
        print(new_file['text'])
        new_file = process_dict(new_file)
        # new_file = str(new_file).replace("'", '"')
            # new_file = json.loads(new_file)
        with open(f, 'w') as out:
            json.dump(new_file, out, ensure_ascii=False)
        counter += 1

print(counter)