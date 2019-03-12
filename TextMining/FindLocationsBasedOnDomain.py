#!/usr/bin/env python
# -*- coding: utf-8 -*-
from pymongo import MongoClient
import nltk
import MySQLdb
from database_access import *
from NER.StanfordNER import StanfordTagger
import requests
import json
from langdetect import detect
from mtranslate import translate
import csv
from nltk.metrics.distance import edit_distance
import pickle
from commonregex import CommonRegex
import sys
import threading
from urlparse import urlparse
reload(sys)
sys.setdefaultencoding('utf-8')

class Project:
    def __init__(self):
        self.name = ""
        self.webpage = ""
        self.first_datasource = ""
        self.first_datasource_id = -1
        self.idProject = -1

def find_org(org,tokens):
    org_tokens = nltk.word_tokenize(org)
    l_org_tokens = len(org_tokens)
    for i in range(0,len(tokens)-l_org_tokens+1):
        pot = tokens[i:(i+l_org_tokens)]
        pot_s = ' '.join(pot)
        distance = edit_distance(pot_s.lower(),org.lower())
        if float(distance)/float(len(org))<0.1:
            return True
    return False

domainMap = {
   # ".ac":"Ascension Island",
    ".ad":"Andorra",
    ".ae":"United Arab Emirates",
    ".af":"Afghanistan",
    ".ag":"Antigua and Barbuda",
    ".ai":"Anguilla",
    ".al" : "Albania",
    ".am" : "Armenia",
    ".an" : "Netherlands Antilles",
    ".ao" : "Angola",
    ".aq" : "Antarctica",
    ".ar" : "Argentina",
    ".as" : "American Samoa",
    ".at" : "Austria",
    ".au" : "Australia",
    ".aw" : "Aruba",
    ".ax" : "Åland",
    ".az" : "Azerbaijan",
    ".ba" : "Bosnia and Herzegovina",
    ".bb" : "Barbados",
    ".bd" : "Bangladesh",
    ".be" : "Belgium",
    ".bf" : "Burkina Faso",
    ".bg" : "Bulgaria",
    ".bh" : "Bahrain",
    ".bi" : "Burundi",
    ".bj" : "Benin",
    ".bm" : "Bermuda",
    ".bn" : "Brunei",
    ".bo" : "Bolivia",
    ".br" : "Brazil",
    ".bs" : "Bahamas",
    ".bt" : "Bhutan",
    ".bv" : "Bouvet Island",
    ".bw" : "Botswana",
    ".by" : "Belarus",
    ".bz" : "Belize",
    ".ca" : "Canada",
    ".cc" : "Cocos(Keeling) Islands",
    ".cd" : "Democratic Republic of the Congo",
    ".cf" : "Central African Republic",
    ".cg" : "Republic of the Congo",
    ".ch" : "Switzerland",
    ".ci" : "Cote d'Ivoire",
    ".ck" : "Cook Islands",
    ".cl" : "Chile",
    ".cm" : "Cameroon",
    ".cn" : "People's Republic of China",
    ".co": "Colombia",
    ".cr" : "Costa Rica",
    ".cs" : "Czechoslovakia",
    ".cu" : "Cuba",
    ".cv" : "Cape Verde",
    ".cw" : "Curaçao",
    ".cx": "Christmas Island",
    ".cy" : "Cyprus",
    ".cz" : "Czech Republic",
    ".dd" : "East Germany",
    ".de" : "Germany",
    ".dj" : "Djibouti" ,
    ".dk" : "Denmark",
    ".dm" : "Dominica" ,
    ".do" : "Dominican Republic",
    ".dz" : "Algeria",
    ".ec" : "Ecuador",
    ".ee" : "Estonia",
    ".eg" : "Egypt",
    ".eh" : "Western Sahara",
    ".er" : "Eritrea",
    ".es" : "Spain",
    ".et" : "Ethiopia",
    #".eu" : "European Union",
    ".fi" : "Finland",
    ".fj" : "Fiji",
    ".fk" : "Falkland Islands",
    ".fm" : "Federated States of Micronesia",
    ".fo" : "Faroe Islands",
    ".fr" : "France",
    ".ga" : "Gabon",
    ".gb" : "United Kingdom",
    ".gd" : "Grenada",
    ".ge" : "Georgia",
    ".gf" : "French Guiana",
    ".gg" : "Guernsey",
    ".gh" : "Ghana",
    ".gi"  :"Gibraltar",
    ".gl" : "Greenland",
    ".gm" : "Gambia",
    ".gn" : "Guinea",
    ".gp" : "Guadeloupe",
    ".gq" : "Equatorial Guinea",
    ".gr" : "Greece",
    ".gs" : "South Georgia and the South Sandwich Islands",
    ".gt" : "Guatemala",
    ".gu" : "Guam",
    ".gw" : "Guinea - Bissau",
    ".gy" : "Guyana",
    ".hk" : "Hong Kong",
    ".hm" : "Heard Island and McDonald Islands",
    ".hn" : "Honduras",
    ".hr" : "Croatia",
    ".ht" : "Haiti",
    ".hu" : "Hungary",
    ".id" : "Indonesia",
    ".ie" : "Ireland",
    ".il" : "Israel",
    ".im" : "Isle of Man",
    ".in" : "India",
    #".io" : "British Indian Ocean Territory",
    ".iq" : "Iraq",
    ".ir" : "Iran",
    ".is" : "Iceland",
    ".it" : "Italy",
    ".je" : "Jersey",
    ".jm" : "Jamaica",
    ".jo" : "Jordan",
    ".jp" : "Japan",
    ".ke" : "Kenya",
    ".kg" : "Kyrgyzstan",
    ".kh" : "Cambodia",
    ".ki" : "Kiribati",
    ".km" : "Comoros",
    ".kn" : "Saint Kitts and Nevis",
    ".kp" : "Democratic People's Republic of Korea",
    ".kr" : "Republic of Korea",
    ".kw" : "Kuwait",
    ".ky" : "Cayman Islands",
    ".kz" :"Kazakhstan",
    ".la" : "Laos",
    ".lb" : "Lebanon",
    ".lc" : "Saint Lucia",
    ".li" : "Liechtenstein",
    ".lk" : "Sri Lanka",
    ".lr" : "Liberia",
    ".ls" : "Lesotho",
    ".lt" : "Lithuania",
    ".lu" : "Luxembourg",
    ".lv" : "Latvia",
    ".ly" : "Libya",
    ".ma" : "Morocco",
    ".mc" : "Monaco",
    ".md" : "Moldova",
   # ".me" : "Montenegro",
    ".mg" : "Madagascar",
    ".mh" : "Marshall Islands",
    ".mk" : "Macedonia",
    ".ml" : "Mali",
    ".mm" : "Myanmar",
    ".mn" : "Mongolia",
    ".mo" : "Macau",
    ".mp" : "Northern Mariana Islands",
    ".mq" : "Martinique",
    ".mr" : "Mauritania",
    ".ms" : "Montserrat",
    ".mt" : "Malta",
    ".mu" : "Mauritius",
    ".mv" : "Maldives",
    ".mw" : "Malawi",
    ".mx" : "Mexico",
    ".my" : "Malaysia",
    ".mz" : "Mozambique",
    ".na" : "Namibia",
    ".nc" : "New Caledonia",
    ".ne" : "Niger",
    ".nf" : "Norfolk Island",
    ".ng" : "Nigeria",
    ".ni" : "Nicaragua",
    ".nl" : "Netherlands",
    ".no" : "Norway",
    ".np" : "Nepal",
   ".nr" : "Nauru",
    ".nu" : "Niue",
    ".nz" : "New Zealand",
    ".om" : "Oman",
    ".pa" : "Panama",
    ".pe" : "Peru",
    ".pf" : "French Polynesia",
    ".pg" : "Papua New Guinea",
    ".ph" : "Philippines",
    ".pk" : "Pakistan",
    ".pl" : "Poland" ,
    ".pm" : "Saint - Pierre and Miquelon",
    ".pn" : "Pitcairn Islands",
    ".pr" : "Puerto Rico",
    ".ps" : "Palestine",
    ".pt" : "Portugal",
    ".pw" : "Palau",
    ".py" : "Paraguay",
    ".qa" : "Qatar",
    ".re" : "Reunion",
    ".ro" : "Romania",
    ".rs" : "Serbia",
    ".ru" : "Russia",
    ".rw" : "Rwanda",
    ".sa" : "Saudi Arabia",
    ".sb" : "Solomon Islands",
    ".sc" : "Seychelles",
    ".sd" : "Sudan",
   ".se" : "Sweden",
    ".sg" : "Singapore",
    ".sh" : "Saint Helena",
    ".si" : "Slovenia",
    ".sj" : "Svalbard and Jan Mayen Islands",
    ".sk" : "Slovakia" ,
    ".sl" : "Sierra Leone",
    ".sm" : "San Marino",
    ".sn": "Senegal",
   ".so":"Somalia",
    ".sr" : "Suriname",
    ".ss": "South Sudan",
    ".st" : "Sao Tome and Principe",
    ".su" : "Soviet Union",
    ".sv" : "El Salvador",
    ".sx" : "Sint Maarten",
    ".sy" : "Syria",
   ".sz" : "Swaziland",
    ".tc" : "Turks and Caicos Islands",
    ".td" : "Chad",
    ".tf" : "French Southern and Antarctic Lands",
    ".tg" : "Togo",
    ".th" : "Thailand",
    ".tj" : "Tajikistan",
    ".tk" : "Tokelau",
    ".tl" : "East Timor",
    ".tm" : "Turkmenistan",
    ".tn" :"Tunisia",
    ".to" : "Tonga",
    ".tp" : "East Timor",
    ".tr" : "Turkey",
    ".tt" : "Trinidad and Tobago",
    ".tv" : "Tuvalu",
    ".tw" : "Taiwan",
    ".tz" : "Tanzania",
   ".ua" : "Ukraine",
    ".ug" : "Uganda",
    ".uk" : "UK",
    ".us" : "USA",
    ".uy" : "Uruguay",
    ".uz" : "Uzbekistan",
    ".va" : "Vatican City",
    ".vc" : "Saint Vincent and the Grenadines",
    ".ve" : "Venezuela",
    ".vg" : "British Virgin Islands",
    ".vi" : "United States Virgin Islands",
    ".vn" : "Vietnam",
    ".vu" : "Vanuatu",
   ".wf" : "Wallis and Futuna",
    ".ws" : "Samoa",
    ".ye" : "Yemen",
    ".yt" : "Mayotte",
    ".yu" : "Yugoslavia",
    ".za" : "South Africa",
   ".zm" : "Zambia",
    ".zw" : "Zimbabwe"

}

