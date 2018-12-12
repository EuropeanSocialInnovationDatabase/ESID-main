#!/usr/bin/env python
# -*- coding: utf-8 -*-
import nltk
import csv
import MySQLdb
from TextMining.database_access import *
from TextMining.NER.StanfordNER import StanfordTagger
from pymongo import MongoClient

# db = MySQLdb.connect(host, username, password, database, charset='utf8')
db2 = MySQLdb.connect(host, username, password, "Semanticon", charset='utf8')
# db.set_character_set("utf8")
db2.set_character_set("utf8")
# cursor = db.cursor()
# nltk.internals.config_java(options='-Xmx3024m')
cursor2 = db2.cursor()
# print("Selecting projects from mysql")
# sql_projects = "Select idProjects,ProjectName,ProjectWebpage, City, Country, Longitude, Latitude from Projects left join ProjectLocation on idProjects=Projects_idProjects where Exclude = 0 and Longitude is Null and Latitude is Null and (City is Null or City <> '')"
# cursor.execute(sql_projects)
# results = cursor.fetchall()
# csvfile = open('locations_tab.csv', 'w')
# mongo_client = MongoClient()
# mongo_db = mongo_client.ESID
# writer = csv.writer(csvfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
# for row in results:
#     idProject = row[0]
#     projectName = row[1]
#     projectWebpage = row[2]
#     projectCity = row[3]
#     ProjectCountry = row[4]
#     if ProjectCountry == "UK":
#         ProjectCountry = "United Kingdom"
#     if ProjectCountry == "USA":
#         ProjectCountry = "United States"
#     if ProjectCountry == "Russian Federation":
#         ProjectCountry = "Russia"
#     if ProjectCountry == "Polonia":
#         ProjectCountry = "Poland"
#     if projectCity == "Prishtina":
#         projectCity = "Pristina"
#     documents = mongo_db.crawl20180801_translated.find({"mysql_databaseID": str(idProject)}, no_cursor_timeout=True).batch_size(100)
#     projectText = ""
#     for doc in documents:
#         projectText = projectText+" "+doc['translation']
#     documents2 = mongo_db.crawl20180801_wayback_translated.find({"mysql_databaseID": str(idProject)}, no_cursor_timeout=True).batch_size(
#         100)
#     for doc in documents2:
#         projectText = projectText+" "+doc['translation']
    # projectText contains all the text, both from archive, description and crawled normally
