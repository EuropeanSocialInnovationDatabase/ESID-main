#!/usr/bin/env python
# -*- coding: utf-8 -*-
import codecs

from database_access import *
import MySQLdb
import simplejson

if __name__ == '__main__':
    insertSource = False
    idDataSource = 56
    print "Transforming SI drive data"
    fname = "si_drive_1005_bycity.json"
    with codecs.open(fname,"rb",encoding='utf-8') as f:
        se_data = f.read()
    json_data = simplejson.loads(se_data)
    #organisation_type = "Non-profit or Social Enterprise"
    db = MySQLdb.connect(host, username, password, database, charset='utf8')
    cursor = db.cursor()
    if insertSource:
        insertDataSource = "Insert into DataSources (Name,Type,URL,DataIsOpen,RelatedToEU,AssociatedProject,DataDurationStart,DataDurationEnd,Theme,CountryCoverage,SocialInnovationDef,MainEntities,DataSource)" \
                           "VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
        cursor.execute(insertDataSource,("SI-drive","Database","https://mapping.si-drive.eu/","Open","Yes","SI-Drive","2014-01-01","2018-01-01","Social innovation","all, predominantly EU","EC,2013","Projects,Actors","search and case studies"))
        db.commit()
    project_overlap = 0
    url_overlap = 0
    for item in json_data:
        city = item['city']
        city_local = item['city_local']
        country = item['country']
        regioon = item['region']
        longitude = item['lon']
        latitude = item['lat']
        projects_in_city = item['projects']
        for pro in projects_in_city:
            newProject = True
            newURL = True
            projectname_en = pro['projectname_en']
            if projectname_en!= None:
                projectname_en = projectname_en.encode('utf-8').replace('"','').replace("'",'').replace('%','')
            else:
                projectname_en=pro['projectname_orig'].encode('utf-8')
            print projectname_en
            projectname_orig = pro['projectname_orig']
            if projectname_orig==None:
                projectname_orig = projectname_en
            else:
                projectname_orig = projectname_orig.encode('utf-8').replace("'",'').replace('"','')
            existing_pro = "SELECT * from Projects where ProjectName like '%"+projectname_en+"%' or ProjectName like '%"+projectname_orig+"%'"
            cursor.execute(existing_pro)
            rows_affected = cursor.rowcount
            if rows_affected != 0:
                project_overlap = project_overlap + 1
                newProject == False

            project_stage = pro['projectstage']
            website = pro['website']
            if website !=None:
                matchingUrl = "SELECT * from Projects where ProjectWebpage like '" + website + "'"
                cursor.execute(matchingUrl)
                rows_affected_url = cursor.rowcount
                website = website.encode('utf-8')
                if rows_affected_url != 0:
                    url_overlap = url_overlap + 1
                    newURL = False
            year = pro['year']
            date = str(year) + "-01-01"
            if newProject:
                print(projectname_en+" "+date+ " "+str(website))
                newProjectQuery = "Insert into Projects (ProjectName,DateStart,ProjectWebpage,FirstDataSource,DataSources_idDataSources) VALUES ('{0}','{1}','{2}','{3}',{4})".format(projectname_en,date,website,"SI-drive",idDataSource)
                cursor.execute(newProjectQuery)
                projectid = cursor.lastrowid
                db.commit()
            else:
                UpdateProjectQuery = "Update Projects set DateStart='"+date+"', ProjectWebpage='"+website+"',FirstDataSource='"+"SI-drive"+"',DataSources_idDataSources="+idDataSource+" where ProjectName='"+projectname_en+"'"
                cursor.execute(UpdateProjectQuery)
                projectid = cursor.lastrowid
                db.commit()
            InsertLocation = "Insert into ProjectLocation (Type,City,Country,Longitude,Latitude,Projects_idProjects) VALUES ('{0}','{1}','{2}',{3},{4},{5})".format("Main",city.encode('utf-8').replace("'",""),country.encode('utf-8').replace("'",""),longitude,latitude,str(projectid))
            cursor.execute(InsertLocation)
            db.commit()
            partner_main = pro['partners']['main']
            if partner_main != {}:
                main_partner_name = partner_main['name'].encode('utf-8').replace("'",'')
                main_partner_sector = partner_main['sector']
                if main_partner_sector!= None:
                    main_partner_sector = main_partner_sector.encode('utf-8')
                main_partner_country = partner_main['country']
                if main_partner_country != None:
                    main_partner_country = main_partner_country.encode('utf-8').replace("'", "")
                PartnerExists = False
                SelectPartner  = "Select * from Actors where ActorName like '%"+main_partner_name+"%'"
                cursor.execute(SelectPartner)
                rows_affected_mainPartner = cursor.rowcount
                if rows_affected_mainPartner>0:
                    row = cursor.fetchone()
                    parner_id = row[0]
                else:
                    InsertParner = "Insert into Actors (ActorName,Type,SubType,SourceOriginallyObtained,DataSources_idDataSources)" \
                                   " Values ('{0}','{1}','{2}','{3}',{4})".format(main_partner_name,"S",main_partner_sector,"SI-Drive",str(idDataSource))
                    cursor.execute(InsertParner)
                    db.commit()
                    parner_id = cursor.lastrowid
                    ParnerLocation = "Insert into ActorLocation (Type,Country, Actors_idActors) Values('{0}','{1}',{2})".format("Headquarters",main_partner_country,str(parner_id))
                    cursor.execute(ParnerLocation)
                    db.commit()
                Connection = "Insert into Actors_has_Projects (Actors_idActors,Projects_idProjects,OrganisationRole) Values ({0},{1},'{2}')".format(parner_id,projectid,"Main partner")
                cursor.execute(Connection)
                db.commit()
            other_partners = pro['partners']['others']
            for o_partner in other_partners:
                o_partner_name = o_partner['name'].encode('utf-8').replace("'","")
                o_partner_sector = o_partner['sector']
                o_partner_country = o_partner['country']
                SelectPartner2 = "Select * from Actors where ActorName like '%" + o_partner_name + "%'"
                cursor.execute(SelectPartner2)
                rows_affected_oPartner = cursor.rowcount
                if rows_affected_oPartner > 0:
                    row = cursor.fetchone()
                    parner_id = row[0]
                else:
                    InsertParner = "Insert into Actors (ActorName,Type,SubType,SourceOriginallyObtained,DataSources_idDataSources)" \
                                   " Values ('{0}','{1}','{2}','{3}',{4})".format(o_partner_name, "S", o_partner_sector, "SI-Drive", str(idDataSource))
                    cursor.execute(InsertParner)
                    db.commit()
                    parner_id = cursor.lastrowid
                    ParnerLocation = "Insert into ActorLocation (Type,Country, Actors_idActors) Values('{0}','{1}',{2})".format("Headquarters", o_partner_country, str(parner_id))
                    cursor.execute(ParnerLocation)
                    db.commit()
                try:
                    Connection = "Insert into Actors_has_Projects (Actors_idActors,Projects_idProjects,OrganisationRole) Values ({0},{1},'{2}')".format(str(parner_id), str(projectid), "Other partner")
                    cursor.execute(Connection)
                    db.commit()
                except Exception:
                    print "Existing pair"
    print project_overlap
    print url_overlap



