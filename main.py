#!/usr/bin/python
from main.epsilonMOEA import epsilonMOEA
from mapping.network_mapping import Graph, Edge
from main.costChecker import costChecker

def main():
    f = open("disc", 'w')
    c = costChecker.processCostFile('data/rand/rand.cost.xml')
    for i in range(30):
        Edge.shapeMut = .00
        Edge.priorityMut = .0
        Edge.priorityDelta = 1
        Edge.laneMut = .00
        Edge.laneDelta = 2
        Edge.spreadMut = .00
        Edge.costPerUnit = 200
        f.write("Run %s\n" %i)
        g = Graph('data/rand/rand.nod.xml', 'data/rand/rand.edg.xml', 'data/rand/rand.flo.xml')
        g.cost = c
        g.load()
        print g.evaluate()
        e = epsilonMOEA()
        e.setGenome(g)
        e.setNumberofEvals(1000)
        e.initPop(50)
        f.write(e.runEvals())
        f.write("\n\n")
    f.close()


if __name__=="__main__":
    main()
