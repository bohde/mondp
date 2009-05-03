#!/usr/bin/python
import math
import operator
import elementtree.ElementTree as ET

def parametric(p,h):
    def closure(t):
        return (p-h) * t + h
    return closure

def rev_parametric(p, h):
    if p == h:
        return lambda x: 2.0
    def closure(x):
        #print h, p
        return (float(x)-h)/(p-h)
    return closure


product = lambda f: reduce(operator.mul, f)

class costChecker():
    intersectCost = 500
    def __init__(self, x, y, costs):
        self.x = x #3tuple, x min, max, delta
        self.y = y #3tuple, y min, max, delta
        self.costs = costs
        self.zero = [[0]*(int(math.ceil(abs(x[1] - x[0])/ x[2])))]*int(math.ceil(abs(y[1] - y[0])/ y[2]))

    def copy_zero(self):
        return list(map(list, self.zero))

    def copy(self):
        return costChecker(self.x, self.y, self.costs)

    def check_costs(self, edges):
        """
        edges is a tuple of points
        make a binary matrix corresponding to the graph
        for each edge mark the intersected grids.
        """
        s = self.check_intersects(edges)
        #print s
        return sum(map(sum, costChecker.costMatrices(s, self.costs)))


    def check_intersects(self, edges):
        return reduce(costChecker.addMatrices, [self.check_intersect(*edge) for edge in edges], self.copy_zero())

    def check_intersect(self, edge1, edge2):
        t = 0.0
        matrix = self.copy_zero()
        if edge1 == edge2:
            return self.zero
        xmask, ymask = map(lambda n: -1 if edge1[n] > edge2[n] else 1, [0,1])
        #print "xm=", xmask, " ym=", ymask
        xf, yf = map(lambda n: parametric(edge1[n], edge2[n]), [0,1])
        xtf, ytf = map(lambda n: rev_parametric(edge2[n], edge1[n]), [0,1])
        j = int(edge1[0]/self.x[2])
        k = int(edge1[1]/self.y[2])
        while t < 1:
            #print "j=", j, " k=", k
            if j < 0 or j >= len(matrix) or k < 0 or k >= len(matrix[j]):
                    return self.zero
            matrix[k][j] = 1
            tx = xtf((j + xmask) * self.x[2])
            #print (j + xmask) * self.x[2]
            ty = ytf((k + ymask) * self.y[2])
            #print (k + ymask) * self.y[2]
            #print "tx=", tx, " ty=", ty
            if tx < ty:
                t = tx
                j += xmask
            else:
                t = ty
                k += ymask
            ##print "t=", t
        return matrix

    @staticmethod
    def processCostFile(f):
        e = ET.ElementTree(file=f).getroot()
        d = e.find("x").attrib
        x = (float(d["min"]), float(d["max"]), float(d["delta"]))
        d = e.find("y").attrib
        y = (float(d["min"]), float(d["max"]), float(d["delta"]))
        g = [[int(i) for i in r.attrib["text"].split()] for r in e.findall("row")]
        return costChecker(x, y, g)


    fMatrices = lambda f: lambda n, m: map(lambda l: map(f, zip(*l)), zip(n, m))
    dMatrices = lambda f: lambda n, m: map(lambda l: map(f, *zip(*l)), zip(n, m))
    costMatrices = staticmethod(fMatrices(lambda m: (lambda x, y: (x > 0) * y + (x > 1) * costChecker.intersectCost)(*m)))
    multMatrices = staticmethod(fMatrices(product))
    addMatrices = staticmethod(fMatrices(sum))
    orMatrices = staticmethod(fMatrices(any))