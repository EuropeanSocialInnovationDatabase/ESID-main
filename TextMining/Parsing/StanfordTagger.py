import nltk
import json
from json import JSONEncoder
from nltk.stem import WordNetLemmatizer
class tagged_word(JSONEncoder):
    def __init__(self,word,tag,lemma):
        self.word = word
        self.tag = tag
        self.lemma = lemma
        self.pos = self.get_full_pos(tag)

    def get_full_pos(self,x):
        return {
            'CC': 'Coordinating conjunction',
            'CD': 'Cardinal number',
            'DT': 'Determiner',
            'EX': 'Existential there',
            'FW': 'Foreign word',
            'IN': 'Preposition or subordinating conjunction',
            'JJ': 'Adjective',
            'JJR': 'Adjective, comparative',
            'JJS': 'Adjective, superlative',
            'LS': 'List item marker',
            'MD': 'Modal',
            'NN': 'Noun, singular or mass',
            'NNS': 'Noun, plural',
            'NNP': 'Proper noun, singular',
            'NNPS': 'Proper noun, plural',
            'PDT': 'Predeterminer',
            'POS': 'Possessive ending',
            'PRP': 'Personal pronoun',
            'PRP$': 'Possessive pronoun',
            'RB': 'Adverb',
            'RBR': 'Adverb, comparative',
            'RBS': 'Adverb, superlative',
            'RP': 'Particle',
            'SYM': 'Symbol',
            'TO': 'To',
            'UH': 'Interjection',
            'VB': 'Verb, base form',
            'VBD': 'Verb, past tense',
            'VBG': 'Verb, gerund or present participle',
            'VBN': 'Verb, past participle',
            'VBP': 'Verb, non-3rd person singular present',
            'VBZ': 'Verb, 3rd person singular present',
            'WDT': 'Wh-determiner',
            'WP': 'Wh-pronoun',
            'WP$': 'Possessive wh-pronoun',
            'WRB': 'Wh-adverb',
            '.':'Punctuation'}[x]

    def default(self,o):
        return o.__dict__

wordnet_lemmatizer = WordNetLemmatizer()

def perform_tagging(text):
    global wordnet_lemmatizer
    tokens=nltk.word_tokenize(text)
    tags = nltk.pos_tag(tokens)
    pos_tags = []
    for tagged_w in tags:
        word = tagged_w[0]
        lemma = wordnet_lemmatizer.lemmatize(word,pos=tag)
        tag = tagged_w[1]
        t = tagged_word(word,tag,lemma)
        pos_tags.append(t)
    return pos_tags

def perform_tagging_json(text):
    global wordnet_lemmatizer
    tokens=nltk.word_tokenize(text)
    tags = nltk.pos_tag(tokens)
    pos_tags = []
    for tagged_w in tags:
        word = tagged_w[0]
        tag = tagged_w[1]
        if "VB" in tag:
            lemma = wordnet_lemmatizer.lemmatize(word,pos='v')
        else:
            lemma = wordnet_lemmatizer.lemmatize(word)

        t = tagged_word(word,tag,lemma)
        pos_tags.append(t)
    return json.dumps([ob.__dict__ for ob in pos_tags])



print perform_tagging_json("We are going out. Just you and me. What is your name?")