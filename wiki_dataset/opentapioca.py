# CODE TO PROCESS OPENTAPIOCA EXTRACTED HTML's

import json
import os


def process(file):
    """
    Code to process OpenTapioca HTML files
    :param file: path of a HTML file
    :return: detected entities from text in JSON format (like in wiki_dataset)
    """
    with open(f"./opentapioca/{file}", "r") as f:
        contents = f.read().replace('<div id="demo_output"><div>', '').replace("&nbsp;", " ")

        spans = contents.split('<span class="bo" data-annotation-id=')[1:]

        mentions_pairs = []
        for s in spans:
            mention_start = s.find('class="bw">') + len('class="bw">')
            mention_end = s.find('</span>')
            mention_text = s[mention_start:mention_end]
            if '<div class="annotation-tag predicted_valid">' in s:
                ind = s.find('<div class="annotation-tag predicted_valid">') + len('<div class="annotation-tag predicted_valid">')
                id_ = s[ind:].split('<a href="')[1].replace("https://www.wikidata.org/wiki/", "")
                end = id_.find('"')
                id_ = id_[:end]
                mentions_pairs.append((mention_text, id_))
            else:
                candidates_raw = s.split('<div class="annotation-tag">')[1:]
                potentials = []
                for k in candidates_raw:
                    id_ = k.replace('<a href="https://www.wikidata.org/wiki/', "")
                    end = id_.find('"')
                    id_ = id_[:end]
                    score = k.split('<span class="scores">')[-1]
                    score_start = score.find('Score: ') + len('Score: ')
                    score_end = score.find('</span>')
                    score = float(score[score_start:score_end])
                    potentials.append((id_, score))
                potentials = sorted(potentials, key=lambda x: x[1], reverse=True)
                potentials = [x[0] for x in potentials]
                candidate = (mention_text, potentials[:3])
                mentions_pairs.append(candidate)


    with open(f"./separate_jsons_processed/{file.replace('html', 'json')}", "r") as f:
        a = json.load(f)
        init_text = a['text']

        start_pointer = 0

        updated_mention_pairs = []

        for mention in mentions_pairs:
            if mention[0]:
                start = init_text.find(mention[0])
                end = start + len(mention[0])
                # print(init_text[start:end])
                # print(mention[0])
                init_text = init_text[end:]
                updated_mention_pairs.append((mention[0], mention[1], start + start_pointer, end + start_pointer))
                start_pointer += end

        text = a['text']
        for pair in updated_mention_pairs:
            if pair[0] != text[pair[2]:pair[3]]:
                # print(pair[0])
                # print(text[pair[2]:pair[3]])
                pass

        entities = []

        for pair in updated_mention_pairs:
            dictionary = {"currentText": "", "startPosition": -1, "endPosition": -1, "id": -1}
            dictionary["currentText"] = pair[0]
            if not isinstance(pair[1], list):
                dictionary["id"] = [pair[1]]
            else:
                dictionary["id"] = pair[1]
            dictionary["startPosition"] = pair[2]
            dictionary["endPosition"] = pair[3]
            entities.append(dictionary)

        a["listWikiEntity"] = entities

        return a

files = os.listdir("./opentapioca")

for fff in files:
    print(fff)
    print(process(fff))
    with open(f'./opentapioca_jsons/{fff.replace("html", "json")}', 'w') as out:
        json.dump(process(fff), out, ensure_ascii=False)
