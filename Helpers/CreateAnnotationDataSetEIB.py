#!/usr/bin/env python
# -*- coding: utf-8 -*-
from pymongo import MongoClient
import nltk
import MySQLdb
from database_access import *
import os
import csv
import re
from HTMLParser import HTMLParser

class MLStripper(HTMLParser):
    def __init__(self):
        self.reset()
        self.fed = []
    def handle_data(self, d):
        self.fed.append(d)
    def get_data(self):
        return ' '.join(self.fed)
def strip_tags(html):
    s = MLStripper()
    s.feed(html)
    return s.get_data()

if __name__ == '__main__':
    if not os.path.exists("ESID-data3"):
        os.makedirs("ESID-data3")
    client = MongoClient()
    db = client.ESID
    project_text = {}
    everything = db.EIBCompetition7.find({},no_cursor_timeout=True).batch_size(30)
    i = 1
    for pro in everything:
        try:
            name = pro["domain"]
            page_title = pro["page_title"]

            if name in project_text.keys():
                if pro["text"] in project_text[name]:
                    continue
                project_text[name]=project_text[name]+"\r\n---------------------------------------\r\nNEW PAGE: "+page_title+ "\r\n\r\n"+pro["text"]
            else:
                project_text[name]="\r\n---------------------------------------\r\nNEW PAGE: "+page_title+ "\r\n\r\n"+pro["text"]
            print "item "+str(i)
            i = i+1
        except Exception as ex:
            print ex.message
            print "Exception: Record ignored"
    print "Writing files"
    too_large = 0
    too_small = 0
    total = 0
    total_in_scope = 0
    allowed_domains = ["adoptaunabuelo.org", "arborea.io", "coloradd.net", "discovering-hands.de",
                       "givevision.net",
                       "kaitiaki.it", "magikme.net", "mycarematters.org", "refugeeswork.at",
                       "freebirdclub.com",
                       "ultraspecialisti.com", "walkwithpath.com", "iosmosi.com",
                       "edukit.org.uk", "sharingacademy.com", "silentsecret.com", "aprendicesvisuales.org",
                       "biocarbonengineering.com",
                       "lazzus.com", "desolenator.com", "mycarematters.org", "ithacalaundry.gr",
                       "fitforkids.dk",
                       "feelif.com", "bgood.at", "blitab.com", "designbypana.com", "ecosia.org",
                       "fitforkids.dk", "koiki.eu", "letsgetsporty.com", "marioway.it",
                       "peppypals.com", "bluebadgestyle.com", "adie.org", "clear-village.org",
                       "thedoschool.org",
                       "helioz.org", "mattecentrum.se", "1toit2ages.be", "bikway.com",
                       "buuv.nu", "organery.co", "ortialti.com", "theyardtheatre.co.uk",
                       "bincome.eu", "bc4gd.com", "wikihouse.cc", "collaction.org", "cultivai.com",
                       "thirdageireland.ie", "feelif.com",
                       "leapslab.com", "inclu-sight.com", "fightthestroke.org", "dialogue-se.com",
                       "mouse4all.com"
                       "openbiomedical.org", "scribeasy.com", "saga.one", "siboxapp.com", "signly.co",
                       "solomon.gr", "barrabes.biz",
                       "wayfindr.net", "action.neweconomics.org", "cucula.org", "themachinetobeanother.org",
                       "aid.technology",
                       "micro-rainbow.org", "solidaritysalt.com", "thebikeproject.co.uk",
                       "adamantbionrg.com", "habibi.at", "mygrantour.org",
                       "coreorient.com", "refugeeswork.at", "learningunlimited.co", "wedocare.dei.uc.pt",
                       "thefreebirdclub.com", "wheeliz.com",
                       "melawear.de", "jakodoma.org", "ssmsapp.com", "galiboff.com", "roda.hr",
                       "instituteintercer.org", "loveyourwaste.com", "crowdfundhq.com",
                       "cfmitalia.it", "tasksquadhq.com", "hazelheartwood.com", "theurbanfarmer.co",
                       "happyfeetpreschool.net", "scn.org", "ipn.pt",
                       "grc.engineering.cf.ac.uk", "science-link.eu", "biobasenwe.org", "innove.ee",
                       "greenpolis.fi", "seap-alps.eu", "cteg.org.uk",
                       "eoi.es", "mka.malopolska.pl", "olsztyn.eu", "exeko.org", "rdsp.com",
                       "rootsofempathy.org", "janeswalk.org", "jumpmath.org",
                       "simprints.com", "hippogriff.se"]
    with open('projects_stats.csv', 'wb') as csvfile:
        csv_writer = csv.writer(csvfile, delimiter=',',
                                quotechar='"', quoting=csv.QUOTE_MINIMAL)
        for item in project_text:
            total = total + 1

            tokens = nltk.word_tokenize(project_text[item])
            if len(tokens)<500 or len(tokens)>25000:
                if len(tokens)<500:
                    too_small = too_small+1
                if len(tokens)>25000:
                    too_large = too_large +1
                #continue
            project_text[item] = re.sub(r'(\n\s*)+\n+', '\n\n', project_text[item])
            f = open('ESID-data3/p_'+item+".txt", 'w')
            f.write(project_text[item].encode('utf-8').strip())  # python will convert \n to os.linesep
            f.write("\r\n WHOLE PROJECT MARK")
            f.close()
            f1 = open('ESID-data3/p_' + item + ".ann", 'w')
            f1.write("")
            f1.close()
            if item in allowed_domains:
                csv_writer.writerow([item,len(tokens),"True"])
                total_in_scope = total_in_scope+1
            else:
                csv_writer.writerow([item, len(tokens), "False"])
    print "Too Large:"+str(too_large)
    print "Too Small:"+str(too_small)
    print "Total projects:"+str(total)
    print "Total projects in scope:" + str(total_in_scope)

    print "Done"