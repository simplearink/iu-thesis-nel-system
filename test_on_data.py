import spacy
import numpy as np

from utils import *
from tqdm import tqdm

# Code for processing raw text to csv;
# To add aliases, set add_aliases=True in method generate_candidates, to use only descriptions, set add_aliases=False
# For different context, you can change row['sent_context'] to row['full_context']

model, tokenizer = load_model_and_tokenizer()
nlp = spacy.load("ru_core_news_lg")

docs = [f"dataset/new_news/{i}.txt" for i in range(11, 31) if i != 26]

for d in docs:
    df = process(d)
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

    pred_df.to_csv(f"./dataset/new_news_test/sent_context/{d.split('/')[-1].replace('txt', 'csv')}")
