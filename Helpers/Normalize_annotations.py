#This file should go to the folder with annotaitons
from os import listdir
from os.path import isfile, join
mypath = "."
onlyfiles = [f for f in listdir(mypath) if isfile(join(mypath, f))]
for file in onlyfiles:
    if ".ann" in file:
        text = ""
        f = open(file, "r")
        content_lines = f.readlines()
        f.close()
        new_content_lines = []
        Objective = -1
        Output = -1
        Actor = -1
        Innovativeness = -1
        Social_Innovation = -1
        T = ""
        isSpam = False
        for content in content_lines:
            content = content.replace("SL_Objective_1a","SL_Objective_1")
            content = content.replace("SL_Objective_1b", "SL_Objective_1")
            content = content.replace("SL_Objective_1c", "SL_Objective_1")
            content = content.replace("SL_Actors_2a", "SL_Actors_2")
            content = content.replace("SL_Actors_2b", "SL_Actors_2")
            content = content.replace("SL_Actors_2c", "SL_Actors_2")
            content = content.replace("SL_Outputs_3a", "SL_Outputs_3")
            content = content.replace("SL_Outputs_3b", "SL_Outputs_3")
            content = content.replace("SL_Outputs_3c", "SL_Outputs_3")
            content = content.replace("SL_Innovativeness_4a", "SL_Innovativeness_4")
            content = content.replace("SL_Innovativeness_4b", "SL_Innovativeness_4")
            content = content.replace("SL_Innovativeness_4c", "SL_Innovativeness_4")
            if "SpamProject" in content:
                content = content.replace("SpamProject","ProjectMark")
                isSpam = True
            if "ProjectMark" in content:
                parts = content.split(" ")
                p = content.split("\t")
                T =  p[0]
            if "DL_Outputs_3a" not in content and "DL_Objective_1a" not in content and "DL_Objective_1b" not in content \
                    and "DL_Objective_1c" not in content and "DL_Innovativeness_4a" not in content and "DL_Actors_2a" not in content \
                    and "DL_Actors_2b" not in content and "DL_Actors_2c" not in content and "DL_Actors" not in content and "DL_Innovativeness" not in content\
                    and "DL_Objective" not in content and "DL_Outputs" not in content:
                new_content_lines.append(content)
            if "DL_Outputs_3a" in content or "DL_Outputs" in content:
                parts = content.split(" ")
                Output = int(parts[2])
            if "DL_Objective_1a" in content or "DL_Objective_1b" in content or "DL_Objective_1c" in content or "DL_Objective" in content:
                parts = content.split(" ")
                Ob = int(parts[2])
                if Ob>Objective:
                    Objective = Ob
            if "DL_Actors_2a" in content or "DL_Actors_2b" in content or "DL_Actors_2c" in content or "DL_Actors" in content:
                parts = content.split(" ")
                Ac = int(parts[2])
                if Ac > Actor:
                    Actor = Ac
            if "DL_Innovativeness_4a" in content or "DL_Innovativeness" in content:
                parts = content.split(" ")
                Ina = int(parts[2])
                if Ina >Innovativeness:
                    Innovativeness = Ina
            if "DL_SocialInnovation" in content:
                parts = content.split(" ")
                SI = int(parts[2])
                if SI>Social_Innovation:
                    Social_Innovation = SI

            if Objective==0 and Output==0 and Innovativeness==0 and Actor == 0:
                Social_Innovation = 0
        if isSpam:
            new_content_lines.append("A1\tDL_Objective " + T + " " + str(0) + "\n")
            new_content_lines.append("A2\tDL_Actors " + T + " " + str(0) + "\n")
            new_content_lines.append("A3\tDL_Outputs " + T + " " + str(0) + "\n")
            new_content_lines.append("A4\tDL_Innovativeness " + T + " " + str(0) + "\n")
            new_content_lines.append("A4\tDL_SocialInnovation " + T + " " + str(0) + "\n")
        else:
            new_content_lines.append("A1\tDL_Objective "+T+" "+str(Objective)+"\n")
            new_content_lines.append("A2\tDL_Actors " + T + " " + str(Actor)+"\n")
            new_content_lines.append("A3\tDL_Outputs " + T + " " + str(Output)+"\n")
            new_content_lines.append("A4\tDL_Innovativeness " + T + " " + str(Innovativeness)+"\n")
            new_content_lines.append("A4\tDL_SocialInnovation " + T + " " + str(Social_Innovation) + "\n")
        f = open(file, "w")
        f.writelines(new_content_lines)
        f.close()
