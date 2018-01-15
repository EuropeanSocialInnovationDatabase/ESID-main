# -*- coding: utf-8 -*-

from nltk.tag import StanfordNERTagger
from nltk.tokenize import word_tokenize
class StanfordTagger:
	def __init__(self):
		self.st = StanfordNERTagger('../Resources/stanford-ner-2017-06-09/classifiers/english.all.3class.distsim.crf.ser.gz',
							   '../Resources/stanford-ner-2017-06-09/stanford-ner.jar',
							   encoding='utf-8')

	def tag_text(self,text):
		tokenized_text = word_tokenize(text)
		classified_text = self.st.tag(tokenized_text)
		return classified_text

