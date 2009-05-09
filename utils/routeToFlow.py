#!/usr/bin/python
"""
Converts a route to flow defs
"""
import sys
try:
    import xml.etree.ElementTree as ET
except:
    import elementtree.ElementTree as ET
import random
begin = str(21600)
end = str(28800)


def process_routes(xmlroutes):
    root = ET.Element("flowdefs")
    for v in xmlroutes.findall("vehicle"):
        ET.SubElement(root, "flow", attrib=process_vehicle(v))
    return ET.ElementTree(root)

def process_vehicle(v):
    d = process_route(v.find("route"))
    d.update({"id":v.attrib["id"], "begin":begin, "end":end, "no":'1'})
    return d

def process_route(r):
    try:
        e = r.text.split()
    except:
        e = r.attrib["edges"].split()
    return {"from":e[0], "to":e[-1]}

if __name__=="__main__":
    if len(sys.argv) == 3:
        f = sys.argv[1]
        o = sys.argv[2]
    else:
        f = "/home/numix/school/ea/cs448/data/rand/rand.rou.xml"
        o = "/home/numix/school/ea/cs448/data/rand/rand.flo.xml"
    process_routes(ET.ElementTree(file=f)).write(o)