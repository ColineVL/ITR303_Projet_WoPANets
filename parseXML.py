import xml.etree.ElementTree as ET
import os.path
from modelisation import Flow, Station, Switch, Edge, Target

# Des tableaux / dictionnaires à remplir !
nodes = {}
edges = []
flows = {}
targets = []


def convertBytes2Bits(byte):
    """Passer d'octets à bits"""
    return byte * 8


def convertMilli2Seconds(milliseconds):
    """Passer de ms à s"""
    return milliseconds / 1000


def findEdge(source, dest):
    """Trouver, dans edges, celui qui part de source pour aller à dest"""
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

        edge = Edge(source, dest, name)
        edges.append(edge)
        # A chaque fois je le crée dans les deux sens : je dois recommencer pour l'autre sens
        source, dest = dest, source
        edge = Edge(source, dest, name)
        edges.append(edge)


def parseFlows(root):
    """parseFlows
    Method to parse flows
        root : the xml main root
    """
    for fl in root.findall("flow"):

        # On crée le flow
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

        # Dans ce flow, on va croiser un certain nombre de edges, on les range ici (sans doublon please)
        edgesParcourusParTousTargets = []

        # Ensuite on crée les targets desservies
        for tg in fl.findall("target"):
            dest = nodes[tg.get("name")]
            target = Target(flow, dest)
            flow.targets.append(target)

            # Pour chaque étape dans le chemin de cette target...
            stepSource = source
            for pt in tg.findall("path"):
                stepDest = nodes[pt.get("node")]
                # On retrouve le edge correspondant et on l'ajoute au path
                edge = edges[findEdge(stepSource, stepDest)]
                target.path.append(edge)
                # Si je ne l'ai pas déjà croisé, je le note
                if edge not in edgesParcourusParTousTargets:
                    edgesParcourusParTousTargets.append(edge)
                stepSource = stepDest

            targets.append(target)

        # J'augmente l'objectif des edges parcourus par ce flow
        for edge in edgesParcourusParTousTargets:
            edge.objectif += 1


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
        return flows, targets, edges
    else:
        print("File not found: " + xmlFile)
