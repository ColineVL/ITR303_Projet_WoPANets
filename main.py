from modelisation import Flow, Station, Target
from parseXML import parseNetwork


def testAvancer(target):
    edge = target.path[target.currentStep]
    if isinstance(edge.source, Station):
        return True
    port = edge.source.ports[edge.destination.name]
    return len(port.flowsPassed) == port.objectif


def main():
    # Constantes
    C = 100 * 10**6

    # Création du réseau
    file = "./documentation/samples/AFDX.xml"
    flows, arrayTargets = parseNetwork(file)

    # Premier calcul : les courbes d'arrivée des Stations
    for flow in flows.values():
        flow.source.arrivalCurveAggregated.add(flow.get_datalength(), flow.get_rate())

    # Deuxième passe : on calcule les délais de chaque Station de départ des flows
    # et on update la courbe d'arrivée de la dite Station

    for target in arrayTargets:
        source = target.flow.source
        source.delay = target.arrivalCurve.burst / C
        target.arrivalCurve.addDelay(source.delay)
        target.currentStep += 1

    # Début de la grande boucle de calcul
    # On passe sur toutes les target et on avance aussi loin que possible

    arrayTargetsToComplete = range(
        len(arrayTargets)
    )  # On va vider ce tableau au fur et à mesure qu'on complète des flows
    targetIndex = 0

    while len(arrayTargetsToComplete) > 0:
        # Il reste des targets à calculer !
        target = arrayTargets[targetIndex]

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
                    edge.source.getDelay(edge.destination) for edge in target.path
                )
                # Je signale que je l'ai terminée
                arrayTargetsToComplete.pop(targetIndex)

            else:
                # Il reste encore de la route, je passe au node suivant
                target.currentStep += 1
                edge = target.path[target.currentStep]
                port = edge.source.ports[edge.destination.nom]
                # Je m'ajoute dans la courbe d'arrivée de ce nouveau switch, si mon flow n'a pas déjà été compté
                flowDejaCompte = target.flow.name in port.flowsPassed
                if not flowDejaCompte:
                    port.arrivalCurveAggregated.add(
                        target.arrivalCurve.burst, target.arrivalCurve.rate
                    )
                    port.flowsPassed.append(target.flow.name)

                # Je vérifie si ce switch a toutes les infos qu'il lui faut pour calculer son délai, retour au début de la boucle while

        # Je suis bloqué ou j'ai fini, je passe à la target suivante
        targetIndex = (targetIndex + 1) % len(arrayTargetsToComplete)


if __name__ == "__main__":
    main()
