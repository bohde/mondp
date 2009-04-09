from main.interface import SUMOInterface
import elementtree.ElementTree as ET
import main.network_mapping as nm

def main():
    s = SUMOInterface()
    s.breakdown()
    s.setNodes(nm.Nodes('data/rand.nod.xml'))
    s.makeNetwork(nm.Edges(s.nodes, 'data/rand.edg.xml'))
    s.makeRoutes('data/rand.flo.xml')
    tree = s.execute()
    last_el = tree.getroot()[-1].attrib
    print float(last_el["meanTravelTime"]), float(last_el["meanWaitingTime"])
    s.breakdown()
