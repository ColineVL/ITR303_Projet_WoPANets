from modelisation import Station
from parseXML import parseNetwork
from saveXML import saveNetwork
import sys


def ajouterMaCourbeArriveeDansSwitch(target, port):
    flowDejaCompte = target.flow.name in port.flowsPassed
    if not flowDejaCompte:
        port.arrivalCurveAggregated.add(
            target.arrivalCurve.burst, target.arrivalCurve.rate
        )
        port.flowsPassed.append(target.flow.name)


def testAvancer(target):
    edge = target.path[target.currentStep]
    if isinstance(edge.source, Station):
        return True
    if target.completed:
        # La target est complète, je ne peux plus l'avancer
        return False
    port = edge.source.ports[edge.destination.name]
    return len(port.flowsPassed) == port.objectif


def main(file):
    # Constantes
    C = 100 * 10**6

    # Création du réseau
    flows, arrayTargets = parseNetwork(file)

    # Premier calcul : les courbes d'arrivée des Stations
    for flow in flows.values():
        flow.source.arrivalCurveAggregated.add(flow.get_datalength(), flow.get_rate())

    # Deuxième passe : on calcule les délais de chaque Station de départ des flows
    # et on update la courbe d'arrivée de la dite Station
    # et j'ajoute ma courbe d'arrivée dans le premier switch
    for target in arrayTargets:
        source = target.flow.source
        source.delay = source.arrivalCurveAggregated.burst / C
        target.arrivalCurve.addDelay(source.delay)
        target.currentStep += 1

        edge = target.path[target.currentStep]
        port = edge.source.ports[edge.destination.name]
        ajouterMaCourbeArriveeDansSwitch(target, port)

    # Début de la grande boucle de calcul
    # On passe sur toutes les target et on avance aussi loin que possible
    nbTargetsToComplete = len(arrayTargets)
    nbTargetsCompleted = 0
    indexCurrentTarget = 0

    while nbTargetsCompleted < nbTargetsToComplete:
        # Il reste des targets à calculer !
        target = arrayTargets[indexCurrentTarget]

        if not target.completed:

            # Je vérifie si je peux avancer
            while testAvancer(target):
                # yay ! Je peux avancer !

                edge = target.path[target.currentStep]
                port = edge.source.ports[edge.destination.name]

                # J'update
                # Calcul du delay de edge.source
                port.delay = port.arrivalCurveAggregated.burst / C
                # J'aggrave ma courbe d'arrivée
                target.arrivalCurve.addDelay(port.delay)

                # Je vérifie si je suis arrivée à destination
                if target.path[target.currentStep] == target.path[-1]:
                    # On termine pour cette target
                    target.totalDelay = sum(
                        edge.source.getDelay(edge.destination.name)
                        for edge in target.path
                    )
                    # Je signale que je l'ai terminée
                    target.completed = True
                    nbTargetsCompleted += 1

                else:
                    # Il reste encore de la route, je passe au node suivant
                    target.currentStep += 1
                    edge = target.path[target.currentStep]
                    port = edge.source.ports[edge.destination.name]
                    # Je m'ajoute dans la courbe d'arrivée de ce nouveau switch, si mon flow n'a pas déjà été compté
                    ajouterMaCourbeArriveeDansSwitch(target, port)

                    # Je vérifie si ce switch a toutes les infos qu'il lui faut pour calculer son délai, retour au début de la boucle while

        # Je suis bloqué ou j'ai fini, je passe à la target suivante
        indexCurrentTarget = (indexCurrentTarget + 1) % nbTargetsToComplete

    # J'ai terminé de tout calculer
    saveNetwork(file, flows.values())


if __name__ == "__main__":
    if len(sys.argv) >= 2:
        xmlFile = sys.argv[1]
    else:
        xmlFile = "./documentation/samples/simple.xml"
    main(xmlFile)
