#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
    This file is part of Evolutionary algorithm network design.

    Evolutionary algorithm network design is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    Evolutionary algorithm network design is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with Evolutionary algorithm network design.  If not, see <http://www.gnu.org/licenses/>.
"""

try:
    import xml.etree.cElementTree as ET
except:
    import elementtree.ElementTree as ET
import random
import time
import pipes
from interface import SUMOInterface
from main.epsilonMOEA import Individual
from threading import Thread
TEMP='/tmp/' + str(random.random()) + "/"
print TEMP

class Graph(Individual):
    def __init__(self, nodes_file=None, edges_file=None, flo_file=None):
        self.nodes = Nodes()
        self.edges = Edges(self.nodes)
        self.nodes_file = nodes_file
        self.edges_file = edges_file
        self.flo_file = flo_file
        self.mins = (-10000, -10000)
        self.eps = (.1, .1)
        Individual.__init__(self)

    def load(self):
        self.nodes = Nodes(self.nodes_file)
        self.edges = Edges(self.nodes, self.edges_file)
        self.edges.load_protected_edges(self.flo_file)

    def copy(self):
        other = Graph()
        other.set_files(*self.get_files())
        other.nodes = self.nodes
        other.cost = self.cost
        other.edges = self.edges.copy()
        return other

    def get_files(self):
        return (self.nodes_file, self.edges_file, self.flo_file)

    def set_files(self, nodes_file, edges_file, flo_file):
        self.nodes_file, self.edges_file, self.flo_file = nodes_file, edges_file, flo_file

    def mate(self, other):
        child1 = Graph(*self.get_files())
        child2 = Graph(*self.get_files())
        child1.cost = self.cost
        child1.nodes = self.nodes
        child2.cost = self.cost
        child2.nodes = self.nodes
        child1.edges, child2.edges = self.edges.mate(other.edges)
        child1.alter_edges()
        child2.alter_edges()
        child1.evaluate()
        child2.evaluate()
        return child1, child2

    def contains_edge(self, edge):
        return self.edges.contains(*edge)

    def add_edge(self, edge, spread):
        self.edges.add(edge[0], edge[1], spread)

    def add_named_edge(self,key, edge):
        self.edges.add_edge(key, edge)

    def writexml(self, file):
        ET.ElementTree(self.nodes.toxml()).write(file + ".nod.xml")
        ET.ElementTree(self.edges.toxml()).write(file + ".edg.xml")

    def alter_edges(self):
        self.edges.alter(*self.nodes.get_random_pair())

    def evaluate(self):
        print "loL"
        s = SUMOInterface()
        s.breakdown()
        s.setNodes(self.nodes)
        s.makeNetwork(self.edges)
        if(s.makeRoutes(self.flo_file)):
            times = s.execute()
        else:
            print "Not enough routes!"
            times = [-10000, -10000]
        cost = self.cost.check_costs(self.edges.convert_modifiable()) + self.edges.total_costs()
        self.fitness = times + [-1*cost]
        print self.fitness
        s.breakdown()
        del s

    def random(self):
        o = self.copy()
        o.alter_edges()
        return o

    def trim(self,route, point1, point2):
        self.nodes.trim(point1, point2)
        self.edges.trim()
        route.trim(x.id for x in self.edges.edges.values())
        

class Nodes():
    def __init__(self, nodes=None):
        self.nodes = {}
        self.mapping = {} #Map new id's to old id's.
        self.n = 0
        if nodes:
            self.load(nodes)

    def load(self, nodes):
        nodes = ET.parse(nodes)
        for node in nodes.getroot().getchildren():
            d = node.attrib
            self.mapping[d["id"]] = d["id"]
            self.nodes[d["id"]] = (d["x"], d["y"])
            #self.n += 1

    def get_mapped_id(self, id):
        return id

    def get_random_pair(self):
        return random.sample(self.nodes.keys(), 2)

    def get_point(self, n):
        return [float(x) for x in self.nodes[n]]

    def toxml(self):
        xmlnodes = ET.Element("nodes")
        for k, node in self.nodes.items():
            xmlnodes.append(ET.Element("node", id=k, x=str(node[0]), y=str(node[1])))
        return xmlnodes

    def trim(self, point1, point2):
        print point1, point2
        print "deleting nodes"
        new_nodes = {}
        oob = (lambda c, x1, x2: (c > x1 and c > x2) or (c < x1 and c < x2))
        for k, v in self.nodes.iteritems():
            if not(any(map(lambda n: oob(float(v[n]), float(point1[n]), float(point2[n])), [0,1]))):
                new_nodes[k] = v
            else:
                print "node", k
        self.nodes = new_nodes
        print "done deleting"


def parametric(p,h):
    p = float(p)
    h = float(h)
    def closure(t):
        return (p-h) * t + h
    return closure

def distance(p1, p2):
    if not(p1):
        return 0
    return ((p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2) ** .5
    #return (sum(map(lambda l: reduce(lambda x, y: (x - y) ** 2, l), zip(p1, p2))) ** .5)

class Shape():
    delta = 1
    def __init__(self, fromnode, tonode, shape):
        self.shape = [fromnode] + shape + [tonode] #These are all tuples. (x,y)
        self.deltax = Shape.delta
        self.detaxy = Shape.delta

    def mutate(self):
        index = random.randint(0, len(self.shape) - 2)
        x = parametric(self.shape[index][0], self.shape[index + 1][0])
        y = parametric(self.shape[index][1], self.shape[index + 1][1])
        t = random.uniform(0, 1)
        self.shape = self.shape[index:] + list([(x(t) + random.gauss(0, self.deltax), y(t) + random.gauss(0, self.deltax))]) + self.shape[:index]
        ########
        # Let's maybe alter deltax and deltay

    def parsed(self):
        #print self.shape
        return ' '.join(["%f,%f" % c for c in self.shape[1:-1]])

    def parsedrev(self):
        return ' '.join(["%f,%f" % c for c in reverse(self.shape[1:-1])])



class Edge():
    shapeMut = .05
    priorityMut = .05
    priorityDelta = 1
    laneMut = .05
    laneDelta = 2
    spreadMut = .01
    costPerUnit = 200
    def __init__(self, id, fromnode, fromcoord, tonode, tocoord, spread=0, priority=0, nolanes=2, speed=None, shape=[], modifiable=True):
        self.spread = spread #0 for center, 1 for right, -1 for left (reversed edge)
        self.priority = priority
        self.nolanes = nolanes
        self.maxspeed = speed
        self.shape = Shape(fromcoord, tocoord, shape)
        self.id = id
        self.fromnode = fromnode
        self.tonode = tonode
        self.modifiable = modifiable

    def mutate(self):
        if modifiable and rand.uniform(0,1) < Edge.shapeMut:
            self.shape.mutate()
            self.setMaxSpeed()
        if rand.uniform(0,1) < Edge.priorityMut:
            self.priority += random.randint(-priorityDelta, priorityDelta)
            self.priority = max(0, self.priority)

        if modifiable and rand.uniform(0,1) < Edge.laneMut:
            self.nolanes += random.randint(-laneDelta, laneDelta)
            self.nolanes = max(0, self.nolanes)

        if modifiable and rand.uniform(0,1) < Edge.spreadMut:
            self.spread = random.randint(-1, 1)

    def setMaxSpeed(self):
        self.maxspeed = 13.9

    def toxml(self):
        if not(self.maxspeed):
            self.setMaxSpeed()
        attrib = {"priority":str(self.priority), "nolanes":str(self.nolanes), "speed":str(self.maxspeed), "id":self.id}
        attrib["spread"] = ("center", "right")[self.spread]
        if(self.spread == -1):
            attrib["tonode"] = str(self.fromnode)
            attrib["fromnode"] = str(self.tonode)
            sh = str(self.shape.parsedrev())
            if len(sh) > 0:
                attrib["shape"] = sh
        else:
            attrib["tonode"] = str(self.tonode)
            attrib["fromnode"] = str(self.fromnode)
            sh = str(self.shape.parsed())
            if len(sh) > 0:
                attrib["shape"] = sh
        return ET.Element("edge", attrib)

    def convert(self):
        return zip(self.shape.shape[1:], self.shape.shape[:-1])

    def length(self):
        #print self.shape.shape
        return sum(map(lambda l: distance(*l), self.convert()))

    def cost(self):
        return self.modifiable * self.length() * Edge.costPerUnit



class Edges():
    n = 0
    def __init__(self, nodes, edges=None):
        self.edges = {}
        self.nodes = nodes
        self.protected_edges = set()
        if edges:
            self.load(edges)

    def copy(self):
        other = Edges(self.nodes)
        other.edges = dict(self.edges)
        return other

    def load(self, edges):
        edges = ET.parse(edges)
        for edge in edges.getroot().getchildren():
            d = edge.attrib
            d["fromcoord"] = self.nodes.get_point(self.nodes.get_mapped_id(d["fromnode"]))
            d["tocoord"] = self.nodes.get_point(self.nodes.get_mapped_id(d["tonode"]))
            d["shape"] = list([tuple(float(x) for x in pair.split(",")) for pair in d["shape"].split(" ")])
            d["modifiable"] = False
            try:
                d["spread"] = 0 if d["spread"] == "center" else 1
            except:
                pass
            key = frozenset((d["fromnode"], d["tonode"]))
            self.add_edge(key, Edge(**d))
            #self.add_id(d["id"], self.nodes.get_mapped_id(d["fromnode"]), self.nodes.get_mapped_id(d["tonode"]))

    def load_protected_edges(self, flow):
        flows = ET.parse(flow)
        for flow in flows.getroot().getchildren():
            self.protected_edges.update((flow.attrib["begin"], flow.attrib["end"]))

    def add_edge(self, key, edge):
        self.edges[key] = edge

    def add_id(self, id, n1, n2):
        key = frozenset((n1, n2))
        if id not in [edge.id for edge in self.edges.values()]:
            self.edges[key] = Edge(id, n1, self.nodes.get_point(n1), n2, self.nodes.get_point(n2))

    def add(self, n1, n2):
        self.add_id("s" + str(Edges.n), n1, n2)
        Edges.n += 1

    def lookup(self, n1, n2):
        key = frozenset((n1, n2))
        return (self.edges[key])[1]

    def get_edges(self):
        return [x for x in self.edges.keys()]

    def alter(self, n1, n2):
        """
        remove the edge is it is found, otherwise make a new one.
        """
        if self.contains(n1, n2):
            del self.edges[frozenset((n1, n2))]
        else:
            self.add(n1, n2)

    def mate(self, other):
        child1 = Edges(self.nodes)
        child2 = Edges(self.nodes)
        child1.protected_edges = self.protected_edges
        child2.protected_edges = self.protected_edges
        for edge in self.edges.keys():
            if edge in other.edges:
                child1.edges[edge] = self.edges[edge]
                child2.edges[edge] = self.edges[edge]
            else:
                random.choice((child1, child2)).edges[edge] = self.edges[edge]
        for edge in other.edges.keys():
            if not(edge in self.edges):
                random.choice((child1, child2)).edges[edge] = other.edges[edge]
        return child1, child2

    def protected(self, n1, n2):
        return self.edges[frozenset((n1, n2))][0] in self.protected_edges

    def contains(self, n1, n2):
        return frozenset((n1, n2)) in self.edges

    def convert(self):
        return reduce(lambda x, y: x + y, [edge.convert() for edge in self.edges.values()])

    def convert_modifiable(self):
        return reduce(lambda x, y: x + y, [edge.convert() for edge in self.edges.values() if edge.modifiable == True], [])

    def toxml(self):
        xmledges = ET.Element("edges")
        for k, edge in self.edges.items():
            k = tuple(k)
            xmledges.append(edge.toxml())
        return xmledges

    def trim(self):
        print "dropping edges"
        new_edges = {}
        for edge, v in self.edges.iteritems():
            e = edge
            edge = list(edge)
            if not(edge[0] in self.nodes.nodes.keys()) or not(edge[1] in self.nodes.nodes.keys()):
                print "edge", edge, self.edges[e]
            else:
                new_edges[e] = v
        self.edges = new_edges
        print "done deleting"

    def total_costs(self):
        return sum([edge.cost() for edge in self.edges.values()])
        

class Route():
    def __init__(self, id, depart, edges):
        self.id = id
        self.depart = depart
        self.edges = edges
        #print id, depart, edges

    def adjust(self, edges):
        
        def mid(acc, test):
            if test == []:
                return acc
            t = test[0].split("#")[0]
            if t in edges:
                return mid(acc + [t], test[1:])
            else:
                return acc

        def begin(test):
            if test == []:
                return []
            t = test[0].split("#")[0]
            if t in edges:
                return mid([], test[1:])
            else:
                return begin(test[1:])
        #print self.edges,
        self.edges = ' '.join(begin(self.edges.split()))
        return len(self.edges) > 0

    def toxml(self):
        route = ET.Element("vehicle", id=self.id, depart=self.depart)
        edges = ET.SubElement(route, "route", edges=self.edges)
        return route

class Routes():
    def __init__(self, rou_file=None):
        self.rou_file = rou_file
        if(self.rou_file):
            self.load()

    def load(self):
        routes = ET.parse(self.rou_file)
        self.routes = []
        for route in routes.getroot().getchildren():
            d = route.attrib
            c = route.getchildren()[0]
            if int(d["depart"]) < 25200:
                self.routes.append(Route(d["id"], d["depart"], c.text))

    def toxml(self):
        routes = ET.Element("routes")
        for r in self.routes:
            routes.append(r.toxml())
        return routes

    def trim(self, edges):
        print len(self.routes)
        new_routes = []
        e = list(edges)
        for route in self.routes:
            if  route.adjust(e):
                new_routes.append(route)
        self.routes = new_routes
        print len(self.routes)

    def writexml(self, file):
        ET.ElementTree(self.toxml()).write(file)