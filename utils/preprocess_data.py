# !pip install pymorphy2==0.8
# !pip install git+https://github.com/aatimofeev/spacy_russian_tokenizer.git
import pickle
import os
from razdel import tokenize, sentenize
import numpy
import csv
from natasha import (
    Segmenter,
    MorphVocab,
    NewsEmbedding,
    NewsMorphTagger,
    NewsSyntaxParser,
    NewsNERTagger,
    PER,
    NamesExtractor,
    DatesExtractor,
    MoneyExtractor,
    AddrExtractor,
    Doc
)

segmenter = Segmenter()
morph_vocab = MorphVocab()

emb = NewsEmbedding()
morph_tagger = NewsMorphTagger(emb)
syntax_parser = NewsSyntaxParser(emb)
ner_tagger = NewsNERTagger(emb)

names_extractor = NamesExtractor(morph_vocab)
dates_extractor = DatesExtractor(morph_vocab)
money_extractor = MoneyExtractor(morph_vocab)
addr_extractor = AddrExtractor(morph_vocab)

data_path = '../data/'
# train_file='paraphrases.tsv', test_file='paraphrases_gold.tsv'
# train_file='paraphrase_framebank.tsv'
def read_all_data(train_file=data_path + 'paraphrases.tsv', test_file= data_path + 'paraphrases_gold.tsv'):
    with open(train_file, encoding='utf-8') as f:
        reader = csv.DictReader(f, delimiter='\t')
        data = list(reader)
        data = numpy.asarray(data)

        # numpy.random.seed(123)
        # numpy.random.shuffle(data)
        length = data.shape[0]

        train = data[:int(0.9 * length)]
        valid = data[int(0.9 * length):]

        with open(test_file, encoding='utf-8') as f:
           reader = csv.DictReader(f, delimiter='\t')
           data = list(reader)
           data = numpy.asarray(data)

        #    numpy.random.seed(123)
        #    numpy.random.shuffle(data)

           test = data

        return train, valid, test

def read_role_data(train_file=data_path + 'framebank_roles.tsv'):
    with open(train_file, encoding='utf-8') as f:
        reader = csv.DictReader(f, delimiter='\t')
        data = list(reader)
        data = numpy.asarray(data)

        # numpy.random.seed(123)
        # numpy.random.shuffle(data)
        length = data.shape[0]

        train = data[:int(0.8 * length)]
        valid = data[int(0.8 * length):int(0.9 * length)]
        test = data[int(0.9 * length):]
        return train ,valid, test

def tokenize_data(all_data):
    tokenized = []
    
    for set_ in all_data:
        data = {'q1': [], 'q2': [], 'y': []}
        for datum in set_:
            # label = int(datum['is_duplicate']) if int(datum['is_duplicate']) != -1 else 2
            data['q1'].append(_text_preprocess(datum['question1']))
            data['q2'].append(_text_preprocess(datum['question2']))
            # -1 -> 0  0 -> 1  1 -> 2
            data['y'].append(int(datum['is_duplicate']) + 1)
        tokenized.append(data)
    return tokenized

def tokenize_roles(role_data):
    tokenized = []
    
    for set_ in role_data:
        data = {'roles1': [], 'roles2': [], 'y': []}
        for datum in set_:
            # label = int(datum['is_duplicate']) if int(datum['is_duplicate']) != -1 else 2
            data['roles1'].append([token.text for token in list(tokenize(datum['roles1']))])
            data['roles2'].append([token.text for token in list(tokenize(datum['roles2']))])
            # -1 -> 0  0 -> 1  1 -> 2
            data['y'].append(int(datum['is_duplicate']) + 1)
        tokenized.append(data)
    return tokenized


def _text_preprocess(text):
    if text is None:
        return []

    text = text.strip().replace('`', "'")

    doc = Doc(text)
    doc.segment(segmenter)
    doc.tag_morph(morph_tagger)
    doc.parse_syntax(syntax_parser)
   
    for token in doc.tokens:
        token.lemmatize(morph_vocab)
   
    tokens = [t.lemma for t in doc.tokens]
    return tokens

def _read_emb(file, dim):
    emb = {}
    dim += 1
    with open(file, encoding='utf-8') as f:
        for line in f:
            tokens = line.strip().split(' ')
            if len(tokens) == dim:
                emb[tokens[0]] = list(map(lambda x: float(x), tokens[1:]))
    return emb

def _token2idx(tokens, token_map, embs, filtered_emb):
    for i in range(len(tokens)):
        if tokens[i] not in token_map:
            if tokens[i] in embs:
                token_map[tokens[i]] = len(token_map)
                # also random vector for new token
                filtered_emb.append(embs[tokens[i]])
            else:
                tokens[i] = '<unk>'
        tokens[i] = token_map[tokens[i]]

def idx_and_emb(all_data, emb_file, dim):
    embs = _read_emb(emb_file, dim)
    word2idx = {'<pad>': 0, '<unk>': 1}
    filtered_emb = [numpy.random.uniform(-0.1, 0.1, dim) for _ in range(2)]
    for set_ in all_data:
        for datum in set_['q1']:
            _token2idx(datum, word2idx, embs, filtered_emb)
        for datum in set_['q2']:
            _token2idx(datum, word2idx, embs, filtered_emb)
    print('{} word types'.format(len(word2idx)))
    filtered_emb = numpy.asarray(filtered_emb, dtype='float32')
    return filtered_emb, word2idx

# def _role_token2idx(tokens,token_map,emb,filtered_emb):
#     for i in range(len(tokens)):
#         if tokens[i] not in token_map:
#             if tokens[i] in embs:
#                 token_map[tokens[i]] = len(token_map)
#                 filtered_emb.append(embs[tokens[i]])
#             else:
#                 tokens[i] = '<unk>'
#         tokens[i] = token_map[tokens[i]]


def idx_and_emb_with_role(all_data, emb_file, dim):
    role_word2idx = {'<pad>': 0, '<unk>': 1, 'pred': 2}
    role_filtered_emb = [numpy.random.uniform(-0.1, 0.1, dim) for _ in range(3)]    

    for set_ in all_data:
        for datum in set_['roles1']:
            _token2idx(datum, role_word2idx, role_filtered_emb)
        for datum in set_['roles2']:
            _token2idx(datum, role_word2idx, role_filtered_emb)

    print('{} word types'.format(len(role_word2idx)))
    print(role_filtered_emb)
    role_filtered_emb = numpy.asarray(role_filtered_emb, dtype='float32')

    return role_filtered_emb, role_word2idx

def main():
    all_data = read_all_data()
    print('Reading data done.')
    # role_data = read_role_data()
    # print('Reading roles data done.')
    tokenized = tokenize_data(all_data)
    # tokenized_roles = tokenize_roles(role_data)
    print('Tokenization done.')

    emb_file = data_path + 'glove.840B.300d.sst.txt'
    filtered_emb, word2idx = idx_and_emb(tokenized, emb_file, 300)
    print('Embedding done.')

    # role_filtered_emb, role_word2idx = idx_and_emb_with_role(tokenized_roles, emb_file, 300)
    # print('Role embedding done.')    

    with open(data_path + 'paraphrases_emb', 'wb') as f:
        pickle.dump((tokenized, filtered_emb, word2idx), f)
        # pickle.dump((tokenized, filtered_emb, word2idx, role_data, role_filtered_emb, role_word2idx), f)
    print('Saved.')

main()