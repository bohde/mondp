import unittest
from main.costChecker import *

class testMatrixOperations(unittest.TestCase):
    def setUp(self):
        self.n = [[0,1], [2,3]]

    def testMult(self):
        self.assertEquals(costChecker.multMatrices(self.n, self.n), [[0,1], [4,9]])

    def testAdd(self):
        self.assertEquals(costChecker.addMatrices(self.n, self.n), [[0, 2], [4, 6]])

    def testOr(self):
        self.assertEquals(costChecker.orMatrices(self.n, self.n), [[0, 1], [1,1]])


class testCostCheck(unittest.TestCase):
    def setUp(self):
        self.check = costChecker((0,50,25),(0,50,25), ((5,10),(15,3)))

    def testDims(self):
        self.assertEquals(len(self.check.costs), 2)
        self.assertEquals(sum(map(len, self.check.costs)), 4)

    def testQuadrants(self):
        edges = [((x,y), (x + 1,y + 1),)  for x in (0,25) for y in (0,25)]
        print edges
        answers = [[[1,0],[0,0]], [[0,0],[1,0]],[[0,1],[0,0]],[[0,0],[0,1]]]
        for edge, answer in zip(edges, answers):
            self.assertEquals(self.check.check_intersect(*edge), answer)

    def testOneMultiple(self):
        edges = ((0,0), (10,40))
        self.assertEquals(self.check.check_intersect(*edges), [[1,0],[1,0]])

    def testOneIntersectPoint(self):
        point = (0,0)
        self.assertEquals(self.check.check_intersect(point, point), [[0,0],[0,0]])

    def testOneIntersects(self):
        edges = ((0,0), (1,1)),
        self.assertEquals(self.check.check_intersects(edges), [[1,0],[0,0]])
        self.assertEquals(self.check.check_costs(edges), 5)

    def testTwoOverlappingIntersects(self):
        edges = [[(0,0), (1,1)]]*2
        self.assertEquals(self.check.check_intersects(edges), [[1,0],[0,0]])
        self.assertEquals(self.check.check_costs(edges), 5)

    def testTwoDifferentIntersects(self):
        edges = [[(0,0), (1,1)],[(0,26), (0,49)]]
        self.assertEquals(self.check.check_intersects(edges), [[1,0],[1,0]])
        self.assertEquals(self.check.check_costs(edges), 20)

def test():
    unittest.main()
