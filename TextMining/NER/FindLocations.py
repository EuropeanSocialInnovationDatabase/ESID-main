#!/usr/bin/env python
# -*- coding: utf-8 -*-
from pymongo import MongoClient
import nltk
import MySQLdb
from mordecai import Geoparser
from TextMining.database_access import *
from TextMining.NER.StanfordNER import StanfordTagger
# import requests
# import json
# from langdetect import detect
# from mtranslate import translate
# import csv
from nltk.metrics.distance import edit_distance
#import pickle
from commonregex import CommonRegex
import sys
#import threading
#reload(sys)
#sys.setdefaultencoding('utf-8')
country_codes = {
"ABW" :  "Aruba",
"AFG" : "Afghanistan",
"AGO": "Angola",
"AIA" :"Anguilla",
"ALA" :  "Åland Islands",
"ALB" : "Albania",
"AND" :  "Andorra",
"ANT" : "Netherlands Antilles",
"ARE" : "United Arab Emirates",
"ARG" :  "Argentina",
"ARM" : "Armenia",
"ASM" : "American Samoa",
"ATA" : "Antarctica",
"ATF" :  "French Southern Territories",
"ATG" :  "Antigua and Barbuda",
"AUS" : "Australia",
"AUT" : "Austria",
"AZE" : "Azerbaijan",
"BDI" : "Burundi",
"BEL" : "Belgium",
"BEN" : "Benin",
"BFA" : "Burkina Faso",
"BGD" : "Bangladesh",
"BGR" : "Bulgaria",
"BHR" : "Bahrain",
"BHS" : "Bahamas",
"BIH" : "Bosnia and Herzegovina",
"BLM" : "Saint Barthélemy",
"BLR" : "Belarus",
"BLZ" :  "Belize",
"BMU" :  "Bermuda",
"BOL" : "Bolivia",
"BRA" : "Brazil",
"BRB" : "Barbados",
"BRN" : "Brunei Darussalam",
"BTN" : "Bhutan",
"BVT" : "Bouvet Island",
"BWA" : "Botswana",
"CAF" : "Central African Republic",
"CAN" : "Canada",
"CCK" : "Cocos (Keeling) Islands",
"CHE" : "Switzerland",
"CHL" : "Chile",
"CHN" :  "China",
"CIV" : "Cote d'Ivoire",
"CMR" : "Cameroon",
"COD" : "Congo, the Democratic Republic of the",
"COG" : "Congo",
"COK" :  "Cook Islands",
"COL" :  "Colombia",
"COM" : "Comoros",
"CPV" : "Cape Verde",
"CRI" : "Costa Rica",
"CUB" : "Cuba",
"CXR" : "Christmas Island",
"CYM" :  "Cayman Islands",
"CYP" : "Cyprus",
"CZE" : "Czech Republic",
"DEU" : "Germany",
"DJI" : "Djibouti",
"DMA" : "Dominica",
"DNK" : "Denmark",
"DOM" : "Dominican Republic",
"DZA" : "Algeria",
"ECU" : "Ecuador",
"EGY" : "Egypt",
"ERI" : "Eritrea",
"ESH" : "Western Sahara",
"ESP" : "Spain",
"EST" : "Estonia",
"ETH" : "Ethiopia",
"FIN" : "Finland",
"FJI" :  "Fiji",
"FLK" :  "Falkland Islands (Malvinas)",
"FRA" : "France",
"FRO" : "Faroe Islands",
"FSM" : "Micronesia, Federated States of",
"GAB" : "Gabon",
"GBR" : "UK",
"GEO" : "Georgia",
"GGY" : "Guernsey",
"GHA" :  "Ghana",
"GIB" : "Gibraltar",
"GIN" : "Guinea",
"GLP" : "Guadeloupe",
"GMB" : "Gambia",
"GNB" : "Guinea-Bissau",
"GNQ" : "Equatorial Guinea",
"GRC" : "Greece",
"GRD" : "Grenada",
"GRL" : "Greenland",
"GTM" : "Guatemala",
"GUF" : "French Guiana",
"GUM" : "Guam",
"GUY" : "Guyana",
"HKG" : "Hong Kong",
"HMD" :  "Heard Island and McDonald Islands",
"HND" : "Honduras",
"HRV" : "Croatia",
"HTI" : "Haiti",
"HUN" : "Hungary",
"IDN" : "Indonesia",
"IMN" : "Isle of Man",
"IND" : "India",
"IOT" : "British Indian Ocean Territory",
"IRL" : "Ireland",
"IRN" : "Iran, Islamic Republic of",
"IRQ" : "Iraq",
"ISL" : "Iceland",
"ISR" : "Israel",
"XKX" : "Kosovo",
"ITA" : "Italy",
"JAM" : "Jamaica",
"JEY" : "Jersey",
"JOR" : "Jordan",
"JPN" : "Japan",
"KAZ" : "Kazakhstan",
"KEN" : "Kenya",
"KGZ" : "Kyrgyzstan",
"KHM" : "Cambodia",
"KIR" : "Kiribati",
"KNA" : "Saint Kitts and Nevis",
"KOR" : "Korea",
"KWT" :  "Kuwait",
"LAO" : "Lao People's Democratic Republic",
"LBN" : "Lebanon",
"LBR" : "Liberia",
"LBY" : "Libyan Arab Jamahiriya",
"LCA" : "Saint Lucia",
"LIE" : "Liechtenstein",
"LKA" : "Sri Lanka",
"LSO" :  "Lesotho",
"LTU" : "Lithuania",
"LUX" : "Luxembourg",
"LVA" :  "Latvia",
"MAC" : "Macao",
"MAF" :  "Saint Martin (French part)",
"MAR" : "Morocco",
"MCO" : "Monaco",
"MDA" : "Moldova",
"MDG" : "Madagascar",
"MDV" : "Maldives",
"MEX" : "Mexico",
"MHL" : "Marshall Islands",
"MKD" : "Macedonia",
"MLI" : "Mali",
"MLT" : "Malta",
"MMR" : "Myanmar",
"MNE" : "Montenegro",
"MNG" : "Mongolia",
"MNP" : "Northern Mariana Islands",
"MOZ" : "Mozambique",
"MRT" : "Mauritania",
"MSR" : "Montserrat",
"MTQ" : "Martinique",
"MUS" : "Mauritius",
"MWI" : "Malawi",
"MYS" : "Malaysia",
"MYT" : "Mayotte",
"NAM" : "Namibia",
"NCL" : "New Caledonia",
"NER" : "Niger",
"NFK" : "Norfolk Island",
"NGA" : "Nigeria",
"NIC" : "Nicaragua",
"NIU" : "Niue",
"NLD" : "Netherlands",
"NOR" : "Norway",
"NPL" : "Nepal",
"NRU" : "Nauru",
"NZL" : "New Zealand",
"OMN" : "Oman",
"PAK" : "Pakistan",
"PAN" : "Panama",
"PCN" : "Pitcairn",
"PER" : "Peru",
"PHL" : "Philippines",
"PLW" : "Palau",
"PNG" : "Papua New Guinea",
"POL" : "Poland",
"PRI" : "Puerto Rico",
"PRK" : "Democratic People's Republic of Korea",
"PRT" : "Portugal",
"PRY" : "Paraguay",
"PSE" : "Palestine",
"PYF" : "French Polynesia",
"QAT" : "Qatar",
"REU" : "Reunion",
"ROU" : "Romania",
"RUS" : "Russia",
"RWA" : "Rwanda",
"SAU" : "Saudi Arabia",
"SDN" : "Sudan",
"SEN" : "Senegal",
"SGP" : "Singapore",
"SGS" : "South Georgia and the South Sandwich Islands",
"SHN" : "Saint Helena, Ascension and Tristan da Cunha",
"SJM" : "Svalbard and Jan Mayen",
"SLB" : "Solomon Islands",
"SLE" : "Sierra Leone",
"SLV" : "El Salvador",
"SMR" : "San Marino",
"SOM" : "Somalia",
"SPM" : "Saint Pierre and Miquelon",
"SRB" : "Serbia",
"STP" : "Sao Tome and Principe",
"SUR" : "Suriname",
"SVK" : "Slovakia",
"SVN" : "Slovenia",
"SWE" : "Sweden",
"SWZ" : "Swaziland",
"SYC" : "Seychelles",
"SYR" : "Syria",
"TCA" : "Turks and Caicos Islands",
"TCD" : "Chad",
"TGO" : "Togo",
"THA" : "Thailand",
"TJK" : "Tajikistan",
"TKL" : "Tokelau",
"TKM" : "Turkmenistan",
"TLS" : "Timor-Leste",
"TON" : "Tonga",
"TTO" : "Trinidad and Tobago",
"TUN" : "Tunisia",
"TUR" : "Turkey",
"TUV" : "Tuvalu",
"TWN" : "Taiwan, Province of China",
"TZA" : "Tanzania",
"UGA" : "Uganda",
"UKR" : "Ukraine",
"UMI" : "United States Minor Outlying Islands",
"URY" : "Uruguay",
"USA" : "USA",
"UZB" : "Uzbekistan",
"VAT" : "Vatican City State",
"VCT" : "Saint Vincent and the Grenadines",
"VEN" : "Venezuela",
"VGB" : "Virgin Islands",
"VIR" : "Virgin Islands, U.S.",
"VNM" : "Viet Nam",
"VUT" : "Vanuatu",
"WLF" : "Wallis and Futuna",
"WSM" : "Samoa",
"YEM" : "Yemen",
"ZAF" : "South Africa",
"ZMB" : "Zambia",
"ZWE" :  "Zimbabwe"
}
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

