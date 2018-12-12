import csv
import MySQLdb
from database_access import *

db = MySQLdb.connect(host, username, password, database, charset='utf8')
cursor = db.cursor()
city_tp = 0
city_fp = 0
city_fn = 0
country_tp = 0
country_fp = 0
country_fn = 0
total_city_in_db = 0
with open('locations_tab.csv') as csv_file:
    csv_reader = csv.reader(csv_file, delimiter=',')
    line_count = 0
    for row in csv_reader:
        project_id = row[0]
        project_name = row[1]
        city = row[3]
        country = row[4]
        if country == "United States":
            country = "USA"
        if country == "United Kingdom":
            country = "UK"
        print(country)
        cursor.execute("Select City,Country from ProjectLocation where Projects_idProjects="+str(project_id))
        results = cursor.fetchall()
        if len(results)==0:
            pass
        if len(results)==0:
            pass
        for res in results:
            if res[0]!=None and res[0]!="Null":
                total_city_in_db = total_city_in_db + 1
            if city==None or city=="":
                city_fn = city_fn + 1
            elif res[0] == None or res[0]=="Null":
                pass
            elif city.lower().replace(" ","") in res[0].lower().replace(" ",""):
                city_tp = city_tp+1
            elif city.lower().replace(" ", "") not in res[0].lower().replace(" ", "") :
                city_fp = city_fp + 1
            if country == None or country=="":
                country_fn = country_fn + 1
            elif res[1] == None:
                pass
            elif country.lower().replace(" ","") in res[1].lower().replace(" ",""):
                country_tp = country_tp+1
            elif country.lower().replace(" ", "") not in res[1].lower().replace(" ", "") :
                country_fp = country_fp + 1
print("City TP: "+str(city_tp))
print("City FP: "+str(city_fp))
print("City FN: " + str(city_fn))
city_p = float(city_tp)/(float(city_tp)+float(city_fp))
city_r = float(city_tp)/(float(city_tp)+float(city_fn))
city_f1 = 2*city_p*city_r/(city_p+city_r)
print("City precision:"+str(city_p))
print("City recall:"+str(city_r))
print("City F1:"+str(city_f1))
print("Country TP: "+str(country_tp))
print("Country FP: "+str(country_fp))
print("Country FN: " + str(country_fn))
country_p = float(country_tp)/(float(country_tp)+float(country_fp))
country_r = float(country_tp)/(float(country_tp)+float(country_fn))
country_f1 = 2*country_p*country_r/(country_p+country_r)
print("Country precision:"+str(country_p))
print("Country recall:"+str(country_r))
print("Country F1:"+str(country_f1))

print("Cities in DB:"+str(total_city_in_db))


