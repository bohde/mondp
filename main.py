#!/usr/bin/python
from main.epsilonMOEA import epsilonMOEA
from main.network_mapping import Graph

def main():
    f = open("out", 'w')
    for i in range(10):
        f.write("Run %s\n" %i)
        g = Graph('data/rand.nod.xml', 'data/rand.edg.xml', 'data/rand.flo.xml')
        g.load()
        e = epsilonMOEA()
        e.setGenome(g)
        e.setNumberofEvals(5000)
        e.initPop(50)
        f.write(e.runEvals(30))
        f.write("\n\n")
    f.close()


if __name__=="__main__":
    main()