import xml.etree.ElementTree as ET
import os.path
from modelisation import Flow, Station, Switch, Edge, Target


nodes = {}
edges = []
flows = {}
targets = []


def convertBytes2Bits(byte):
    return byte * 8


def convertMilli2Seconds(milliseconds):
    return milliseconds / 1000


def findEdge(source, dest):
    found = [
        index
        for index in range(len(edges))
        if (source.name == edges[index].source.name)
        and (dest.name == edges[index].destination.name)
    ]
    assert len(found) == 1

    return found[0]


def parseStations(root):
    """parseStations
    Method to parse stations
        root : the xml main root
    """
    for station in root.findall("station"):
        name = station.get("name")
        nodes[name] = Station(name)


def parseSwitches(root):
    """parseSwitches
    Method to parse switches
        root : the xml main root
    """
    for sw in root.findall("switch"):
        name = sw.get("name")
        nodes[name] = Switch(name)


def parseEdges(root):
    """parseEdges
    Method to parse edges
        root : the xml main root
    """
    for link in root.findall("link"):
        source = nodes[link.get("from")]
        dest = nodes[link.get("to")]
        name = link.get("name")

        # Pour chaque edge, je dois aussi l'ajouter dans les ports du switch source
        edge = Edge(source, dest, name)
        edges.append(edge)
        if isinstance(source, Switch):
            source.ports[dest.name] = edge
        # A chaque fois je le crée dans les deux sens
        edge = Edge(dest, source, name)
        edges.append(edge)
        if isinstance(source, Switch):
            source.ports[dest.name] = edge


def parseFlows(root):
    """parseFlows
    Method to parse flows
        root : the xml main root
    """
    # D'abord on crée le flow correspondant
    for fl in root.findall("flow"):
        name = fl.get("name")
        source = nodes[fl.get("source")]

        flow = Flow(
            name,
            convertBytes2Bits(67),
            convertBytes2Bits(float(fl.get("max-payload"))),
            convertMilli2Seconds(float(fl.get("period"))),
            source,
        )
        flows[name] = flow

        # Ensuite on crée les targets desservies
        for tg in fl.findall("target"):
            dest = nodes[tg.get("name")]
            target = Target(flow, dest)
            flow.targets.append(target)

            stepSource = source
            for pt in tg.findall("path"):
                stepDest = nodes[pt.get("node")]
                indexEdge = findEdge(stepSource, stepDest)
                target.path.append(edges[indexEdge])
                stepSource = stepDest

            targets.append(target)


def parseNetwork(xmlFile):
    """parseNetwork
    Method to parse the whole network
        xmlFile : the path to the xml file
    """
    if os.path.isfile(xmlFile):
        tree = ET.parse(xmlFile)
        root = tree.getroot()
        parseStations(root)
        parseSwitches(root)
        parseEdges(root)
        parseFlows(root)
        return flows, targets
    else:
        print("File not found: " + xmlFile)
