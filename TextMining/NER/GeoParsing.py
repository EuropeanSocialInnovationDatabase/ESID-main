from mordecai import Geoparser
from geopy.geocoders import Nominatim
#import pyap
geo = Geoparser()
#naa = geo.geoparse("I traveled from Oxford to Ottawa.")
#print(naa)
baa = geo.geoparse("My address is Pedje Milosavljevica 74, Belgrade, Serbia")
print(baa)
#geolocator = Nominatim()
#location = geolocator.geocode("Pedje Milosavljevica 74, Belgrade, Serbia")
#print(location.address)

#test_address = """
#    Lorem ipsum 225 E. John Carpenter Freeway, Suite 1500 Irving, Texas 75062 Dorem sit amet
#    """
#addresses = pyap.parse(test_address, country='US')
#for address in addresses:
#    print(address)
    # shows address parts
#    print(address.as_dict())