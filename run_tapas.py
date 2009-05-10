#!/usr/bin/python
from main.epsilonMOEA import epsilonMOEA
from mapping.network_mapping import Graph
from mapping.interface import SUMOInterface
from main.costChecker import costChecker
from multiprocessing import Process
import random

def main():
    #f = open("tapas_out", 'w')
    c = costChecker.processCostFile('data/tapas_small/cologne.cost.xml')
    g = Graph('data/tapas_small/cologne.nod.xml', 'data/tapas_small/cologne.edg.xml', 'data/tapas_small/6-8.flo.xml')
    g.cost = c
    g.load()
    g.evaluate()
    print len(g.nodes.nodes.values())
    random.seed(42)
    SUMOInterface.begin = 21600
    SUMOInterface.end = 28800
    for j in xrange(5):
        ps = [Process(target=run_eval, args=("tapas_out", g, i, random.random())) for i in range(j, j+2)]
        for p in ps:
            p.start()
        for p in ps:
            p.join()

def run_eval(filename, g, i, rand):
    random.seed(rand)
    f = open(filename + str(i), 'w')
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