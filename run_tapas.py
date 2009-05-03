#!/usr/bin/python
from main.epsilonMOEA import epsilonMOEA
from mapping.network_mapping import Graph
from main.costChecker import costChecker

def main():
    f = open("out", 'w')
    c = costChecker.processCostFile('data/tapas/cologne.cost.xml')
    g = Graph('data/tapas/cologne.nod.xml.lol', 'data/tapas/cologne.edg.xml.lol', 'data/tapas/6-8.flo.xml')
    g.cost = c
    f.write(g.evaluate())
    g.load()
    for i in range(30):
        f.write("Run %s\n" %i)
        e = epsilonMOEA()
        e.setGenome(g)
        e.setNumberofEvals(1000)
        e.initPop(50)
        f.write(e.runEvals())
        f.write("\n\n")
    f.close()


if __name__=="__main__":
    main()