if __name__ == '__main__':



    project_names = []
    project_list = []
    print("Processing database")
    db = MySQLdb.connect(host, username, password, database, charset='utf8')
    cursor = db.cursor()
    sql_projects = "Select ProjectName,ProjectWebpage,FirstDataSource,DataSources_idDataSources,idProjects, Country, City from Projects left join ProjectLocation on idProjects = Projects_idProjects where (Country is Null or Country = '') and Exclude=0"
    cursor.execute(sql_projects)
    results = cursor.fetchall()

    for res in results:
        output_file = open("output2.txt", 'a')
        project_names.append(res[0])
        output_file.write("\n================================\n")
        output_file.write("Project name: "+res[0])
        if res[1]!=None:
            output_file.write("\nWebpage: "+res[1])
        output_file.write("\nProject_id:"+str(res[4]))
        pro = Project()
        pro.name = res[0]
        pro.webpage = res[1]
        pro.first_datasource = res[2]
        pro.first_datasource_id = res[3]
        pro.idProject = res[4]
        project_list.append(pro)
        country = ""

        if pro.webpage!=None and pro.webpage!="":
            print pro.webpage
            if "http://" not in pro.webpage and "https://" not in pro.webpage:
                pro.webpage = "http://"+pro.webpage
            domain = urlparse(pro.webpage).hostname
            print domain

            ext = domain.split(".")[-1]
            if "."+str(ext) in domainMap.keys():
                country = domainMap["."+str(ext)]
        print "-----------"
        print "Locations:"+str(country)
        if country!="":
            cursor.execute("Insert into ProjectLocation(Type,Country,Projects_idProjects,FoundWhere,DataTrace) VALUES (%s,%s,%s,%s,%s)",("Main",country,str(pro.idProject),"Domain extension","Country found from domain"))
            db.commit()
            output_file.write("\nLocations:"+str(country))
            output_file.close()