import MySQLdb
from TextMining.database_access import *
import csv
import sys
import os
KETs = ['http://www.gate.ac.uk/ns/ontologies/knowmak/advanced_manufacturing_technology',
        'http://www.gate.ac.uk/ns/ontologies/knowmak/mne_in_manufacturing',
        'http://www.gate.ac.uk/ns/ontologies/knowmak/advanced_materials_for_manufacturing',
        'http://www.gate.ac.uk/ns/ontologies/knowmak/biotechnology_for_manufacturing',
        'http://www.gate.ac.uk/ns/ontologies/knowmak/nanotechnologies_for_manufacturing',
        'http://www.gate.ac.uk/ns/ontologies/knowmak/photonics_for_manufacturing',
        'http://www.gate.ac.uk/ns/ontologies/knowmak/software_for_manufacturing',
        'http://www.gate.ac.uk/ns/ontologies/knowmak/advanced_materials',
        'http://www.gate.ac.uk/ns/ontologies/knowmak/advanced_polymers',
        'http://www.gate.ac.uk/ns/ontologies/knowmak/advanced_biomaterials',
        'http://www.gate.ac.uk/ns/ontologies/knowmak/advanced_ceramics',
        'http://www.gate.ac.uk/ns/ontologies/knowmak/advanced_metals',
        'http://www.gate.ac.uk/ns/ontologies/knowmak/advanced_superconductors',
        'http://www.gate.ac.uk/ns/ontologies/knowmak/novel_composites',
        'http://www.gate.ac.uk/ns/ontologies/knowmak/industrial_biotechnology',
        'http://www.gate.ac.uk/ns/ontologies/knowmak/animal_biotechnology',
        'http://www.gate.ac.uk/ns/ontologies/knowmak/applied_immunology',
        'http://www.gate.ac.uk/ns/ontologies/knowmak/assay_systems',
        'http://www.gate.ac.uk/ns/ontologies/knowmak/biologics',
        'http://www.gate.ac.uk/ns/ontologies/knowmak/biomaterials',
        'http://www.gate.ac.uk/ns/ontologies/knowmak/biomimetics',
        'http://www.gate.ac.uk/ns/ontologies/knowmak/cell_delivery',
        'http://www.gate.ac.uk/ns/ontologies/knowmak/environmental_biotechnology',
        'http://www.gate.ac.uk/ns/ontologies/knowmak/expression_systems',
        'http://www.gate.ac.uk/ns/ontologies/knowmak/gene_delivery',
        'http://www.gate.ac.uk/ns/ontologies/knowmak/genomics',
        'http://www.gate.ac.uk/ns/ontologies/knowmak/industrial_microbiology',
        'http://www.gate.ac.uk/ns/ontologies/knowmak/metabolomics',
        'http://www.gate.ac.uk/ns/ontologies/knowmak/molecular_engineering',
        'http://www.gate.ac.uk/ns/ontologies/knowmak/nanobiotechnology',
        'http://www.gate.ac.uk/ns/ontologies/knowmak/nucleic_acid_therapeutics',
        'http://www.gate.ac.uk/ns/ontologies/knowmak/oligo_delivery',
        'http://www.gate.ac.uk/ns/ontologies/knowmak/protein_and_peptide_delivery',
        'http://www.gate.ac.uk/ns/ontologies/knowmak/proteomics',
        'http://www.gate.ac.uk/ns/ontologies/knowmak/regenerative_medicine',
        'http://www.gate.ac.uk/ns/ontologies/knowmak/sequencing',
        'http://www.gate.ac.uk/ns/ontologies/knowmak/stem_cell_biotechnology',
        'http://www.gate.ac.uk/ns/ontologies/knowmak/tissue_engineering',
        'http://www.gate.ac.uk/ns/ontologies/knowmak/mems_and_nems',
        'http://www.gate.ac.uk/ns/ontologies/knowmak/actuator_technologies',
        'http://www.gate.ac.uk/ns/ontologies/knowmak/alternative_computing_technologies',
        'http://www.gate.ac.uk/ns/ontologies/knowmak/computer_memory_technologies',
        'http://www.gate.ac.uk/ns/ontologies/knowmak/energy_storage',
        'http://www.gate.ac.uk/ns/ontologies/knowmak/hardware_architectures',
        'http://www.gate.ac.uk/ns/ontologies/knowmak/microcomputing_technologies',
        'http://www.gate.ac.uk/ns/ontologies/knowmak/nanoelectronics',
        'http://www.gate.ac.uk/ns/ontologies/knowmak/passive_electronic_materials',
        'http://www.gate.ac.uk/ns/ontologies/knowmak/photonics_based_communication_technologies',
        'http://www.gate.ac.uk/ns/ontologies/knowmak/power_electronics',
        'http://www.gate.ac.uk/ns/ontologies/knowmak/rf_technologies',
        'http://www.gate.ac.uk/ns/ontologies/knowmak/semiconductor_materials_technologies',
        'http://www.gate.ac.uk/ns/ontologies/knowmak/sensor_technologies',
        'http://www.gate.ac.uk/ns/ontologies/knowmak/dna_nanotechnology',
        'http://www.gate.ac.uk/ns/ontologies/knowmak/computational_nanotechnology',
        'http://www.gate.ac.uk/ns/ontologies/knowmak/micro_and_nano_electronics',
        'http://www.gate.ac.uk/ns/ontologies/knowmak/industrial_biotechnology',
        'http://www.gate.ac.uk/ns/ontologies/knowmak/food_nanotechnology',
        'http://www.gate.ac.uk/ns/ontologies/knowmak/graphene',
        'http://www.gate.ac.uk/ns/ontologies/knowmak/nanomedicine',
        'http://www.gate.ac.uk/ns/ontologies/knowmak/nanometrology',
        'http://www.gate.ac.uk/ns/ontologies/knowmak/nanoscale_devices',
        'http://www.gate.ac.uk/ns/ontologies/knowmak/nanoscale_materials',
        'http://www.gate.ac.uk/ns/ontologies/knowmak/nanoscience_techniques_and_instrumentation',
        'http://www.gate.ac.uk/ns/ontologies/knowmak/nanotoxicology',
        'http://www.gate.ac.uk/ns/ontologies/knowmak/optics_and_photonics',
        'http://www.gate.ac.uk/ns/ontologies/knowmak/lasers_leds_and_light_sources',
        'http://www.gate.ac.uk/ns/ontologies/knowmak/applied_optics',
        'http://www.gate.ac.uk/ns/ontologies/knowmak/biophotonics',
        'http://www.gate.ac.uk/ns/ontologies/knowmak/green_photonics',
        'http://www.gate.ac.uk/ns/ontologies/knowmak/optical_materials_and_structures',
        'http://www.gate.ac.uk/ns/ontologies/knowmak/optical_metrology',
        'http://www.gate.ac.uk/ns/ontologies/knowmak/optical_physics',
        'http://www.gate.ac.uk/ns/ontologies/knowmak/optical_techniques',
        'http://www.gate.ac.uk/ns/ontologies/knowmak/optofluidics',
        'http://www.gate.ac.uk/ns/ontologies/knowmak/photoacoustics',


                ]

