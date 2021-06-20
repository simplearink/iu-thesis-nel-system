import requests
from transformers import AutoTokenizer, AutoModel
import torch
from qwikidata.entity import WikidataItem
from qwikidata.linked_data_interface import get_entity_dict_from_api
from sklearn.metrics.pairwise import cosine_similarity
import pandas as pd
from natasha import (
    Segmenter,
    NewsEmbedding,
    NewsNERTagger,
    Doc
)
import spacy

#Mean Pooling - Take attention mask into account for correct averaging
def mean_pooling(model_output, attention_mask):
    token_embeddings = model_output[0] #First element of model_output contains all token embeddings
    input_mask_expanded = attention_mask.unsqueeze(-1).expand(token_embeddings.size()).float()
    sum_embeddings = torch.sum(token_embeddings * input_mask_expanded, 1)
    sum_mask = torch.clamp(input_mask_expanded.sum(1), min=1e-9)
    return sum_embeddings / sum_mask

# Vectorization of data
def vectorize(tokenizer_model, vectorizer_model, data):
    encoded_input = tokenizer_model(data, padding=True, truncation=True, max_length=128, return_tensors='pt')
    # Compute token embeddings
    with torch.no_grad():
        model_output = vectorizer_model(**encoded_input)
    # Perform pooling. In this case, mean pooling
    sentence_embeddings = mean_pooling(model_output, encoded_input['attention_mask'])
    return sentence_embeddings

# Models loading
def load_model_and_tokenizer():
    tokenizer = AutoTokenizer.from_pretrained("DeepPavlov/rubert-base-cased-sentence")
    model = AutoModel.from_pretrained("DeepPavlov/rubert-base-cased-sentence")
    return model, tokenizer

# cosine similarity calculation between found entity text and variants text (e.g. descriptions)
def calculate_similarity(model, tokenizer, init_text, variants_texts):
    variants_vectors = vectorize(tokenizer, model, variants_texts)
    init_vec = vectorize(tokenizer, model, init_text)
    return cosine_similarity(init_vec, variants_vectors)[0]

# candidates generation
def generate_candidates(query, add_aliases=False):
    text = requests.get(f"https://www.wikidata.org/w/index.php?search={query}").text
    s = text.find('<div class="searchresults">')
    if "There were no results matching the query." in text:
        return -1, -1
    text = text[s:]
    s2 = text.find("<ul class")
    f = text.find("</ul>")
    search_results = text[s2:f + 5].split("</a>")

    variants_ids = []
    variants = []

    for i in search_results[:-1]:
        s = i.find("<a href")
        f = i[s:] + "</a>"
        id_ = f[f.find("/wiki/") + 6:f.find('" title')]
        q_dict = get_entity_dict_from_api(id_)
        q = WikidataItem(q_dict)

        desc = q.get_description("ru")
        if desc:
            # print(desc)
            variants_ids.append(id_)
            variants.append(desc)
        if add_aliases:
            if len(q.get_label('ru')) > 0:
                variants_ids.append(id_)
                variants.append(q.get_label('ru'))
            else:
                variants_ids.append(id_)
                variants.append(q.get_enwiki_title())
            alias_variants = q.get_aliases("ru")
            for a in alias_variants:
                variants_ids.append(id_)
                variants.append(a)

    return variants_ids, variants

# process initial document with a raw text, generate dataframe with entities of required types and all requires info
def process(doc_path):
    segmenter = Segmenter()
    emb = NewsEmbedding()
    ner_tagger = NewsNERTagger(emb)

    text = " ".join([line.strip() for line in open(doc_path).readlines() if line.strip()])

    sentences = [s.strip() for s in text.split(". ") if s.strip()]

    df = pd.DataFrame(columns=["entity", "id", "start", "end", "sent_context", "full_context"])

    for s in sentences:
        doc = Doc(s)

        doc.segment(segmenter)
        doc.tag_ner(ner_tagger)

        common = []

        for span in doc.spans:
            if span.type in ["PER", "LOC", "ORG"]:
                common.append(span)
                stext = span.text if span.text[-1] != "." else span.text[:-1]
                ent = {"entity": stext, "start": span.start, "end": span.stop, "sent_context": s, "full_context": text}
                df = df.append(ent, ignore_index=True)
    return df

# process a raw text, generate dataframe with entities of required types and all requires info
def process_text(text):
    segmenter = Segmenter()
    emb = NewsEmbedding()
    ner_tagger = NewsNERTagger(emb)

    nlp = spacy.load("ru_core_news_lg")
    tokens = nlp(text)

    sentences = []

    for sent in tokens.sents:
        if str(sent) != "\n":
            sentences.append(str(sent))

    # print(sentences)

    df = pd.DataFrame(columns=["entity", "id", "start", "end", "sent_context", "full_context"])

    for s in sentences:
        doc = Doc(s)

        doc.segment(segmenter)
        doc.tag_ner(ner_tagger)

        common = []

        for span in doc.spans:
            if span.type in ["PER", "LOC", "ORG"]:
                common.append(span)
                stext = span.text if span.text[-1] != "." else span.text[:-1]
                ent = {"entity": stext, "start": span.start, "end": span.stop, "sent_context": s, "full_context": text}
                df = df.append(ent, ignore_index=True)
    return df