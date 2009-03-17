import unittest
from main import epsilonMOEA as eMOEA

class TestIndividualDomination(unittest.TestCase):
    def setUp(self):
        self.one = eMOEA.Individual()
        self.two = eMOEA.Individual()
        self.two.dominated = False
        self.one.dominated = False

    def testdominates(self):
        self.one.fitness = (1, 0)
        self.two.fitness = (0, 0)
        self.assertEqual(self.one.dominates(self.two), 1)
        self.assertEqual(self.one.dominated, False)
        self.assertEqual(self.two.dominated, True)

    def testdominated(self):
        self.one.fitness = (0, 0)
        self.two.fitness = (0, 1)
        self.assertEqual(self.one.dominates(self.two), -1)
        self.assertEqual(self.one.dominated, True)
        self.assertEqual(self.two.dominated, False)

    def testnondominated(self):
        self.one.fitness = (0, 0)
        self.two.fitness = (0, 0)
        self.assertEqual(self.one.dominates(self.two), 0)
        self.assertEqual(self.one.dominated, False)
        self.assertEqual(self.two.dominated, False)

    def testnondominated(self):
        self.one.fitness = (1, 0)
        self.two.fitness = (0, 1)
        self.assertEqual(self.one.dominates(self.two), 0)
        self.assertEqual(self.one.dominated, False)
        self.assertEqual(self.two.dominated, False)

def fitness_generator(n):
    if n == 0:
        yield []
        return
    for el in fitness_generator(n-1):
        for l in [0, 1]:
            yield el + [l]

def testIndWrapper(n):
    class testIndiv(eMOEA.Individual):
        fg = fitness_generator(n)

        def __init__(self):
            eMOEA.Individual.__init__(self)
            self.mins = [0] * n
            self.eps = [.1] * n

        @staticmethod
        def random():
            ind = testIndiv()
            ind.fitness = testIndiv.fg.next()
            return ind
    return testIndiv

class TestPopulation(unittest.TestCase):
    def setUp(self):
        self.genome = testIndWrapper(2)
        self.pop = eMOEA.Population(3, self.genome)
        self.pop.initialize()

class TestPopulationSelect(TestPopulation):
    def testdominated(self):
        pop = self.pop
        self.assertEquals(pop._pop_select(1,0,0), pop.inds[1])

    def testundom(self):
        pop = self.pop
        self.assertEquals(pop._pop_select(1,2,1), pop.inds[2])

class TestPopulationArchive(TestPopulation):
    def testarchive(self):
        self.pop.split_population()
        self.assertEquals([tuple(x.fitness) for x in self.pop.archive_population()], [(0,1), (1,0)])

class TestPopulationAcceptance(TestPopulation):
    def setUp(self):
        TestPopulation.setUp(self)
        self.testInd = self.genome()

    def testdominates(self):
        self.testInd.fitness = (1,1)
        self.assertEquals(self.pop.pop_acceptance(self.testInd), True)

    def testnondominates(self):
        self.testInd.fitness = (0,0)
        self.assertEquals(self.pop.pop_acceptance(self.testInd), False)

class TestPopulationArchiveAcceptance(TestPopulation):
    def setUp(self):
        TestPopulation.setUp(self)
        self.pop.split_population()
        self.testInd = self.genome()

    def testnondominating(self):
        self.testInd.fitness = (0, 0)
        self.assertEquals(self.pop.archive_acceptance(self.testInd), False)
        self.assertEquals(self.testInd in self.pop.archive, False)

    def testdominating(self):
        self.testInd.fitness = (2,2)
        self.assertEquals(self.pop.archive_acceptance(self.testInd), True)
        self.assertEquals(self.testInd in self.pop.archive, True)

    def testepsdominating(self):
        self.testInd.fitness = (1.02, 0)
        self.assertEquals(self.pop.archive_acceptance(self.testInd), True)
        self.assertEquals(self.testInd in self.pop.archive, True)

    def testepsnondominating(self):
        self.testInd.fitness = (.98, 0)
        self.assertEquals(self.pop.archive_acceptance(self.testInd), False)
        self.assertEquals(self.testInd in self.pop.archive, False)

    def test_euclid_fail(self):
        p = self.pop.archive[-1]
        p.fitness = (.99, .1)
        p.gen_ident()
        o = self.testInd
        o.fitness = (.98, .1)
        o.gen_ident()
        self.assertEquals(eMOEA.euclid_dist(o.ident_array, o.fitness) > eMOEA.euclid_dist(p.ident_array, p.fitness), True)
        self.assertEquals(self.pop.archive_acceptance(o), False)
        self.assertEquals(o in self.pop.archive, False)

    def test_euclid_pass(self):
        p = self.pop.archive[-1]
        p.fitness = (.95, .1)
        p.gen_ident()
        o = self.testInd
        o.fitness = (.98, .1)
        o.gen_ident()
        self.assertEquals(eMOEA.euclid_dist(o.ident_array, o.fitness) > eMOEA.euclid_dist(p.ident_array, p.fitness), False)
        self.assertEquals(self.pop.archive_acceptance(o), True)
        self.assertEquals(o in self.pop.archive, True)

    def test_new_hyper_cube(self):
        o = self.testInd
        o.fitness = (.8, .1)
        o.gen_ident()
        [x.gen_ident() for x in self.pop.archive]
        self.assertEquals(o.ident_array in [x.ident_array for x in self.pop.archive], False)
        self.assertEquals(self.pop.archive_acceptance(o), True)
        self.assertEquals(o in self.pop.archive, True)


class TestIndividualIdentArray(unittest.TestCase):
    def setUp(self):
        self.genome = testIndWrapper(2)
        self.ind = self.genome()

    def testIdentArray(self):
        self.ind.fitness = (1, 0)
        self.ind.gen_ident()
        self.assertEquals(self.ind.ident_array, (10 ,0))

class TestEuclid(unittest.TestCase):
    def test(self):
        self.assertEquals(eMOEA.euclid_dist((0, 1), (1, 0)), 2)

    def test2(self):
        self.assertEquals(eMOEA.euclid_dist((2, 2), (0, 0)), 4)

def test():
    unittest.main()