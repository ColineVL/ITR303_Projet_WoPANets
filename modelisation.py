def convertSeconds(milliseconds):
    return milliseconds / 1000


class Flow:
    """
    Un flow, entre deux stations, passant par des switch.

    Attributes
    ----------
    overhead : int
        Nombre d'octets de l'overhead, bytes
    payload : int
        Nombre d'octets de la charge utile, bytes
    name : str
        Identifiant du flow
    period : int
        Période d'émission des messages, ms
    source : Station
        Début du flow
    targets: array
        Tableau des Stations destination desservies par ce flow
    """

    def __init__(self, name, overhead, payload, period, source):
        self.name = name
        self.overhead = overhead
        self.payload = payload
        self.period = period
        self.source = source
        self.targets = []

    def get_datalength(self):
        return self.overhead + self.payload

    def get_rate(self):
        return self.get_datalength() / convertSeconds(self.period)


class Target:
    """
    La destination d'un flow

    Attributes
    ----------
    path : array
        Tableau des Edges parcourus par le flow parent pour atteindre cette target
    flow : Flow
        Flow parent
    destination : Station
        La target en elle-même : où va-t-on ?
    currentStep : int
        Indice de path : où on s'est arrêté la dernière fois qu'on a calculé quelque chose sur ce flow pour cette target
    arrivalCurve : ArrivalCurve
        Courbe d'arrivé du flow pour cette target
    totalDelay : int
        Délai total du flow pour cette target, en ms
    """

    def __init__(self, flow, destination):
        self.path = []
        self.flow = flow
        self.destination = destination
        self.currentStep = 0
        self.arrivalCurve = ArrivalCurve(flow.get_datalength(), flow.rate)
        self.totalDelay = 0


class ArrivalCurve:
    """
    Représente une courbe d'arrivée affine.

    Attributes
    ----------
    burst : int
        Valeur du burst, en ms
    rate : int
        Valeur du rate, en ms
    """

    def __init__(self, burst, rate):
        self.burst = burst
        self.rate = rate

    def add(self, burst, rate):
        self.burst += burst
        self.rate += rate

    def addDelay(self, delay):
        self.burst += delay * self.rate


class Edge:
    """
    Un bout de chemin, qui relie deux Nodes.
    C'est également un port du Node source.

    Attributes
    ----------
    source : Node
        Début du edge
    destination : Node
        Fin du edge
    name : str
        Identifiant du edge
    objectif : int
        Nombre de flows qui arrivent dans la source et qui ensuite partent vers destination
    increment : int
        Nombre de ces flows de passage qu'on a déjà comptabilisés dans la arrivalCurveAggregated
        # TODO inutile puisqu'on fait la liste dans flowPassed ?
    arrivalCurveAggregated : ArrivalCurve
        Somme des courbes d'arrivée des flows arrivant sur source et partant vers destination
    flowsPassed : array
        Tableau des identifiants des flows déjà comptabilisés dans la arrivalCurveAggregated
    delay : int
        Délai subi en passant par ce edge

    """

    def __init__(self, source, destination, name):
        self.source = source
        self.destination = destination
        self.name = name
        self.objectif = 0
        self.increment = 0
        self.arrivalCurveAggregated = ArrivalCurve(0, 0)
        self.flowPassed = []


class Node:
    """
    Un switch ou une station

    Attributes
    ----------
    name : str
        Identifiant du node
    """

    def __init__(self, name):
        self.name = name


class Switch(Node):
    """
    Un switch

    Attributes
    ----------
    ports : array
        L'ensemble des Edges partant de ce switch
    """

    def __init__(self, name):
        self.ports = []
        super().__init__(name)


class Station(Node):
    """
    Une station, ou end system. La source et la destination des flows.

    Attributes
    ----------
    arrivalCurveAggregated : ArrivalCurve
        Courbe d'arrivée agrégée des flows qui partent de cette station (la somme quoi)
    delay : int
        Délai de la station, en ms
    """

    def __init__(self, name):
        self.arrivalCurveAggregated = ArrivalCurve(0, 0)
        super().__init__(name)
