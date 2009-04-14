import random
import elementtree.ElementTree as ET
t = ET.Element("costs")
x = (0, 888.47, 10)
y = (0, 812.81, 10)
ET.SubElement(t, "x", {"min":str(x[0]), "max":str(x[1]), "delta":str(x[2])})
ET.SubElement(t, "y", {"min":str(y[0]), "max":str(y[1]), "delta":str(y[2])})
m = ET.SubElement(t, "matrix")
for y in xrange(y[0], int(y[1]/y[2])):
    ET.SubElement(t, "row", text = " ".join([str(random.randint(10,100)) for n in xrange(x[0], int(x[1]/x[2]))]))
ET.ElementTree(t).write("rand.cost.xml")