projectText = """Bounce Back: For adults and youth | CMHA British Columbia===============================   Skip to Header Navigation  Skip to Primary Navigation  Skip to Content  Skip to Primary Sidebar  Skip to Footer Area Top Highlight Bar Find a CMHA branch serving your community  |  Need Help Now ? Call 310-6789 in BC   end utility-bar container Close highlight bar  end utility-bar wrap       British Columbia Division  About  Us    Contact  Us    facebook Twitter  Search CMHA British Columbia... Search   end search-container    end header-wrap    end wrap      Mental  Health    Find Help  Now    Improving Mental  Health    Mental  Illnesses    Alcohol and Other  Drugs    The Bigger  Picture    Services  Wellness  Programs    Youth  Campus  Scholarships and  Bursaries    Workplace  Suicide  Prevention    Bounce Back: Check In on Your Mental  Health    Impact  Take  Action    Influencing  Policy    Tools for  Change    Stories of  Impact    News and  Editorials    Events  Get  Involved    Donate  Volunteer  Take  Action    Become A  Member    Careers  Shop  Donate Box Donate     Search CMHA British Columbia... Donate Box Donate  About  Us    Contact  Us    Mental  Health    Find Help  Now    Improving Mental  Health    Mental  Illnesses    Alcohol and Other  Drugs    The Bigger  Picture    Services  Wellness  Programs    Youth  Campus  Scholarships and  Bursaries    Workplace  Suicide  Prevention    Bounce Back: Check In on Your Mental  Health    Impact  Take  Action    Influencing  Policy    Tools for  Change    Stories of  Impact    News and  Editorials    Events  Get  Involved    Donate  Volunteer  Take  Action    Become A  Member    Careers  Shop      end wrap    end nav_container    end primary_nav    end cmha-header    Breadcrumb NavXT 5.7.0   Home  »  Programs and Services  »  Bounce Back®: For adults and youth Bounce Back®: For adults and youth  Posted on  May 30, 2016  AddThis Sharing Buttons above  Feeling overwhelmed, tired or like you’re in a rut? Are you more worried than usual or find yourself feeling angry more easily? Bounce Back® may be able to help.  Bounce Back® teaches effective skills to help individuals (aged 15+) overcome symptoms of mild to moderate depression or anxiety, and improve their mental health. Participants can learn skills to help combat unhelpful thinking, manage worry and anxiety, and become more active and assertive.  Available for free across BC, Bounce Back® has been shown to help reduce symptoms of depression and anxiety by half, and over 90% say they would recommend it to a friend or family member. Bounce Back® is also available in regions of  Ontario  and  Manitoba .  Bounce Back® offers three forms of help:  Bounce Back Today Video  Offers practical tips on managing mood, sleeping better, building confidence, increasing activity, problem solving and healthy living. The video is available online or in DVD format in English, Cantonese and Mandarin.  How to watch the video online:  Visit  www.bouncebackvideo.ca  and use the access code bbtodaybc  How to get the DVD:  Ask your family doctor  Call us toll-free at 1-866-639-0522 or email us at  &#x62;&#x6f;&#117;nc&#x65;&#x62;&#x61;ck&#64;&#x63;&#x6d;&#104;a.&#x62;&#x63;&#x2e;&#99;a   Bounce Back® Coaching  A customized series of workbooks with 4 to 6 coaching sessions delivered by phone or video conference.  The Bounce Back® workbooks are available in English with telephone coaching in English, French, Cantonese, or Punjabi. Please talk to your doctor to request a referral to Bounce Back®‘s coaching service.  Bounce Back® Online  An independent, self-guided online program with access to video modules, e-books and worksheets.  To access Bounce Back® Online, visit  www.bouncebackonline.ca  and select ‘Register Now’ to get started.  Learn more:  Read the brochure  Preview a clip of the video  Read the Annual Report  Info for practitioners:  Download a referral form  Read our Primer for practitioners  Bounce Back® is led by CMHA BC with funding provided by the Provincial Health Services Authority.   AddThis Sharing Buttons below  Primary Sidebar Our  Services   Navigation Menu Our  Services   Wellness  Programs    Youth  Campus  Scholarships and  Bursaries    Workplace  Suicide  Prevention    Bounce Back: Check In on Your Mental  Health    Footer Section Who We  Are   About  CMHA    Our  Values    Our  History    Our Board of  Directors    Our Honorary  Patrons    Our  Staff    Annual  Reports    CMHA BC  Locations    Contact  Us    What We  Do   Services  Events  Impact  Newsletter  Media  Releases    Get  Involved    Find  Us  On:  Facebook   Twitter   Youtube   Instagram  Canadian Mental Health Association British Columbia Division Suite 905 - 1130 West Pender Street Vancouver, BC V6E 4A4  Phone:  604-688-3234  Toll-free phone:  1-800-555-8222  Fax:  604-688-3236  E-mail:  info&#64;&#99;&#109;&#x68;&#x61;&#x2e;&#x62;&#x63;&#x2e;&#x63;a  Charitable Registration No. 88844 1995 RR 0001  The main CMHA BC office is located on the traditional, unceded lands of the xʷməθkʷəy̓əm (Musqueam), Skxwxú7mesh (Squamish) and səl̓ilwətaʔɬ (Tsleil-Waututh) Nations.   end .wrap   end .footer-container  Take  Action    Shop  CMHA Info  Hub    CMHA  Connects    Donor  Login    Log in &copy; 2018  CMHA British Columbia Accessibility  Copyright and  Permissions    Privacy  Disclaimer  QUIZ_EMBEDER START  nivo lite box  end nivo lite box  QUIZ_EMBEDER END   AddThis Settings Begin   wp_footer  Major depressive disorders affect approximately 10-12% of all adults in Canada, which is around 1.5 million people, in any one year and it is forecast that within a decade they will be the second leading cause of ill health after ischaemic heart disease. Improving the mental health and well-being of adults is a major challenge that requires evidence-based social innovations that can have a significant impact on population health.The Bounce Back: Reclaim Your Health initiative was commissioned from the Canadian Mental Health Association in British Columbia by the provinces Ministry of Health in 2006. Bounce Back received an initial $6 million of funding and this enabled the Association to adopt and adapt a suitable community-based intervention for adults with anxiety and mild to moderate depression. The Association adopted and adapted the Living Life to the Full programme, developed in Scotland by Professor Chris Williams from Glasgow University, to provide a low intensity and high capacity means of providing cognitive behavioural therapy for people with major depressive disorders. The Bounce Back programme is delivered in two ways: firstly, adults can request a free DVD from Bounce Back or their primary health care centre or they can request up to 16 workbooks and received up to 5 telephone coaching sessions from one of around 20 trained coaches who can answer questions, help people to develop new skills and monitor how participants are doing. The Bounce Back coaches do not provide individual counselling but they enable and empower participants to develop coping strategies and greater resilience and a referral from a primary health care practitioner is required if a participant wants to have telephone coaching.Bounce Back was launched in 2008 and was primarily aimed at patients with long-term physical conditions who were also experiencing mental health issues but it quickly became apparent that it could also be an appropriate intervention for all adults experiencing anxiety or depression. Bounce Back offers practical tips on managing moods, building self-confidence, problem solving, healthy living and ways to increase physical and social activities that build individual resilience. Since it began operating across the whole of British Columbia (population 4.4 million), Bounce Back had distributed more than 120,000 DVDs and has grown to receive more than 25,000 referrals from more than 1,700 primary health care professionals right across the province. Around 75% of participants are female, the average age of participants is 44 years and 48 years for those who complete the course through the telephone coaching route.There is a Participant Advisory Committee that plays a role in monitoring the programme and advising on future developments and there are high levels of satisfaction with Bounce Back from participants and health care professionals. Bounce Back has improved population health by reducing the severity of depression, as measured by the PHQ9 questionnaire, by about half for those who complete the course. British Columbia is currently the only province that offers this innovative intervention as a free to use part of the health care system but it is also being trialled in Nova Scotia.In relation to the active ageing index, the Bounce Back programme has had measurable positive effects on mental well-being by reducing the severity of anxiety and depression among participants who have completed the course. The programme is based on the general principles of cognitive behavioural therapy so it encourages individuals to be more socially connected and to take more physical exercise as ways of improving general mood."""

