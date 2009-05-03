from mapping.network_mapping import *
import elementtree.ElementTree as ET

attrib = {"id":"1", "tonode":"Blah", "tocoord":(0,0), "fromnode":"Blah2",  "fromcoord":(1,1)}
e = Edge(**attrib)
#e.shape.mutate()
#e.shape.mutate()
print ET.tostring(e.toxml())
