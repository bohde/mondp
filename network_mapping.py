#!/usr/bin/python
# -*- coding: utf-8 -*-

import elementtree.ElementTree as ET
import random
random.seed(42)

class Graph():
    def __init__(self, append, nodes_file, edges_file):
        self.nodes_file = nodes_file
        #print ET.tostring(self.nodes.toxml())
        self.edges_file = edges_file
        #print ET.tostring(self.edges.toxml())
        self.append = append
        self.edges.alter(*self.nodes.get_random_pair())

    def load(self):
        self.nodes = Nodes(nodes_file)
        self.edges = Edges(edges_file)


    def get_files(self):
        return (nodes_file, edges_file)

    def merge(self, other):
        #child1 =
        pass

    def writexml(self):
        ET.ElementTree(self.nodes.toxml()).write(self.nodes_file + self.append)
        ET.ElementTree(self.edges.toxml()).write(self.edges_file + self.append)

    def alter_edges(self):
        self.edges.alter(*self.nodes.get_random_pair())

class Node():
    def __init__(self, id, x, y):
        self.id = id
        self.x = float(x)
        self.y = float(y)
        print self.id, self.x, self.y

    def __str__(self):
        return 'x="%.2f" y="%.2f"' % (self.x, self.y)

    def toxml(self):
        return ET.Element("node", id=self.id, x=str(self.x), y=str(self.y))

class Nodes():
    def __init__(self, nodes):
        self.nodes = {}
        nodes = ET.parse(nodes)
        for node in nodes.getroot().getchildren():
            d = node.attrib
            self.nodes[d["id"]] = Node(d["id"], d["x"], d["y"])

    def get_random_pair(self):
        return random.sample(self.nodes.values(), 2)

    def toxml(self):
        xmlnodes = ET.Element("nodes")
        for k, node in self.nodes.items():
            xmlnodes.append(node.toxml())
        return xmlnodes


class Edge():
    def __init__(self, id, from_node, to_node, spread):
        self.id = id
        self.from_node = from_node
        self.to_node = to_node
        self.spread = spread

    def right_nodes(self, n1, n2):
        return (self.from_node == n1 and self.to_node == n2) or (self.from_node == n2 and self.to_node == n1)

    def toxml(self):
        return ET.Element("edge", id=self.id, fromnode=self.from_node, tonode=self.to_node, spread_type=self.spread)

class Edges():
    def __init__(self, edges):
        self.edges = {}
        edges = ET.parse(edges)
        for edge in edges.getroot().getchildren():
            d = edge.attrib
            self.edges[d["id"]] = Edge(d["id"], d["fromnode"], d["tonode"], d["spread_type"])

    def alter(self, n1, n2):
        """
        remove the edge is it is found, otherwise make a new one.
        """
        for edge in self.edges.values():
            if edge.right_nodes(n1.id, n2.id):
                del self.edges[edge.id]
                return
        id = str(len(self.edges))
        self.edges[id] = Edge(id, n1.id, n2.id, "center")

    def contains(self, edge):
        for e in self.edges.valuse():
            if e.right_nodes(e.from_node, e.to_node):
                return True
        return False

    def toxml(self):
        xmledges = ET.Element("edges")
        for k, edge in self.edges.items():
            xmledges.append(edge.toxml())
        return xmledges
    
if __name__=="__main__": 
    g = Graph("out", "hokkaido-japan/hokkaido.nod.xml", "hokkaido-japan/hokkaido.edg.xml")
    g.load()
    g.writexml()