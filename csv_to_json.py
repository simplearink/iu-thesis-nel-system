import pandas as pd
import json
import os

# turn CSV prediction files to JSON prediction files (for easier comparison)

files = os.listdir("wiki_dataset/res/sent_context")
files = ["./res/sent_context/" + i for i in files]

print(files[3])

for filename in files:

    a = pd.read_csv(filename)
    try:
        a['id'] = a['id'].apply(eval)
    except:
        pass

    # print(a)

    with open(f"./new_dataset/separate_jsons_processed/{filename.split('/')[-1].replace('csv', 'json')}") as inner:
        dictionary = json.load(inner)

    dictionary['listWikiEntity'] = []

    for i, row in a.iterrows():
        inner_dict = {'currentText': "", 'startPosition': -1, 'endPosition': -1, 'id': -1}
        inner_dict['currentText'] = row['entity']
        inner_dict['id'] = row['id']
        sent_start = dictionary['text'].find(row['sent_context'])
        st = row['start'] + sent_start
        fin = row['end'] + sent_start
        inner_dict['startPosition'] = st
        inner_dict['endPosition'] = fin
        dictionary['listWikiEntity'].append(inner_dict)

    print(dictionary['listWikiEntity'])

    new_filename = "./res/jsons/" + "/".join(filename.split("/")[-2:]).replace("csv", "json")

    with open(new_filename, 'w') as out:
        json.dump(dictionary, out, ensure_ascii=False)
