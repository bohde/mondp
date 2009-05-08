from __future__ import with_statement
import pipes
import os
import subprocess
try:
    import xml.eltree.ElementTree as ET
except:
    import elementtree.ElementTree as ET
import network_mapping as nm
import threading
import random

def sfifo(f):
    try:
        os.mkfifo(f)
    except:
        pass

def throwAwayThread(targ):
    t = threading.Thread(target=targ)
    t.deamon = True
    t.start()
    #t.run()

def writeNodesOrEdgesToPipe(et, pipe):
    """
    et - an Nodes or Edges object
    pipe - the string location of the pipe
    """
    ET.ElementTree(et.toxml()).write(pipe)

class SUMOInterface():
    id = 0
    def __init__(self, file_dir="/home/numix/tmp/mondp%f/" % random.random(), sumo="sumo"):
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
    getRouteFile = getFilename(".rou.xml")

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

    def openPipeAndLambda(lambd):
        def wrap(self, f, obj):
            def inner():
                pipe = open(f, 'w')
                lambd(obj, pipe)
            sfifo(f)
            throwAwayThread(inner)
        return wrap

    openPipeAndWrite = openPipeAndLambda(writeNodesOrEdgesToPipe)
    openPipeAndWriteXML = openPipeAndLambda(lambda xml, f: xml.write(f))

    def makeNetwork(self, edges):
        dev_null = open(os.devnull)
        self.openPipeAndWrite(self.getEdgeFile(), edges)
        self.openPipeAndWrite(self.getNodeFile(), self.nodes)
        sfifo(self.getNetFile())
        args = ['sumo-netconvert', #'-v',
'-n=' + self.getNodeFile(),  '-e',  self.getEdgeFile(), '-o', self.getNetFile()]
        s = subprocess.Popen(args)#, stdout=dev_null.fileno(), stderr=dev_null.fileno())
        self.network = ET.ElementTree(file=self.getNetFile())

    def makeRoutes(self, flows):
        dev_null = open(os.devnull)
        self.openPipeAndWriteXML(self.getNetFile(), self.network)
        sfifo(self.getRouteFile())
        args = ["sumo-duarouter", "--flows=%s" % flows,  "--net=%s" % self.getNetFile(),  "--output-file=%s" % self.getRouteFile(),  "-b",  "0",  "-e" ,  "2000"]
        p1 = subprocess.Popen(args, stdout=dev_null.fileno(), stderr=dev_null.fileno())
        routes = ET.ElementTree(file=self.getRouteFile())
        self.openPipeAndWriteXML(self.getRouteFile(), routes)

    def execute(self):
        dev_null = open(os.devnull)
        self.openPipeAndWriteXML(self.getNetFile()+'2', self.network)
        sfifo(self.getOutFile())
        args = [self.sumo, #'-v',
'-b', '0', '-e', '2000', '-n', self.getNetFile()+'2', '-r', self.getRouteFile(), '--emissions-output', self.getOutFile()]
        p1 = subprocess.Popen(args, stdout=dev_null.fileno(), stderr=dev_null.fileno())
        tree = ET.ElementTree(file=self.getOutFile())
        return tree