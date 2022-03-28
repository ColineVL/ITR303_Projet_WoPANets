def convertSeconds2Micro(seconds):
    return seconds * 10**6


def saveNetwork(xmlFile, flows):
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
    res.write("\t<delays>\n")
    for flow in flows:
        res.write('\t\t<flow name="' + flow.name + '">\n')
        for target in flow.targets:
            res.write(
                '\t\t\t<target name="'
                + target.destination.name
                + '" value="'
                + str(convertSeconds2Micro(target.totalDelay))
                + '" />\n'
            )
        res.write("\t\t</flow>\n")
    res.write("\t</delays>\n")
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
