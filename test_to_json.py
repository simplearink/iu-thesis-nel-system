import spacy

from utils import *
from tqdm import tqdm

import os
import json

import numpy as np

# Code for processing json files to csv;
# To add aliases, set add_aliases=True in method generate_candidates, to use only descriptions, set add_aliases=False
# The code for 2 context types is provided below

model, tokenizer = load_model_and_tokenizer()
nlp = spacy.load("ru_core_news_lg")

docs = os.listdir("wiki_dataset/separate_jsons_processed")
docs = ['./wiki_dataset/separate_jsons_processed/' + i for i in docs]


# full context
for d in docs:
    with open(d) as f:
        json_d = json.load(f)['text']
    df = process_text(json_d)
    pred_df = pd.DataFrame(columns=["entity", "id", "start", "end", "sent_context", "full_context"])

    for i, row in tqdm(df.iterrows(), total=len(df)):
        mention = row['entity']
        lemmatized = []
        doc = nlp(mention)

        for token in doc:
            lemmatized.append(token.lemma_.capitalize())

        lemmatized = " ".join(lemmatized)

        try:
            candidates_idx, candidates_desc = generate_candidates(lemmatized, add_aliases=False)
        except:
            candidates_idx = -1


        if candidates_idx == -1 or len(candidates_idx) == 0:
            id_ = -1
        else:
            similars = calculate_similarity(model, tokenizer, json_d, candidates_desc)
            similars_sorted = np.argsort(-similars)

            id_ = []

            for sim in range(3):
                if len(candidates_idx) > sim:
                    id_.append(candidates_idx[sim])

        row['id'] = id_

        pred_df = pred_df.append(row, ignore_index=True)

    pred_df.to_csv(f"./res/full_context/{d.split('/')[-1].replace('json', 'csv')}")

# sentence context
for d in docs:
    with open(d) as f:
        json_d = json.load(f)['text']
    df = process_text(json_d)
    pred_df = pd.DataFrame(columns=["entity", "id", "start", "end", "sent_context", "full_context"])

    for i, row in tqdm(df.iterrows(), total=len(df)):
        mention = row['entity']
        lemmatized = []
        doc = nlp(mention)

        for token in doc:
            lemmatized.append(token.lemma_.capitalize())

        lemmatized = " ".join(lemmatized)

        try:
            candidates_idx, candidates_desc = generate_candidates(lemmatized, add_aliases=False)
        except:
            candidates_idx = -1


        if candidates_idx == -1 or len(candidates_idx) == 0:
            id_ = -1
        else:
            similars = calculate_similarity(model, tokenizer, row['sent_context'], candidates_desc)
            similars_sorted = np.argsort(-similars)

            id_ = []

            for sim in range(3):
                if len(candidates_idx) > sim:
                    id_.append(candidates_idx[sim])

        row['id'] = id_

        pred_df = pred_df.append(row, ignore_index=True)

    pred_df.to_csv(f"./res/sent_context/{d.split('/')[-1].replace('json', 'csv')}")