def doWork():
    pass


if __name__ == '__main__':
    geo = Geoparser()
    project_names = []
    project_list = []
    print("Processing database")
    st = StanfordTagger('Resources')
    db = MySQLdb.connect(host, username, password, database, charset='utf8')
    cursor = db.cursor()
    sql_projects = "Select ProjectName,ProjectWebpage,FirstDataSource,DataSources_idDataSources,idProjects from Projects " \
                   "left join ProjectLocation on idProjects = Projects_idProjects where Exclude=0 and (Country is Null or Country = '')"
    cursor.execute(sql_projects)
    results = cursor.fetchall()
    mongo_client = MongoClient()
    mongo_db = mongo_client.ESID

    for res in results:
        output_file = open("output21.txt", 'a')
        project_names.append(res[0])
        output_file.write("\n================================\n")
        output_file.write("Project name: "+res[0])
        website = res[1]
        if website == None:
            website = ""
        output_file.write("\nWebpage: "+website)
        output_file.write("\nProject_id:"+str(res[4]))
        pro = Project()
        pro.name = res[0]
        pro.webpage = res[1]
        pro.first_datasource = res[2]
        pro.first_datasource_id = res[3]
        pro.idProject = res[4]
        project_list.append(pro)

        # processThread = threading.Thread(target=doWork, args=(pro,))  # <- note extra ','
        # processThread.start()

        documents = mongo_db.translated.find({"mysql_databaseID":str(pro.idProject)},no_cursor_timeout=True).batch_size(30)
        project_text = ""
        for doc in documents:
            project_text = project_text + doc['translation']

        # common_regex_processed = CommonRegex(project_text)
        #
        # output_file.write("\n\nLinks: " +  str(common_regex_processed.links))
        # output_file.write("\n\nEmails: " + str(common_regex_processed.emails))
        # output_file.write("\n\nPhones: " + str(common_regex_processed.phones))
        project_text = project_text.strip() #.decode('utf-8','ignore')

        short_texts = project_text.splitlines()
        classified_text = []
        for t in short_texts:
            classified_text = classified_text + st.tag_text(t)
        #st = None
        extracted_locations = []

        print(classified_text)
        loc_full_name = ""
        org_full_name = ""
        was_prev_loc = False
        was_prev_org = False
        for t in classified_text:
            if t[1]=="LOCATION":
                if was_prev_loc == False:
                    loc_full_name = loc_full_name +" "+ t[0]
                    was_prev_loc = True
                    continue
                if was_prev_loc == True:
                    loc_full_name = loc_full_name + " "+t[0]
            if t[1]!= "LOCATION":
                if was_prev_loc:
                    extracted_locations.append(loc_full_name)
                    loc_full_name = ""
                was_prev_loc = False
        freq_location = {}
        for location in extracted_locations:
            if location in freq_location:
                freq_location[location] = freq_location[location] + 1
            else:
                freq_location[location] = 1
        most_freq = ""
        freq = 0
        for loc in freq_location:
            if freq_location[loc]>freq:
                freq = freq_location[loc]
                most_freq = loc
        print("-----------")
        print("Locations:"+str(most_freq) +"   " +str(freq))
        output_file.write("\nLocations:"+str(most_freq) +"   " +str(freq))
        output_file.write("\nLocations:")
        output_file.write("\n")
        output_file.write(str(set(extracted_locations)))

        if most_freq!="" and most_freq!=None and most_freq!="Europe":
            try:
                naa = geo.geoparse(most_freq)
            except:
                print("There was an error")
                naa = ""
            if naa != ""  and naa!=[]:
                code = naa[0]['country_predicted']
                if code not in country_codes.keys():
                    continue
                country = country_codes[code]
                output_file.write("\nCountry:" + str(country))
                print("ProjectID:"+str(pro.idProject))
                print("Country:" + str(country))
                cursor.execute("INSERT INTO ProjectLocation (Type,Country,Projects_idProjects) VALUES (%s,%s,%s)",("Main",country,str(pro.idProject)))
                location_id = cursor.lastrowid
                cursor.execute("INSERT INTO DataFrom (TableName,EntityId,ColumnName,ColumnValue,DataSourceType,DataSourceName) VALUES (%s,%s,%s,%s,%s,%s)",
                               ("ProjectLocation",str(location_id),"Country",country,"AutomaticExtraction","MostFrequentLocation"))
                db.commit()

            output_file.close()
        output_file.close()
        # if most_freq!=None and most_freq!="":
        #     r = requests.get('http://maps.googleapis.com/maps/api/geocode/json?address='+most_freq)
        #     res = r.json()
        #     print res
