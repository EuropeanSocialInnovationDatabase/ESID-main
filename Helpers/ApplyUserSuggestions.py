import MySQLdb
from database_access import *

dba = MySQLdb.connect(host, username, password, database, charset='utf8')
cursor = dba.cursor()
select_sql = "Select * from user_suggestions where Applied=0"
cursor.execute(select_sql)
user_suggestions = cursor.fetchall()
for us in user_suggestions:
    id = us[0]
    print(id)
    uname = us[1]
    add_suggestion = us[2]
    edit_suggestion = us[3]
    project_id = us[4]
    date_time = us[5]
    table_name = us[6]
    table_field = us[7]
    filed_value = us[8]
    if filed_value!=None:
        filed_value = filed_value.strip()
    entry_id = us[9]
    comment = us[10]
    if edit_suggestion == 1:
        if table_name == "ProjectLocation":
            edit_sql = "Update "+table_name+" set "+table_field+"= '"+filed_value+"' where Projects_idProjects="+str(project_id)
        if table_name == "Projects":
            if table_field=="ProjectWebsite":
                table_field = "ProjectWebpage"
                edit_sql = "Update " + table_name + " set " + table_field + "= '" + filed_value + "',CrawlAgain=1 where idProjects=" + str(
                    project_id)
        if table_name.strip() == "Project_Topics":
            print("here")
            if filed_value == '0':
                print("exclude")
                edit_sql = "Update Project_Topics set Exclude = 1 where idTopics = "+str(entry_id)
            # else:
            #     print("insert")
            #     edit_sql = "Insert into Project_Topics (TopicName,TopicScore,TopicScore2,Projects_idProject,Comment,Version,Sources,Text_length,Exclude) " \
            #                "Values ('{0}',{1},{2},'{3}','{4}','{5}','{6}',{7},{8})".format(filed_value,500,500,project_id,"Manual applied","Manually added","Human annotators",0,0)
            #edit_sql = "Update "+table_name+" set "+table_field+"= '"+filed_value+"' where idProjects="+str(entry_id)
        if table_name == "Actors":
            edit_sql = "Update "+table_name+" set "+table_field+"= '"+filed_value+"' where idActors="+str(entry_id)
        if table_name == "TypeOfSocialInnotation":
            edit_sql = "Update TypeOfSocialInnotation set "+table_field+"= '"+filed_value+"' where Projects_idProjects="+str(project_id)

        if table_name == "AdditionalProjectData":
            edit_sql = "Update " + table_name + " set Value= '" + filed_value + "' where FieldName='"+table_field+"' and Projects_idProjects=" + str(project_id)

        cursor.execute(edit_sql)
        update_sql = "Update user_suggestions set Applied=1 where id_suggestion="+str(id)
        cursor.execute(update_sql)
        dba.commit()
    if add_suggestion==1:
        if table_name.strip() == "Project_Topics":
            print("insert")
            edit_sql = "Insert into Project_Topics (TopicName,TopicScore,TopicScore2,Projects_idProject,Comment,Version,Sources,Text_length,Exclude) " \
                       "Values ('{0}',{1},{2},'{3}','{4}','{5}','{6}',{7},{8})".format(filed_value, 500, 500,
                                                                                       project_id, "Manual applied",
                                                                                       "Manually added",
                                                                                       "Human annotators", 0, 0)
            cursor.execute(edit_sql)
        update_sql = "Update user_suggestions set Applied=1 where id_suggestion=" + str(id)
        cursor.execute(update_sql)
        dba.commit()
