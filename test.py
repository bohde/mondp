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
    r = nm.Routes("data/tapas/routes6-8.rou.xml")
    g = nm.Graph("data/tapas/cologne.nod.xml", "data/tapas/cologne.edg.xml", "data/rand/rand.flo.xml")
    g.load()
    g.trim(r, (8333, 14749), (11327, 18467))
    g.writexml()