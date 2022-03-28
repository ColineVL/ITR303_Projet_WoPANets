def convertSeconds2Micro(seconds):
    return seconds * 10**6


def saveNetwork(xmlFile, flows, edges):
    """saveNetwork
    Method to save the delays in a new XML file
        xmlFile : the path to the xml (input) file
    """
    posDot = xmlFile.rfind(".")
    if not (posDot == -1):
        resFile = xmlFile[0:posDot] + "_res.xml"
    else:
        resFile = xmlFile + "_res.xml"
    res = open(resFile, "w")
    res.write('<?xml version="1.0" encoding="UTF-8"?>\n')
    res.write("<results>\n")
    # Les delays
    res.write("\t<delays>\n")
    for flow in flows:
        res.write('\t\t<flow name="' + flow.name + '">\n')
        for target in flow.targets:
            res.write(
                f'\t\t\t<target name="{target.destination.name}" value="{convertSeconds2Micro(target.totalDelay)}" />\n'
            )
        res.write("\t\t</flow>\n")
    res.write("\t</delays>\n")

    # Les loads
    res.write("\t<load>\n")
    for i in range(0, len(edges) - 1, 2):
        # Ils vont toujours par paires
        edgeDirect = edges[i]
        edgeReverse = edges[i + 1]
        res.write('\t\t<edge name="' + edgeDirect.name + '">\n')
        res.write(
            f'\t\t\t<usage percent="{edgeDirect.load:.1f}%" type="direct" value="{edgeDirect.arrivalCurveAggregated.rate}" />\n'
        )
        res.write(
            f'\t\t\t<usage percent="{edgeReverse.load:.1f}%" type="reverse" value="{edgeReverse.arrivalCurveAggregated.rate}" />\n'
        )
        res.write("\t\t</edge>\n")
    res.write("\t</load>\n")

    res.write("</results>\n")
    res.close()
    # file2output(resFile)


def file2output(file):
    """file2output
    Method to print a file to standard ouput
        file : the path to the xml (input) file
    """
    hFile = open(file, "r")
    for line in hFile:
        print(line.rstrip())
