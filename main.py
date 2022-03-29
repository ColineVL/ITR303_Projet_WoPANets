from parseXML import parseNetwork
from saveXML import saveNetwork
import sys


def ajouterMaCourbeArriveeDansSwitch(target, edge):
    flowDejaCompte = target.flow.name in edge.flowsPassed
    if not flowDejaCompte:
        edge.arrivalCurveAggregated.add(
            target.arrivalCurve.burst, target.arrivalCurve.rate
        )
        edge.flowsPassed.append(target.flow.name)


def testAvancer(target):
    # Si la target est complète, je ne peux plus l'avancer
    if target.completed:
        return False

    edge = target.path[target.currentStep]
    # Dans les autres cas on regarde si le edge est complet
    return len(edge.flowsPassed) == edge.objectif


def main(file):
    # Constante
    C = 100 * 10**6

    # Création du réseau à partir du XML input
    flows, arrayTargets, edges = parseNetwork(file)

    # Premier calcul : les courbes d'arrivée des Stations, on aggrège pour chaque Station tout ce qui en part
    for flow in flows.values():
        flow.source.arrivalCurveAggregated.add(flow.get_datalength(), flow.get_rate())

    # Deuxième passe : on calcule les délais de chaque Station de départ des flows
    # Ce délai se retrouve dans chacun des edges partant de cette station
    for target in arrayTargets:
        source = target.flow.source  # Station de départ
        # Je calcule le délai de la source du flow, je le stocke dans le edge (si ce n'est pas déjà fait)
        edge = target.path[target.currentStep]
        if edge.delay == 0:
            edge.delay = source.arrivalCurveAggregated.burst / C
        # J'applique le délai sur ma propre courbe d'arrivée
        target.arrivalCurve.addDelay(edge.delay)
        # Dans mon chemin vers la target, je peux passer au step suivant
        # Et j'ajoute ma courbe d'arrivée dans le premier switch du path
        target.currentStep += 1
        edge = target.path[target.currentStep]
        ajouterMaCourbeArriveeDansSwitch(target, edge)

    # Début de la grande boucle de calcul
    # On passe sur toutes les target et on avance aussi loin que possible
    nbTargetsToComplete = len(
        arrayTargets
    )  # Nombre de targets pour lesquelles il faut compléter le chemin (ie calculer le délai sur chaque node)
    nbTargetsCompleted = 0  # Nombre de targets qu'on a déjà finies
    indexCurrentTarget = 0  # Index de la target qu'on est en train de travailler

    while nbTargetsCompleted < nbTargetsToComplete:
        # Il reste des targets à calculer !
        target = arrayTargets[indexCurrentTarget]

        # Je vérifie si je peux avancer
        while testAvancer(target):
            # yay ! Je peux avancer !

            edge = target.path[target.currentStep]

            # J'update
            # Calcul du delay de ce edge, si ce n'est pas déjà fait
            if edge.delay == 0:
                edge.delay = edge.arrivalCurveAggregated.burst / C
            # J'aggrave ma courbe d'arrivée
            target.arrivalCurve.addDelay(edge.delay)

            # Je vérifie si je suis arrivée à destination
            if target.path[target.currentStep] == target.path[-1]:
                # On termine pour cette target
                target.totalDelay = sum(edge.delay for edge in target.path)
                # Je signale que je l'ai terminée
                target.completed = True
                nbTargetsCompleted += 1

            else:
                # Il reste encore de la route, je passe au edge suivant
                target.currentStep += 1
                edge = target.path[target.currentStep]
                # Je m'ajoute dans la courbe d'arrivée de ce nouveau switch, si mon flow n'a pas déjà été compté
                ajouterMaCourbeArriveeDansSwitch(target, edge)

                # Je vérifie si ce switch a toutes les infos qu'il lui faut pour calculer son délai, retour au début de la boucle while !

        # Je suis bloqué ou j'ai fini, je passe à la target suivante
        indexCurrentTarget = (indexCurrentTarget + 1) % nbTargetsToComplete

    # Calcul des load sur chaque edge
    for edge in edges:
        edge.load = edge.arrivalCurveAggregated.rate * 100 / C

    # J'ai terminé de tout calculer, on exporte !
    saveNetwork(file, flows.values(), edges)


if __name__ == "__main__":
    if len(sys.argv) >= 2:
        xmlFile = sys.argv[1]
    else:
        xmlFile = "./documentation/samples/AFDX.xml"
    main(xmlFile)
