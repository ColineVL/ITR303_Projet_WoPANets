import xml.etree.ElementTree as ET
import os.path
import sys
from modelisation import *

file = "documentation\sample\3ESE.xml"

nodes = {}
edges = {}
flows = {}

""" parseStations
    Method to parse stations
        root : the xml main root
"""


def parseStations(root):
    for station in root.findall("station"):
        name = station.get("name")
        nodes[name] = Station(name)


""" parseSwitches
    Method to parse switches
        root : the xml main root
"""


def parseSwitches(root):
    for sw in root.findall("switch"):
        name = sw.get("name")
        nodes[name] = Switch(name)


""" parseEdges
    Method to parse edges
        root : the xml main root
"""


def parseEdges(root):
    for sw in root.findall("link"):
        source = nodes[sw.get("from")]
        dest = nodes[sw.get("to")]
        name = sw.get("name")
        edges.append(Edge(source, dest, name))


""" parseFlows
    Method to parse flows
        root : the xml main root
"""


def parseFlows(root):
    # D'abord on crée le flow correspondant
    for fl in root.findall("flow"):
        name = fl.get("name")
        source = nodes[fl.get("source")]

        flow = Flow(
            name, 67, float(fl.get("max-payload")), float(fl.get("period")), source
        )
        flows[name] = flow

        # Ensuite on crée les targets desservies
        for tg in fl.findall("target"):
            dest = nodes[tg.get("name")]
            target = Target(flow, dest)
            flow.targets.append(target)
            target.path.append(flow.source)
            for pt in tg.findall("path"):
                step = nodes[pt.get("node")]
                target.path.append(step)


""" parseNetwork
    Method to parse the whole network
        xmlFile : the path to the xml file
"""


def parseNetwork(xmlFile):
    if os.path.isfile(xmlFile):
        tree = ET.parse(xmlFile)
        root = tree.getroot()
        parseStations(root)
        parseSwitches(root)
        parseEdges(root)
        parseFlows(root)
    else:
        print("File not found: " + xmlFile)
