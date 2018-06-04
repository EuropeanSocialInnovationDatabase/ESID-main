import nltk
import MySQLdb
from nltk.corpus import stopwords
from my_settings import *
location_dict = {}
country_dict = {}
class Location:
    unique_id = 0
    city_name = ""
    orig_name = ""
    region = 0
    population = -1
    country = ""
    longitude = -1
    latitude = -1
class Country:
    country_name = ""
    country_code3 = ""
    country_code2 = ""
    numeric_code = ""
    population = -1
    longitude = -1
    latitude = -1
    country_name_lc = ""

db = MySQLdb.connect(host, username, password, "Semanticon", charset='utf8')
cursor = db.cursor()

def populate_dict():
    query = "SELECT * FROM Semanticon.City where Population>0"
    cursor.execute(query)
    data = cursor.fetchall()
    for row in data:
        location_dict[row[1]] = []
    for row in data:
        loc = Location()
        loc.unique_id = row[0]
        loc.city_name = row[1]
        loc.orig_name = row[2]
        loc.region = row[3]
        loc.population = row[4]
        loc.country = row[5]
        loc.longitude = row[6]
        loc.latitude = row[7]
        location_dict[loc.city_name].append(loc)
    query = "SELECT * FROM Semanticon.Country"
    cursor.execute(query)
    data = cursor.fetchall()
    for row in data:
        loc = Country()
        loc.country_name = row[0]
        loc.country_name_lc = row[0].lower()
        loc.country_code3 = row[1]
        loc.country_code2 = row[2]
        loc.numeric_code = row[3]
        loc.population = row[4]
        loc.longitude = row[5]
        loc.latitude = row[6]
        country_dict[loc.country_name_lc] = loc

populate_dict()
sent = "I have been living in New York City (United States), but most people call it just New York because it is shorter. I went to visit Belgrade, Serbia as well"

tokens = nltk.word_tokenize(sent.lower())
#Find countires
countries = []
i = 0
while i < len(tokens):
    found_key2 = ""
    if i+3<len(tokens) and tokens[i]+" "+tokens[i+1]+" "+tokens[i+2]+" "+tokens[i+3] in country_dict.keys():
        found_key2 = tokens[i]+" "+tokens[i+1]+" "+tokens[i+2]+" "+tokens[i+3]
        i = i + 3
    elif i+2<len(tokens) and tokens[i]+" "+tokens[i+1]+" "+tokens[i+2] in country_dict.keys() :
        found_key2 = tokens[i]+" "+tokens[i+1]+" "+tokens[i+2]
        i = i + 2
    elif i+1<len(tokens) and tokens[i]+" "+tokens[i+1] in country_dict.keys() :
        found_key2 = tokens[i]+" "+tokens[i+1]
        i = i + 1
    elif tokens[i] in country_dict.keys():
        found_key2 = tokens[i]
    if found_key2!="":
        countries.append(country_dict[found_key2])
    i = i + 1

# There are cities as some English stopwords, such as is, have, as, etc.
tokens = [word for word in tokens if word not in stopwords.words('english')]
cities = []
i = 0
# Find cities
while i < len(tokens):
    found_key = ""
    if i+3<len(tokens) and tokens[i]+" "+tokens[i+1]+" "+tokens[i+2]+" "+tokens[i+3] in location_dict.keys():
        found_key = tokens[i]+" "+tokens[i+1]+" "+tokens[i+2]+" "+tokens[i+3]
        i = i + 3
    elif i+2<len(tokens) and tokens[i]+" "+tokens[i+1]+" "+tokens[i+2] in location_dict.keys() :
        found_key = tokens[i]+" "+tokens[i+1]+" "+tokens[i+2]
        i = i + 2
    elif i+1<len(tokens) and tokens[i]+" "+tokens[i+1] in location_dict.keys() :
        found_key = tokens[i]+" "+tokens[i+1]
        i = i + 1
    elif tokens[i] in location_dict.keys():
        found_key = tokens[i]
    if found_key!="":
        selected = None
        citiesA = location_dict[found_key]
        for c in citiesA:
            if selected == None:
                selected = c
            if selected.population<c.population:
                selected = c
        if selected!=None:
            cities.append(selected)
    i = i + 1
cont = 0
sentA = sent
city_mentions = {}
for city in cities:
    val = sentA.lower().index(city.city_name)
    if val>=0:
        start = cont + val
        end = start + len(city.city_name)
        sentA = sentA[end-cont:]
        cont = end
        if city.city_name in city_mentions.keys():
            city_mentions[city.city_name] = city_mentions[city.city_name] + 1
        else:
            city_mentions[city.city_name] = 1
        print(city.city_name.title() + " "+str(city.population)+ " "+str(city.longitude)+" "+str(city.latitude)+"  "+str(city.unique_id) + "   "+str(start)+ "  "+str(end) )
city_max_mentions = 0
city_max_mentions_name = ""
for mention in city_mentions.keys():
    if city_max_mentions<city_mentions[mention]:
        city_max_mentions_name = mention
        city_max_mentions = city_mentions[mention]

cont = 0
sentA = sent
country_mentions = {}
for country in countries:
    val = sentA.lower().index(country.country_name_lc)
    if val>=0:
        start = cont + val
        end = start + len(country.country_name_lc)
        sentA = sentA[end-cont:]
        cont = end
        if country.country_name_lc in country_mentions.keys():
            country_mentions[country.country_name_lc] = country_mentions[country.country_name_lc] + 1
        else:
            country_mentions[country.country_name_lc] = 1
        print(country.country_name.title() + " "+str(country.country_code2)+ " "+str(country.country_code3)+" "+str(country.numeric_code)+"  "+str(country.population)+ "   "+str(country.longitude) + "   "+ str(country.latitude) +"   "+str(start)+ "  "+str(end) )


country_max_mentions = 0
country_max_mentions_name = ""
for mention in country_mentions.keys():
    if country_max_mentions<country_mentions[mention]:
        country_max_mentions_name = mention
        country_max_mentions = country_mentions[mention]

print("City with the most mentions: "+city_max_mentions_name.title())
print("Country with the most mentions: "+country_max_mentions_name.title())