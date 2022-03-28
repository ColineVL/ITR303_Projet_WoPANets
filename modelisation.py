class Flow:
    """
    Un flow, entre deux stations, passant par des switch.

    Attributes
    ----------
    overhead : float
        Nombre d'octets de l'overhead, bits
    payload : float
        Nombre d'octets de la charge utile, bits
    name : str
        Identifiant du flow
    period : float
        Période d'émission des messages, en s
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
        return self.get_datalength() / self.period

    def __repr__(self):
        return f"Flow {self.name}"

    def __str__(self):
        return f"Flow {self.name}"


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
    currentStep : float
        Indice de path : où on s'est arrêté la dernière fois qu'on a calculé quelque chose sur ce flow pour cette target
    arrivalCurve : ArrivalCurve
        Courbe d'arrivé du flow pour cette target
    totalDelay : float
        Délai total du flow pour cette target, en s
    completed : bool
        True si cette target a été complétée
    """

    def __init__(self, flow, destination):
        self.path = []
        self.flow = flow
        self.destination = destination
        self.currentStep = 0
        self.arrivalCurve = ArrivalCurve(flow.get_datalength(), flow.get_rate())
        self.totalDelay = 0
        self.completed = False


class ArrivalCurve:
    """
    Représente une courbe d'arrivée affine.

    Attributes
    ----------
    burst : float
        Valeur du burst, en s
    rate : float
        Valeur du rate, en s
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
    objectif : float
        Nombre de flows qui arrivent dans la source et qui ensuite partent vers destination
    arrivalCurveAggregated : ArrivalCurve
        Somme des courbes d'arrivée des flows arrivant sur source et partant vers destination
    flowsPassed : array
        Tableau des identifiants des flows déjà comptabilisés dans la arrivalCurveAggregated
    delay : float
        Délai subi en passant par ce edge, en s

    """

    def __init__(self, source, destination, name):
        self.source = source
        self.destination = destination
        self.name = name
        self.objectif = 0
        self.arrivalCurveAggregated = ArrivalCurve(0, 0)
        self.flowsPassed = []

    def __repr__(self):
        return f"Edge from {self.source.name} to {self.destination.name}"

    def __str__(self):
        return f"Edge from {self.source.name} to {self.destination.name}"


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

    def __repr__(self):
        return f"Node {self.name}"

    def __str__(self):
        return f"Node {self.name}"


class Switch(Node):
    """
    Un switch

    Attributes
    ----------
    ports : dict
        L'ensemble des Edges partant de ce switch : mappe nom destination du edge -> edge
    """

    def __init__(self, name):
        self.ports = {}
        super().__init__(name)

    def getDelay(self, nomDestination):
        return self.ports[nomDestination].delay


class Station(Node):
    """
    Une station, ou end system. La source et la destination des flows.

    Attributes
    ----------
    arrivalCurveAggregated : ArrivalCurve
        Courbe d'arrivée agrégée des flows qui partent de cette station (la somme quoi)
    delay : float
        Délai de la station, en s
    """

    def __init__(self, name):
        self.arrivalCurveAggregated = ArrivalCurve(0, 0)
        super().__init__(name)

    def getDelay(self, nomDestination):
        return self.delay
