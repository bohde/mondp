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

import elementtree.ElementTree as ET
import random
import time
import pipes
from interface import SUMOInterface
from epsilonMOEA import Individual
random.seed(42)
TEMP='/tmp/'

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
        other.edges = self.edges.copy()
        return other

    def get_files(self):
        return (self.nodes_file, self.edges_file, self.flo_file)

    def set_files(self, nodes_file, edges_file, flo_file):
        self.nodes_file, self.edges_file, self.flo_file = nodes_file, edges_file, flo_file

    def mate(self, other):
        child1 = Graph(*self.get_files())
        child2 = Graph(*self.get_files())
        child1.nodes = self.nodes
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

    def writexml(self):
        ET.ElementTree(self.nodes.toxml()).write(self.nodes_file + "." + str(self.id))
        ET.ElementTree(self.edges.toxml()).write(self.edges_file + "." + str(self.id))

    def alter_edges(self):
        self.edges.alter(*self.nodes.get_random_pair())

    def evaluate(self):
        s = SUMOInterface()
        s.breakdown()
        s.setNodes(self.nodes)
        s.makeNetwork(self.edges)
        s.makeRoutes(self.flo_file)
        tree = s.execute()
        last_el = tree.getroot()[-1].attrib
        self.fitness = [-1 * float(last_el["meanTravelTime"]), -1 * float(last_el["meanWaitingTime"])]
        for i,x in enumerate(self.fitness):
            if x >0:
                self.fitness[i] = -10000
        print self.fitness
        s.breakdown()
        del s

    def random(self):
        o = self.copy()
        o.alter_edges()
        return o

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
            self.mapping[d["id"]] = str(self.n)
            self.nodes[str(self.n)] = (d["x"], d["y"])
            self.n += 1

    def get_mapped_id(self, id):
        return self.mapping[id]

    def get_random_pair(self):
        return random.sample(self.nodes.keys(), 2)

    def toxml(self):
        xmlnodes = ET.Element("nodes")
        for k, node in self.nodes.items():
            xmlnodes.append(ET.Element("node", id=k, x=str(node[0]), y=str(node[1])))
        return xmlnodes

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
            self.add_id(d["id"], self.nodes.get_mapped_id(d["fromnode"]), self.nodes.get_mapped_id(d["tonode"]))

    def load_protected_edges(self, flow):
        flows = ET.parse(flow)
        for flow in flows.getroot().getchildren():
            self.protected_edges.update((flow.attrib["begin"], flow.attrib["end"]))

    def add_edge(self, key, edge):
        self.edges[key] = edge

    def add_id(self, id, n1, n2, spread="Center"):
        key = frozenset((n1, n2))
        if id not in [edge[0] for edge in self.edges.values()]:
            self.edges[key] = (str(id), spread)

    def add(self, n1, n2, spread="Center"):
        self.add_id("s" + str(Edges.n), n1, n2, spread)
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
            self.add(n1, n2, "center")

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

    def toxml(self):
        xmledges = ET.Element("edges")
        for k, edge in self.edges.items():
            k = tuple(k)
            xmledges.append(ET.Element("edge", id=edge[0], fromnode=k[0], tonode=k[1], spread_type=edge[1]))
        return xmledges
