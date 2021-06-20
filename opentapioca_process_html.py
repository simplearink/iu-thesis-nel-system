import json
import os
import pandas as pd

def process(file):
    """
    Code to process HTML OpenTapioca files to CSV of news_dataset format
    :param file: path of HTML file
    :return: dataframe of news_dataset format
    """
    with open(f"./news_dataset/opentapioca/{file}", "r") as f:
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

    # print(mentions_pairs)

    with open(f"./news_dataset/raw/{file.replace('html', 'txt')}", "r") as f:
        a = pd.DataFrame()
        init_text = f.read()

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
        with open(f"./news_dataset/raw/{file.replace('html', 'txt')}", "r") as f:
            text = f.read()
        for pair in updated_mention_pairs:
            if pair[0] != text[pair[2]:pair[3]]:
                # print(pair[0])
                # print(text[pair[2]:pair[3]])
                pass

        entities = []

        for pair in updated_mention_pairs:
            dictionary = {"entity": "", "id": "", "start": -1, "end": -1, "id": -1, "full_context": text}
            dictionary["entity"] = pair[0]
            if not isinstance(pair[1], list):
                dictionary["id"] = [pair[1]]
            else:
                dictionary["id"] = pair[1]
            dictionary["start"] = int(pair[2])
            dictionary["end"] = int(pair[3])
            a = a.append(dictionary, ignore_index=True)

        return a

files = os.listdir("./news_dataset/opentapioca")

for fff in files:
    print(fff)
    print(process(fff))
    k = process(fff)
    k.to_csv(f'./news_dataset/opentapioca_jsons/{fff.replace("html", "csv")}')