# -*- coding: utf-8 -*-
import json

import requests

s = """Webmasters - Hungarian Maltese Aid Service =============================== Top navbar toggle Toggle Navigation Top Top Navbar Lists Contact Language (HU) Language (EN) EN DE /.navbar-collapse /.container-fluid Top navbar toggle Toggle navigation Top navbar lists Nursing jobs Spiritual support Lifestyle and nutrition Career counseling Service map Legal advice /.navbar-collapse /.container-fluid slider Indicators Wrapper for slides Affiliated with Home Care Home care Home Controls Previous Next Nursing Tasks Spiritual Support Service Map Nutrition & Lifestyle Spiritual Support Spiritual Care The Power of Love With Christian Eye Holiday and Leisure: Sunday Thinking Spiritual Support Spiritual Support Spiritual Care Our Resources I. With Christian eyes Endre Gyökössy: Love or Justice? All Entries Nutrition and lifestyle Lifestyle and nutrition The ingredients and processes of Hungarian cuisine for a healthy diet Part 2 Vegetables and vegetables Lifestyle and nutrition Healthy nutrition and dietary supplements Lifestyle and nutrition Dietary role in home care Lifestyle and nutrition Healthy nutrition principles All entries Recipes Eggplant cream Broccoli millet Mushroom poppy Poppy inflated All entries Featured topics donation Alzheimer's crib dementia depression health lifestyle hit interview poetry art psychology love nutrition poem Nursing tasks Home nursing is not an easy task in which we want to help you. Please take a look your videos. Who cares for you? Elderly Child Injured Search All Videos View All Nursing Videos Andrea Gál Andrea Gál I am a graduate nurse, an intensive nursing and anesthesiologist, I participated in the preparation of short films under the Nursing Tasks menu and help you in their care duties. Ask the Expert Zsuzsanna Jáki I am Zsuzsanna Jáki, a psychologist and spiritual counselor. In this section I strive to make the writings here to be a spiritual support for the sick, the carers and all our readers during everyday struggles. I'm asking the expert for advice The power of love The holiday and the time of rest: Thoughts from Sunday Spiritual support Our resources I. Endre Gyökössy: Love or justice? Spiritual support from Lourdes to Dobogókő When I am ill, gem's first thought was that for some spiritual reason I got something wrong. That is, you are not bacillus or v 'iacute; rus a & bdquo; hib & aacute; s & rdquo; . This is the assumed & eacute; st """

r = requests.post("http://services.gate.ac.uk/knowmak/classifier/project", data=s)
print(r.status_code, r.reason)
data = json.loads(r.text)
for clas in data["classification"]:
    keywords = ""
    for key in data["classification"][clas]["keywords"]:
        keywords = keywords+","+key
    keywords = keywords[1:]
    print([clas,data["classification"][clas]["score"][0],data["classification"][clas]["score"][1],keywords])