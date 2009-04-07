from __future__ import with_statement
import pipes
import os
import subprocess
import elementtree.ElementTree as ET
import network_mapping as nm
import threading

def throwAwayThread(targ):
    t = threading.Thread(target=targ)
    t.deamon = True
    t.start()
    t.run()

def writeNodesOrEdgesToPipe(et, pipe):
    """
    et - an Nodes or Edges object
    pipe - the string location of the pipe
    """
    ET.ElementTree(et.toxml()).write(pipe)

class SUMOInterface():
    id = 0
    def __init__(self, file_dir="/tmp/mondp/", sumo="sumo"):
        """
        file_dir - output directory. For reading and writing.
        sumo - "sumo executable"
        """
        self.id = SUMOInterface.id
        SUMOInterface.id += 1
        self.file_dir = file_dir
        self.sumo = sumo
        try:
            os.makedirs(self.file_dir)
        except:
            pass

    def setNodes(self, nodes):
        """

        """
        self.nodes = nodes

    def getFilename(filetype):
        def closure(self):
            return ''.join([self.file_dir, str(self.id), filetype])
        return closure

    getNodeFile = getFilename(".nod.xml")
    getEdgeFile = getFilename(".edg.xml")
    getNetFile = getFilename(".net.xml")
    getOutFile = getFilename(".out.xml")

    def applyToAllFilesWrapper(func):
        def applyToAllFiles(self):
            for f in (self.getNodeFile(), self.getEdgeFile(), self.getNetFile(), self.getOutFile()):
                try:
                    func(f)
                except:
                    pass
        return applyToAllFiles

    setup = applyToAllFilesWrapper(os.mkfifo)
    breakdown = applyToAllFilesWrapper(os.unlink)

    def writeNodes(self):
        writeNodesOrEdgesToPipe(self.nodes, pipes.Template().open(self.getNodeFile(), 'w'))

    def makeNetwork(self, edges):
        dev_null = open(os.devnull)
        edgef = pipes.Template().open(self.getEdgeFile(), 'w')
        nodef = pipes.Template().open(self.getNodeFile(), 'w')
        os.mkfifo(self.getNetFile())
        args = ['sumo-netconvert', '-v', '-n=' + self.getNodeFile(),  '-e',  self.getEdgeFile(), '-o', self.getNetFile()]
        writeNodesOrEdgesToPipe(self.nodes, nodef)
        writeNodesOrEdgesToPipe(edges, edgef)
        s = subprocess.Popen(args)#, stdout=dev_null.fileno(), stderr=dev_null.fileno())
        tree = None
        #with open(self.getNetFile(), 'r') as pin:
            #tree = ET.ElemenentTree(file=pin)
        edgef.close()
        nodef.close()
        dev_null.close()
        return tree

    def execute(self):
        dev_null = open(os.devnull)
        args = [self.sumo, '-b', '0', '-e', '1000', '-n', '/home/numix/school/ea/cs448/data/rand/net.net.xml', '-r', '/home/numix/school/ea/cs448/data/rand/rand.rou.xml', '--emissions-output', self.getOutFile()]
        p1 = subprocess.Popen(args, stdout=dev_null.fileno(), stderr=dev_null.fileno())
        tree = None
        with open(self.getOutFile(), 'r') as pin:
            tree = ET.ElementTree(file=pin)
        return tree

if __name__ == "__main__":
        s = SUMOInterface()
        s.breakdown()
        s.setNodes(nm.Nodes('/home/numix/school/ea/cs448/data/rand/rand.nod.xml'))
        net = s.makeNetwork(nm.Edges(s.nodes, '/home/numix/school/ea/cs448/data/rand/rand.edg.xml'))
        #print ET.tostring(net.getroot())
        #tree = s.execute()
        #last_el = tree.getroot()[-1].attrib
        #print float(last_el["meanTravelTime"]), float(last_el["meanWaitingTime"])
        #s.breakdown()
