from database_access import *
import MySQLdb
import sys
import csv
import datetime

class Organisation:
    def __init__(self):
        self.database_id = -1
        self.organisation_name = "" # ActorName
        self.WelfareRegime = ""
        self.country = ""  # Location.City
        self.theme = ""
        self.target_group = ""
        self.established = ""
        self.type_of_org = ""
        self.size = ""
        self.description = ""



if __name__ == '__main__':
    print("Starting SIMPACTTransformer")
    if(len(sys.argv)<2):
        print "This scripts needs one arguments: csv with organisations"
        exit(1)
    db = MySQLdb.connect(host, username, password, database, charset='utf8')
    cursor = db.cursor()
    organisations_arg = sys.argv[1]
    organisations = []
    with open(organisations_arg, 'rb') as csvfile:
        orgreader = csv.reader(csvfile, delimiter=';', quotechar='"')
        i = 0
        for row in orgreader:
            if(i==0):
                i+=1
                continue
            org = Organisation()
            org.organisation_name = row[0]
            org.WelfareRegime = row[1]
            org.country = row[2]
            org.theme = row[3]
            org.target_group = row[4]
            org.established = row[5]
            org.type_of_org = row[6]
            org.size = row[7]
            org.description = row[8]
            organisations.append(org)
            i+=1
    for organisation in organisations:
        print "Saving "+organisation.organisation_name
        sql_org = "Insert into Actors (ActorName,Type,SubType,StartDate,SourceOriginallyObtained,DataSources_idDataSources) VALUES ('{0}','{1}','{2}','{3}','{4}','{5}')"
        cursor.execute(sql_org.format(organisation.organisation_name, 'S',organisation.type_of_org,str(organisation.established)+"-01-01",
                                 'SIMPACT',13))
        org_id_inTable = cursor.lastrowid
        organisation.database_id = org_id_inTable
        db.commit()

        sql_loc = "Insert into ActorLocation (Type,Country,Actors_idActors) VALUES " \
                      "(%s,%s,%s)"
        cursor.execute(sql_loc, ("Headquarters", organisation.country,
                                     organisation.database_id))
        db.commit()

        sql_short_desc = "Insert into ActorsAdditionalData (FieldName,FieldContent,Actors_idActors,DateObtained,SourceURL)" \
                         "VALUES(%s,%s,%s,NOW(),%s)"
        cursor.execute(sql_short_desc, (
        "WelfareRegime", organisation.WelfareRegime, organisation.database_id, "http://www.simpact-project.eu/evidence/sicases/index.htm"))
        db.commit()

        sql_theme = "Insert into ActorsAdditionalData (FieldName,FieldContent,Actors_idActors,DateObtained,SourceURL)" \
                         "VALUES(%s,%s,%s,NOW(),%s)"
        cursor.execute(sql_theme, (
            "Theme", organisation.theme, organisation.database_id,
            "http://www.simpact-project.eu/evidence/sicases/index.htm"))
        db.commit()

        sql_impact = "Insert into ActorsAdditionalData (FieldName,FieldContent,Actors_idActors,DateObtained,SourceURL)" \
                       "VALUES(%s,%s,%s,NOW(),%s)"
        cursor.execute(sql_impact, (
            "TargetGroup", organisation.target_group, organisation.database_id,
            "http://www.simpact-project.eu/evidence/sicases/index.htm"))
        db.commit()

        sql_notes = "Insert into ActorsAdditionalData (FieldName,FieldContent,Actors_idActors,DateObtained,SourceURL)" \
                     "VALUES(%s,%s,%s,NOW(),%s)"
        cursor.execute(sql_notes, (
            "Size", organisation.size, organisation.database_id,
            "http://www.simpact-project.eu/evidence/sicases/index.htm"))
        db.commit()
        sql_contact = "Insert into ActorsAdditionalData (FieldName,FieldContent,Actors_idActors,DateObtained,SourceURL)" \
                     "VALUES(%s,%s,%s,NOW(),%s)"
        cursor.execute(sql_contact, (
            "Description", organisation.description, organisation.database_id,
            "http://www.simpact-project.eu/evidence/sicases/index.htm"))
        db.commit()
    print "Done!!!!"
