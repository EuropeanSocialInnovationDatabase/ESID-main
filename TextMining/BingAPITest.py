import requests
import MySQLdb
from nltk import edit_distance
import nltk
from database_access import *
#Key 1: bb703c27e515480ea0dc5ea7c24e092b

#Key 2: 70b82466ba294bb1abb90158680bdbdf
db = MySQLdb.connect(host, username, password, database, charset='utf8')
cursor = db.cursor()
query = "Select * from Projects where ProjectWebpage=''"
cursor.execute(query)
results = cursor.fetchall()
subscription_key = "bb703c27e515480ea0dc5ea7c24e092b"
assert subscription_key
search_url = "https://api.cognitive.microsoft.com/bing/v7.0/search"
search_term = "Microsoft Cognitive Services"
headers = {"Ocp-Apim-Subscription-Key" : subscription_key}
for res in results:
    search_term = res[2].lower()
    search_term_tokens = nltk.word_tokenize(search_term)
    params  = {"q": search_term, "textDecorations":True, "textFormat":"HTML"}
    response = requests.get(search_url, headers=headers, params=params)
    response.raise_for_status()
    search_results = response.json()
    print "Search TERM: "+search_term
    print search_results
    webPages = search_results['webPages']['value']
    for page in webPages:
        name = page['name'].replace("<b>",'').replace('</b>','').lower()
        url = page['url']
        date_crawled = page['dateLastCrawled']
        tokens_name = nltk.word_tokenize(name)
        name_token_match = 0
        for term in search_term_tokens:
            if term in tokens_name:
                name_token_match = name_token_match + 1
        if name_token_match>=len(search_term_tokens)-1 and name_token_match>0:
            print "Match"
        print name
        print url
        print date_crawled
        print """========================="""