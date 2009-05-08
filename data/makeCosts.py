import random
import elementtree.ElementTree as ET
t = ET.Element("costs")
x = (18641.0, 19535.0, 50)
y = (33850.0, 35412.0, 50)
ET.SubElement(t, "x", {"min":str(x[0]), "max":str(x[1]), "delta":str(x[2])})
ET.SubElement(t, "y", {"min":str(y[0]), "max":str(y[1]), "delta":str(y[2])})
m = ET.SubElement(t, "matrix")
for y in xrange(y[0], int(y[1]/y[2])):
    ET.SubElement(t, "row", text = " ".join([str(random.randint(10,100)) for n in xrange(x[0], int(x[1]/x[2]))]))
ET.ElementTree(t).write("rand.cost.xml")