cities = {}
countries = {}
try:
    st_tagger = StanfordTagger('../Resources')
    tags = st_tagger.tag_text(projectText)
    #print tags
    for tag in tags:
        if tag[1]=='LOCATION':# Check whether city
            new_sql = "SELECT City,Country_CountryName,Longitude,Latitude FROM Semanticon.City where city like '{0}' and Population>0".format(
                tag[0].encode('utf-8'))
            # print new_sql
            try:
                cursor2.execute(new_sql)
                results2 = cursor2.fetchall()
                FoundCity = ""
                FoundCountry = ""
                found = False
                for r in results2:
                    FoundCity = r[0]
                    FoundCountry = r[1]
                    if FoundCity not in cities.keys():
                        cities[str(FoundCity)] = 1
                    else:
                        cities[str(FoundCity)] = cities[str(FoundCity)] + 1
                    if FoundCountry not in countries.keys():
                        countries[str(FoundCountry)] = 1
                    else:
                        countries[str(FoundCountry)] = countries[str(FoundCountry)] + 1
                new_sql = "SELECT CountryName FROM Semanticon.Country where CountryName like '{0}'".format(
                    tag[0].encode('utf-8'))
                # print new_sql
                cursor2.execute(new_sql)
                results2 = cursor2.fetchall()
                for r in results2:
                    FoundCountry = r[0]
                    if FoundCountry not in countries.keys():
                        countries[str(FoundCountry)] = 1
                    else:
                        countries[str(FoundCountry)] = countries[str(FoundCountry)] + 1
            except:
                print("Cannot handle string: "+tag[0])
except:
    print("Tagger cannot handle this project")
print cities
print countries
max_city = ""
max_city_count = 0
max_country = ""
max_country_count = 0
for city in cities:
    new_sql = "SELECT CountryName FROM Semanticon.Country where CountryName like '{0}'".format(
        city.encode('utf-8'))
    # print new_sql
    cursor2.execute(new_sql)
    results2 = cursor2.fetchall()
    if len(results2)>0:
        continue
    if city == "uk":
        continue
    if city == "republic":
        continue
    if cities[city]>max_city_count:
        max_city_count = cities[city]
        max_city = city
for country in countries:
    if countries[country]>max_country_count:
        max_country_count = countries[country]
        max_country = country
print "Max city:"+max_city
print "Max country:"+max_country
    #writer.writerow([idProject,projectName.encode('utf-8'),projectWebpage.encode('utf-8'),max_city.encode('utf-8'),max_country.encode('utf-8')])
