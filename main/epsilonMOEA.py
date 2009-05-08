import random
import math
import os

def euclid_dist(a, b):
    return sum(abs(n-m) for n,m in zip(a,b))

class Population():
    def __init__(self, popsize, genome):
        self.popsize = popsize
        self.genome = genome
        self.archive = None

    def initialize(self):
        self.inds = [self.genome.random() for n in xrange(self.popsize)]

    def pop_select(self):
        return self._pop_select(random.randint(0, len(self.inds) - 1), random.randint(0, len(self.inds) - 1), random.randint(0,1))

    def _pop_select(self, a, b, c):
        one, two = self.inds[a], self.inds[b]
        dom = one.dominates(two)
        return ((one, two)[c], one, two)[dom]

    def split_population(self):
        self.archive = []
        for x in self.inds:
            if x.dominated:
                continue
            for y in self.inds + self.archive:
                if x.dominates(y) == -1:
                    break
            if not(x.dominated):
                self.archive.append(x)
        for x in self.archive:
            self.inds.remove(x)

    def acceptance_wrapper(p):
        def acceptance(self, ind):
            dom = []
            for x in ((self.inds, self.archive)[p]):
                check = (ind.dominates, ind.ident_dominates)[p](x)
                if  check == -1:
                    return False
                if check == 1:
                    dom.append(x)
            if len(dom) == 0:
                    if p == 0:
                        pop = random.choice(self.inds)
                    else:
                        pop = None
                        for x in self.archive:
                            if ind.ident_array == x.ident_array:
                                indom = ind.dominates(x)
                                if indom == 1 or (indom == 0 and (euclid_dist(ind.fitness, ind.ident_array) < euclid_dist(x.fitness, x.ident_array))):
                                    pop = x
                                    break
                                if indom == 0 or indom == -1:
                                    return False
            else:
                    pop = random.choice(dom)
            if pop:
                (self.inds, self.archive)[p].remove(pop)
            (self.inds, self.archive)[p].append(ind)
            return True
        return acceptance

    pop_acceptance = acceptance_wrapper(0)

    def archive_population(self):
        return self.archive

    def archive_select(self):
        return random.choice(self.archive)

    archive_acceptance = acceptance_wrapper(1)

    def evaluation(self):
        for ind in self.archive_select().mate(self.pop_select()):
            if(not(self.archive_acceptance(ind))):
                self.pop_acceptance(ind)

    def clear(self):
        pass

class Individual():
    """
    A stub genome representation
    """
    genome = None

    def __init__(self):
        """
        The fitness values, which is an n-tuple
        """
        self.fitness = None
        self.dominated = False
        self.ident_array = None

    def evaluate(self):
        """
        subclass this. 
        """
        pass

    def random(self):
        """
        subclass this
        """
        pass

    def mate(self, other):
        """
        subclass this
        """
        pass

    def __dom_wrapper(pop):
        def dominates(self, other):
            if not((self.fitness, self.ident_array)[pop]):
                (self.evaluate, self.gen_ident)[pop]()

            if not((other.fitness, other.ident_array)[pop]):
                (other.evaluate, other.gen_ident)[pop]()

            other_partial = False
            self_partial = False

            for j, k in zip((self.fitness, self.ident_array)[pop], (other.fitness, other.ident_array)[pop]):
                if j > k:
                    self_partial = True
                if k > j:
                    other_partial = True
                if other_partial and self_partial:
                    return 0
            ret = self_partial - other_partial
            if ret == -1:
                self.dominated = True
            if ret == 1:
                other.dominated = True
            return ret
        return dominates

    dominates = __dom_wrapper(0)
    ident_dominates = __dom_wrapper(1)

    def gen_ident(self):
        self.ident_array = tuple(math.ceil((fit - minval)/float(ep)) for fit, minval, ep in zip(self.fitness, self.mins, self.eps))

    def set_eps(eps):
        self.eps = eps

    def set_mins(mins):
        self.mins = mins


class epsilonMOEA():
    def __init__(self):
        pass

    def setGenome(self, genome):
        self.genome = genome

    def setNumberofEvals(self, evals):
        self.evals = evals

    def initPop(self, popsize):
        """
        Step 1 Randomly initialize a population P (0). The
            non-dominated solutions of P (0) are copied to
            an archive population E(0). Set the iteration
            counter t = 0.
        """
        if not(self.genome):
            print "Genome not set!"
            os.exit(1)
        self.popsize = popsize
        self.population = Population(popsize, self.genome)
        self.population.initialize()
        self.population.split_population()


    def runEvals(self):
        for i in xrange(self.popsize, self.evals,  2):
            self.population.evaluation()
        #print len(set([x.fitness for x in self.population.archive]))
        return '\n'.join([str(x.fitness) for x in self.population.archive])
        
 
    """
    Step 2 One solution p is chosen from the population
        P (t) using the pop selection procedure.
    """
    """
    Step 3 One solution e is chosen from the archive
        population A(t) using an archive selection
        procedure.
    """

    """
    Step 4 One offspring solutions c is created using p
        and e.
    """

    """
    Step 5 Solution c is included in P (t) using a
        pop acceptance procedure.
    """
    """
    Step 6 Solution c is included in A(t) using a
        archive acceptance procedure.
    """

    """
    Step 7 If termination criterion is not satisfied,
        set t = t + 1 and go to Step 2, else report A(t).
    """