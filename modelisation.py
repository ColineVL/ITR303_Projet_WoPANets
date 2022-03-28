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
        self.targets = []  # rempli quand on parse le XML

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
        Courbe d'arrivée du flow pour cette target
    totalDelay : float
        Délai total du flow pour cette target, en s
    completed : bool
        True si cette target a été complétée
    """

    def __init__(self, flow, destination):
        self.path = []  # rempli quand on parse le XML
        self.flow = flow
        self.destination = destination
        self.currentStep = 0  # incrémenté au fur et à mesure du calcul
        self.arrivalCurve = ArrivalCurve(
            flow.get_datalength(), flow.get_rate()
        )  # On la décalera d'un certain délai à chaque fois que l'on partira d'un node
        self.totalDelay = 0  # Calculé à la fin, quand tout est prêt pour ce chemin
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
        """On aggrège une nouvelle courbe, on somme donc"""
        self.burst += burst
        self.rate += rate

    def addDelay(self, delay):
        """On décale d'un certain delay, ça ne change pas le rate"""
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
    load : float
        Charge du edge, en % (par rapport au débit maximal)
    """

    def __init__(self, source, destination, name):
        self.source = source
        self.destination = destination
        self.name = name
        self.objectif = 0  # Calculé à la fin du parseXML
        self.arrivalCurveAggregated = ArrivalCurve(
            0, 0
        )  # On aggrègera toutes les courbes qui passeront par ce Edge
        self.flowsPassed = (
            []
        )  # Quand on aggrège, on le note ici aussi pour ne pas oublier qu'on l'a déjà mis !
        self.delay = 0  # Calculé quand on aura fini de tout aggréger
        self.load = 0  # Calculé tout à la fin, pour comparer à C

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
        self.ports = {}  # Rempli dans le parseXML
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
        self.arrivalCurveAggregated = ArrivalCurve(
            0, 0
        )  # Calculé pendant la première passe du programme
        self.delay = 0  # Calculé pendant la deuxième passe du programme
        super().__init__(name)

    def getDelay(self, _):
        return self.delay
