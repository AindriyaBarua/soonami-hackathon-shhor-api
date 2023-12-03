"""
Developed by Aindriya Barua in December, 2023
"""

import re
import emoji

import constants

stopwords = list(set(constants.HINGLISH_STOPWORDS + constants.ENGLISH_STOPWORDS))


def preprocess_text(sent):
    sent = sent.strip()
    sent = sent.lower()
    sent = re.sub(r'^@[0-9a-z_\.]+', '', sent)  # username
    sent = re.sub(r' @[0-9a-z_\.]+', '', sent)
    sent = re.sub(r'\\x[0-9a-z]+', ' ', sent)  # remove \x09
    sent = re.sub(r"http\S+", "", sent)
    # not removing hash, star, exclamation from mid of word
    sent = re.sub(r"[,;\(\)\\.:\-_/|](!$)*", " ", sent)
    sent = sent.replace('"', ' ')
    sent = sent.replace("'", ' ')

    emojis = emoji.emoji_list(sent)

    if len(emojis) > 0:
        for item in emojis:
            for emo in item['emoji']:
                sent = re.sub(emo, " " + emo + " ", sent)

    sent = re.sub('\n', ' ', sent)
    sent = re.sub(' +', ' ', sent)
    sent = sent.strip()
    return sent


def custom_lemmatize(tokens):
    lemmatized_tokens = []
    for token in tokens:

        new = token[0]
        count = 1
        for ch in token[1:]:

            if ch == new[len(new) - 1]:
                count = count + 1
                if count <= 2:
                    new = new + ch
            else:
                count = 1
                new = new + ch
        lemmatized_tokens.append(new)
    return lemmatized_tokens


def tokenize(sentence):
    tokens = sentence.split()
    return tokens


def remove_stopwords(word_tokens):
    filtered_tokens = [word for word in word_tokens if word not in stopwords]
    return filtered_tokens


def preprocess_main(sent):
    sent = preprocess_text(str(sent))
    tokens = tokenize(sent)
    lemmatized_tokens = custom_lemmatize(tokens)

    filtered_tokens = remove_stopwords(lemmatized_tokens)

    normalized_sent = " ".join(filtered_tokens)
    return normalized_sent
