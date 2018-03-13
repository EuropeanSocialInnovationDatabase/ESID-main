# -*- coding: utf-8 -*-
import requests
import json
project_text = """
A social financial system where inflation is transformed into basic income using blockchain.

We believe that basic income is inevitable because of the growing optimisation and automation in almost every sector of our society, which probably will lead to loss of numerous jobs. The programmable nature of blockchain technology is making it possible to introduce a fair way to create a basic income. The idea is to issue a blockchain-based token (cryptocurrency) programmed with a negative interest in currency board with a fiat currency 1:1. The fairness is in the financing of the basic income, which will come not from the societal consumption, but from the storage of means.


"""

r = requests.post("http://services.gate.ac.uk/knowmak/classifier/project", data=project_text.encode('ascii','ignore'))
print(r.status_code, r.reason)
print(r.text)
data = json.loads(r.text)
for clas in data["classification"]:
    print("Class:" + clas + ":" + str(data["classification"][clas]["score"]))
    print "Keywords"
    for key in data["classification"][clas]["keywords"]:
        print key + ":" + str(data["classification"][clas]["keywords"][key])