from modelisation import Edge, Flow, Station, Target


def main():
    # Constantes
    C = 100 * 10**6

    station = Station("testStation")
    arrayFlows = [Flow("test", 1, 2, 4, station)]
    target = Target(arrayFlows[0], station)
    arrayTargets = [target]

    # Premier calcul : les courbes d'arrivée des Stations
    for flow in arrayFlows:
        flow.source.arrivalCurveAggregated.add(flow.get_datalength, flow.get_rate)

    # Deuxième passe : on calcule les délais de chaque Station de départ des flows
    # et on update la courbe d'arrivée de la dite Station

    for target in arrayTargets:
        source = target.flow.source
        source.delay = target.arrivalCurve.burst / C
        target.arrivalCurve.addDelay(source.delay)


if __name__ == "__main__":
    main()
