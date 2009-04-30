import unittest
import tests.emoeaTests as emoea
import tests.costTests as cost
import mapping.network_mapping as nm
import elementtree. ElementTree as ET
#import tests.testInterface as interface
if __name__ == "__main__":
    #interface.main()
    #unittest.main(emoea)
    #unittest.main(cost)
    r = nm.Routes("data/rand.rou.xml")
    g = nm.Graph("data/rand.nod.xml", "data/rand.edg.xml", "data/rand.flo.xml")
    g.load()
    g.trim(r, (0.0, 470.0), (602.0, 0.0))
    g.writexml()