SGCs= [
    'http://www.gate.ac.uk/ns/ontologies/knowmak/bioeconomy',
    'http://www.gate.ac.uk/ns/ontologies/knowmak/agriculture_and_forestry',
    'http://www.gate.ac.uk/ns/ontologies/knowmak/biomass',
    'http://www.gate.ac.uk/ns/ontologies/knowmak/food_consumption',
    'http://www.gate.ac.uk/ns/ontologies/knowmak/food_production',
    'http://www.gate.ac.uk/ns/ontologies/knowmak/land_use',
    'http://www.gate.ac.uk/ns/ontologies/knowmak/animals_livestock_management',
    'http://www.gate.ac.uk/ns/ontologies/knowmak/marine_resources',
    'http://www.gate.ac.uk/ns/ontologies/knowmak/marine_technology',
    'http://www.gate.ac.uk/ns/ontologies/knowmak/climate_change_and_the_environment',
    'http://www.gate.ac.uk/ns/ontologies/knowmak/air_quality_management',
    'http://www.gate.ac.uk/ns/ontologies/knowmak/ccmt',
    'http://www.gate.ac.uk/ns/ontologies/knowmak/noise',
    'http://www.gate.ac.uk/ns/ontologies/knowmak/packaging',
    'http://www.gate.ac.uk/ns/ontologies/knowmak/soil_quality',
    'http://www.gate.ac.uk/ns/ontologies/knowmak/waste_management_and_recycling',
    'http://www.gate.ac.uk/ns/ontologies/knowmak/water_resources',
    'http://www.gate.ac.uk/ns/ontologies/knowmak/water_systems',
    'http://www.gate.ac.uk/ns/ontologies/knowmak/energy',
    'http://www.gate.ac.uk/ns/ontologies/knowmak/alternative_fuels',
    'http://www.gate.ac.uk/ns/ontologies/knowmak/biofuels',
    'http://www.gate.ac.uk/ns/ontologies/knowmak/carbon_capture_and_storage',
    'http://www.gate.ac.uk/ns/ontologies/knowmak/carbon_footprint',
    'http://www.gate.ac.uk/ns/ontologies/knowmak/concentrated_solar_power',
    'http://www.gate.ac.uk/ns/ontologies/knowmak/energy_efficiency',
    'http://www.gate.ac.uk/ns/ontologies/knowmak/energy_storage',
    'http://www.gate.ac.uk/ns/ontologies/knowmak/energy_supply',
    'http://www.gate.ac.uk/ns/ontologies/knowmak/geothermal_energy',
    'http://www.gate.ac.uk/ns/ontologies/knowmak/hydro_power',
    'http://www.gate.ac.uk/ns/ontologies/knowmak/low_carbon_technology',
    'http://www.gate.ac.uk/ns/ontologies/knowmak/nuclear_energy',
    'http://www.gate.ac.uk/ns/ontologies/knowmak/ocean_energy',
    'http://www.gate.ac.uk/ns/ontologies/knowmak/photovoltaics',
    'http://www.gate.ac.uk/ns/ontologies/knowmak/renewable_heating_and_cooling',
    'http://www.gate.ac.uk/ns/ontologies/knowmak/smart_cities_and_communities',
    'http://www.gate.ac.uk/ns/ontologies/knowmak/wind_energy',
    'http://www.gate.ac.uk/ns/ontologies/knowmak/health',
    'http://www.gate.ac.uk/ns/ontologies/knowmak/active_ageing_and_self_management_of_health',
    'http://www.gate.ac.uk/ns/ontologies/knowmak/preventing_disease',
    'http://www.gate.ac.uk/ns/ontologies/knowmak/treating_and_managing_disease',
    'http://www.gate.ac.uk/ns/ontologies/knowmak/e_health',
    'http://www.gate.ac.uk/ns/ontologies/knowmak/health_biotechnology',
    'http://www.gate.ac.uk/ns/ontologies/knowmak/health_care_provision_and_integrated_care',
    'http://www.gate.ac.uk/ns/ontologies/knowmak/health_data',
    'http://www.gate.ac.uk/ns/ontologies/knowmak/personalized_medicine',
    'http://www.gate.ac.uk/ns/ontologies/knowmak/pharmaceuticals',
    'http://www.gate.ac.uk/ns/ontologies/knowmak/social_care',
    'http://www.gate.ac.uk/ns/ontologies/knowmak/security',
    'http://www.gate.ac.uk/ns/ontologies/knowmak/catastrophe_fighting',
    'http://www.gate.ac.uk/ns/ontologies/knowmak/digital_security',
    'http://www.gate.ac.uk/ns/ontologies/knowmak/public_safety_communication',
    'http://www.gate.ac.uk/ns/ontologies/knowmak/security_equipment',
    'http://www.gate.ac.uk/ns/ontologies/knowmak/security_monitoring',
    'http://www.gate.ac.uk/ns/ontologies/knowmak/society',
    'http://www.gate.ac.uk/ns/ontologies/knowmak/co_creation',
    'http://www.gate.ac.uk/ns/ontologies/knowmak/cultural_heritage',
    'http://www.gate.ac.uk/ns/ontologies/knowmak/democracy',
    'http://www.gate.ac.uk/ns/ontologies/knowmak/education',
    'http://www.gate.ac.uk/ns/ontologies/knowmak/employment',
    'http://www.gate.ac.uk/ns/ontologies/knowmak/entrepreneurship',
    'http://www.gate.ac.uk/ns/ontologies/knowmak/global_engagement',
    'http://www.gate.ac.uk/ns/ontologies/knowmak/hate_speech_and_harassment',
    'http://www.gate.ac.uk/ns/ontologies/knowmak/knowledge_transfer',
    'http://www.gate.ac.uk/ns/ontologies/knowmak/local_engagement',
    'http://www.gate.ac.uk/ns/ontologies/knowmak/poverty',
    'http://www.gate.ac.uk/ns/ontologies/knowmak/reflective_society',
    'http://www.gate.ac.uk/ns/ontologies/knowmak/social_inequality',
    'http://www.gate.ac.uk/ns/ontologies/knowmak/transport',
    'http://www.gate.ac.uk/ns/ontologies/knowmak/aeronautics',
    'http://www.gate.ac.uk/ns/ontologies/knowmak/automobiles',
    'http://www.gate.ac.uk/ns/ontologies/knowmak/freight',
    'http://www.gate.ac.uk/ns/ontologies/knowmak/intelligent_transport',
    'http://www.gate.ac.uk/ns/ontologies/knowmak/maritime_transport',
    'http://www.gate.ac.uk/ns/ontologies/knowmak/rail_transport',
    'http://www.gate.ac.uk/ns/ontologies/knowmak/sustainable_transport',
    'http://www.gate.ac.uk/ns/ontologies/knowmak/transport_infrastructure',
    'http://www.gate.ac.uk/ns/ontologies/knowmak/urban_mobility'
]

