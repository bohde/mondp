#!/usr/bin/python
from main.epsilonMOEA import epsilonMOEA
from main.network_mapping import Graph

def main():
    g = Graph('data/rand.nod.xml', 'data/rand.edg.xml', 'data/rand.flo.xml')
    g.load()
    e = epsilonMOEA()
    e.setGenome(g)
    e.setNumberofEvals(10000)
    e.initPop(10)
    e.runEvals()


if __name__=="__main__":
    main()