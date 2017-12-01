import requests
import json
r = requests.post("http://services.gate.ac.uk/knowmak/classifier/project", data="""
<p><strong>Grow and Protect Your Business with the Right Technology Support</strong></p>
<p>Many small to medium sized businesses within the UK have enough on their plate trying to provide quality products and services. Unfortunately, the technical aspect of running a business can prove to be very frustrating. Often times, the amount of time it takes to handle these technical services can take away from efforts made to offer consumers the best services and product possible. Fortunately a service like <a href="http://www.office-tek.co.uk/">Office Tek</a> can help remove some of the burden of the technical aspects off of the shoulders of a business that has better things to do.</p>
<p>The first thing to understand about this type of service is the comprehensive nature of what is provided. For example, every business is going to have some type of IT requirement. It doesn't matter what the business does, they will need some type of technical infrastructure, and this particular service offers comprehensive IT solutions for businesses of all sizes.</p>
<p><strong>Managing VoIP</strong></p>
<p>Managing costs for a small to medium-size business is crucial, and a way that business can offset higher costs, while still receiving quality services, is through VoIP phone systems. These phone systems use Internet connections to communicate rather than standard phone lines. However, this can be somewhat technical and may be beyond the ability for the business owner, or the office staff, to properly handle. It's in these cases that a technical vendor can help.</p>
<p><img src="https://s4.postimg.org/e1ire8yn1/0_2.jpg" alt="" width="400" height="300" /></p>
<p><strong>System Security</strong></p>
<p>Lastly, protecting a businesses security is essential, especially with how dangerous of a place the Internet can be when for companies that do any business online. Hackers are getting more creative and aggressive when it comes to stealing client and business data for their own use. Having a service that can constantly monitor the security of a business computer or server, and fend off attacks, is something that a business can have with <a href="http://www.office-tek.co.uk/services-solutions/managed-it-support/">Proactive technology support by Office Tek</a>.</p>
<p>Listing all the services that this particular company provides would be impossible in such a limited article. Suffice to say that if it has anything to do with technology, this technology vendor can handle every aspect of your business. Whether it's IT support, phone communications, Internet security, data backup services or <a href="https://en.wikipedia.org/wiki/Cloud_computing">cloud computing</a>, if technical help is what your business needs, this is the service that can provide it.</p>
""")
print(r.status_code, r.reason)
print(r.text)
data = json.loads(r.text)
for clas in data["classification"]:

    print "Class:" + clas + ":"+ str(data["classification"][clas]["score"])
    print "Keywords"
    for key in data["classification"][clas]["keywords"]:
        print key+ ":" + str(data["classification"][clas]["keywords"][key])
