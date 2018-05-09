#!/usr/bin/env python
# -*- coding: utf-8 -*-
from sklearn.feature_extraction.text import TfidfVectorizer
import nltk
from sklearn.metrics.pairwise import linear_kernel
from nltk.stem.porter import *

description = """vision values our objective goal aim purpose about project involving community how. 
     Skip to primary navigation  Skip to content  Skip to primary sidebar  Skip to footer L4A We work with older people receiving care across Leicester and Leicestershire Home  About  Our values &#038; mission  Our work  Our team  Support L4A  Donate  Volunteer  News  Contact us  About  Research shows that learning in the later stages of life can boost confidence, give a more positive outlook on life and delay on the onset of dementia. L4A believes that there is a gap in provision of educational and learning services to people who live in care settings and seeks to address this gap.  We define learning as &#8216;a tool for creating wellbeing, a good later life and can be a catalyst for change.&#8217;  We define our fourth age as &#8216;not a numerical age but a time in later life when older people need care and support to go about daily living.&#8217;  Our Vision  Older age is a time of development enhanced by learning.  Our Mission  To offer learning opportunities to older people in need of care or support, primarily in Leicester and Leicestershire.  Our Values  At Learning for the Fourth Age (L4A), our values are central. They inform our governance, our work with older people and the impact that we create with them. Our values are:  We see learning as a tool for creating wellbeing and a good later life that can also be a catalyst for change.  We value learning for ourselves as an organisation, as well as learning being our specialism for older people and our volunteers  We empower our older people by offering them real choices in what and how they learn  We are determined to deliver quality, as well as to innovate and find creative solutions to problems  We constructively challenge stereotypes about care settings, older people and what constitutes learning. Older people are never too old to learn.  We share our ideas, our experiences and work with others, as L4A is a demonstration organisation and a thought and practice leader for learning in the fourth age.  L4A believes that there is a gap in provision of educational and learning services to people who live in care homes and seeks to address this gap by:  Encouraging older people to follow up existing interests or develop new ones using a multimedia range of resources.  Supporting learners with their individual needs by a trained learning mentor working with them on a one-to-one basis, using appropriate resources for each learner and taking into account their physical needs.  Promoting the value of education as a tool for increasing wellbeing., giving a more positive outlook on life, increasing confidence and delaying the onset of dementia.  Working towards raising the expectations that residents, relatives and society have for the quality of life and mental stimulus for the elderly, especially for those in care.  Encouraging the Care Quality Commission to strengthen the standards for social care inspection to include mental stimulation as a threshold requirement and one-to-one learning, complemented by group learning as the norm.  Annual reports  Please click the links below to read our most recent annual report or those from previous years.  L4A-Annual-Report-2017  L4A-Annual-Report-2016  L4A-Annual-Report-2015  L4A-Annual-Report-2013-14  Annual-report-2012-13  directors-report-2011-12  L4A-Directors-Report-2010-2011  L4A-Directors-Report-2009-10  L4A-Directors-Report-2008-09     Primary Sidebar     Latest news  VOTE FOR US TO WIN £50,000  Help us win £50,000  &#8216;Painting by Numbers&#8217; Workshop proves great success for L4A volunteer  Special Movie Matinee spreads that glorious feeling!  Continuing Impact of &#8216;The Power of Stories&#8217;  Categories  event  (6)  Fundraisers  (4)  In the press  (2)  Job opportunities  (1)  Projects  (12)  Uncategorized  (3)  Volunteer case study  (2)  Our Baking a Difference pilot project was very successful. Here is the information about it - we hope you’ll see wh…  https://t.co/rooyw5diBM   May 4, 2018 5:24 am  Footer Policies  Privacy Policy  Terms and conditions  Navigation  About  Volunteer  Donate  News  Contact us  Support our work  We work with Leicestershire&#8217;s oldest people to improve wellbeing through learning.  News categories  event  Fundraisers  In the press  Job opportunities  Projects  Uncategorized  Volunteer case study  Follow us  Copyright &#x000A9; 2018 · Learning for the Fourth Age · Charity number: 1157818 
     """
print description


should_stem  = False
new_desc = ""
if should_stem:
    text_tokens = nltk.word_tokenize(description.decode("utf-8"))
    stemmer = PorterStemmer()
    stemmed_text = [stemmer.stem(word) for word in text_tokens]
    for token in text_tokens:
        new_desc = new_desc+ " "+token
else:
    new_desc = description.decode("utf-8")
sentences = nltk.sent_tokenize(new_desc.lower())
tfidf = TfidfVectorizer().fit_transform(sentences)
cosine_similarities = linear_kernel(tfidf[0], tfidf[1:]).flatten()
print cosine_similarities
biggest_index = -1
second_index = -1
biggest_val = -1
second_val= -1
current_index = 0
for sim in cosine_similarities:
    if sim>biggest_val:
        biggest_index = current_index
        biggest_val = sim
    if sim > second_val and sim<biggest_val:
        second_val = sim
        second_index = current_index

    current_index = current_index + 1
print sentences[1:][biggest_index]
print sentences[1:][second_index]