dba = MySQLdb.connect(host, username, password, database, charset='utf8')
cursor = dba.cursor()

topic_file = open( "topic_stats.csv", 'wb')
topic_writer = csv.writer(topic_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
topic_writer.writerow(["TopicName", "Projects_appearing"])

sql = "SELECT distinct(idProjects),ProjectName,DateStart,DateEnd,ProjectWebpage FROM Projects where Exclude =0"
cursor.execute(sql)
results = cursor.fetchall()
project_KET = []
project_SGC = []
project_KET_and_SGC = []
project_KET_or_SGC = []
projects = []
projects_no_topic = []
projects_topic_under_treshold = []
topic_counts  = {}
for res in results:
    hasTopic = False
    hasKET = False
    hasSGC = False
    pro_id = res[0]
    pro_name = res[1]
    pro_web = res[4]
    projects.append(pro_id)
    sql4 = "Select * from EDSI.Project_Topics where Version like '%v3%' and Projects_idProject =" + str(pro_id)
    cursor.execute(sql4)
    results4 = cursor.fetchall()
    r_topics = []
    for res4 in results4:
        hasTopic = True
        lenght = res4[9]
        score = res4[2]
        if lenght > 100000:
            score = score * 10
        elif lenght > 50000:
            score = score * 7
        elif lenght > 30000:
            score = score * 2
        elif lenght > 10000:
            score = score * 1.7
        if score > 2:
            r_topics.append(
                {"TopicName": res4[1], "TopicScore1": res4[2], "TopicScore2": res4[3], "Keywords": res4[4],
                 "Length": lenght})
    r_topics2 = sorted(r_topics, key=lambda k: k['TopicScore1'], reverse=True)
    r_topics2 = r_topics2[:10]
    for topic in r_topics2:
        if topic['TopicName'] in SGCs:
            hasSGC = True
        if topic['TopicName'] in KETs:
            hasKET = True
        if topic['TopicName'] not in topic_counts.keys():
            topic_counts[topic['TopicName']] = 1
        else:
            topic_counts[topic['TopicName']] = topic_counts[topic['TopicName']]+1
    if hasSGC:
        project_SGC.append(pro_id)
    if hasKET:
        project_KET.append(pro_id)
    if hasKET and hasSGC:
        project_KET_and_SGC.append(pro_id)
    if hasKET or hasSGC:
        project_KET_or_SGC.append(pro_id)
    if hasKET == False and hasSGC == False and hasTopic == True:
        projects_topic_under_treshold.append([pro_id,pro_name,pro_web,"TopicUnderTreshold"])
    if hasKET == False and hasSGC == False and hasTopic == False:
        projects_no_topic.append([pro_id,pro_name,pro_web,"NoTopic"])
for t in topic_counts.keys():
    topic_writer.writerow([t,topic_counts[t]])
topic_file.close()

topic_file2 = open( "notopic_projects.csv", 'wb')
topic_writer2 = csv.writer(topic_file2, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
topic_writer2.writerow(["ProjectID", "ProjectName","ProjectWeb","Reason"])
for t in projects_topic_under_treshold:
    try:
        topic_writer2.writerow([t[0],t[1].encode('utf-8'),t[2],t[3]])
    except:
        print("Some Error")
for t in projects_no_topic:
    try:
        topic_writer2.writerow([t[0],t[1].encode('utf-8'),t[2],t[3]])
    except:
        print("Some Error")

print("projects with KET:"+str(len(project_KET)))
print("projects with SGC:"+str(len(project_SGC)))
print("projects with SGC and KET:"+str(len(project_KET_and_SGC)))
print("projects with SGC or KET:"+str(len(project_KET_or_SGC)))
print("projects total:"+str(len(projects)))