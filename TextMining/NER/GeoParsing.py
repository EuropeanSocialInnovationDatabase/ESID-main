from mordecai import Geoparser
geo = Geoparser()
naa = geo.geoparse("I traveled from Oxford to Ottawa.")
print(naa)
baa = geo.geoparse("My address is Pedje Milosavljevica 74, Belgrade, Serbia")
print(baa)