import re
from nltk.tokenize import sent_tokenize, word_tokenize
import spacy
nlp = spacy.load('en_core_web_sm')

def remove_string_special_characters(s):
    # Replace special character with ' '
    stripped = re.sub('[^\w.!?%\s]', '', s)
    stripped = re.sub('_', '', stripped)

    # Change any whitespace to one space
    stripped = re.sub('\s+', ' ', stripped)

    # Remove start and end white spaces
    stripped = stripped.strip()

    return stripped


def remove_html_tags(text):
    return re.sub('<[^<]+?>', '', text).replace('\n', ' ')


def check_sentence_has_verb(tokens):
    for token in tokens:
        if token.pos_ == 'VERB':
            return True
    return False


MAX_CONSECUTIVE_NOUNS = 5


def check_sentence_for_consecutive_nouns(tokens):
    nouns_counter = 0
    for token in tokens:
        if token.pos_ == 'NOUN':
            nouns_counter += 1
            if nouns_counter >= MAX_CONSECUTIVE_NOUNS:
                return True
        else:
            nouns_counter = 0
    return False


def check_sentence_is_valid(sentence):
    tokens = nlp(sentence)
    return check_sentence_has_verb(tokens) and not check_sentence_for_consecutive_nouns(tokens)


MIN_SENT_WORDS_LEN = 3
MAX_SENT_WORDS_LEN = 55


def preprocess_text(text):
    text = remove_string_special_characters(text)
    text = remove_html_tags(text)
    sentences = sent_tokenize(text)
    sentences = [sent for sent in sentences if len(word_tokenize(sent)) > MIN_SENT_WORDS_LEN and len(word_tokenize(sent)) < MAX_SENT_WORDS_LEN and check_sentence_is_valid(sent)]
    return '\n'.join(sentences)