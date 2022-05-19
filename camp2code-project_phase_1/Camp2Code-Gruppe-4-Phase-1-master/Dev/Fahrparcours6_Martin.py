import PiCar
import numpy as np
import time
import random


Fahrzeug = PiCar.SensorCar()


def irMessung(anzahl=10):
    messergebnis = Fahrzeug.ir.get_average(anzahl)
    print(messergebnis)
    """
    print(f'Mittelw.:{irwerte.mean()}')
    print(f'Standardabw.: {irwerte.std()}')
    print(f'Spanne: {irwerte.ptp()} ')
    """
    return messergebnis


def checklinie(value):
    messergebnis = np.array(value)
    if (messergebnis.std() / messergebnis.mean()) < 0.2:
        # if (messergebnis.mean() / messergebnis.ptp()) > 2.5:
        print("Keine Linie zu erkennen, starte Liniensuche")
        checkergebnis = False
    else:
        checkergebnis = True
    return checkergebnis


def ergebnisinterpretation(value):
    messergebnis = np.array(value)
    interpretation = np.where(
        messergebnis < (messergebnis.mean() - 0.8 * messergebnis.std()), 1, 0
    )
    print(interpretation)
    return interpretation


laufzeit = 400
startzeit = time.time()
Fahrzeug.steering_angle = 0
linienflag = None

while time.time() - startzeit < laufzeit:

    messergebnis = irMessung(20)

    linienflag = checklinie(messergebnis)

    if linienflag == True:
        # normales Linienverfolgungsprogramm

        Fahrzeug.drive(50, 1)

        interpretation = ergebnisinterpretation(messergebnis)

        if interpretation.sum() == 1:  # nur ein Sensor schlägt aus
            if interpretation[0] == 1:  # hart links
                Fahrzeug.steering_angle = -40
            elif interpretation[1] == 1:  # leicht links
                Fahrzeug.steering_angle = -15
            elif interpretation[2] == 1:  # mitte
                Fahrzeug.steering_angle = 0
            elif interpretation[3] == 1:  # leicht rechts
                Fahrzeug.steering_angle = 15
            elif interpretation[4] == 1:  # hart rechts
                Fahrzeug.steering_angle = 40

        elif interpretation.sum() == 2:  # zwei Sensoren schlagen aus
            if interpretation[0] == 1 & interpretation[1] == 1:
                Fahrzeug.steering_angle = -30
            elif interpretation[1] == 1 & interpretation[2] == 1:
                Fahrzeug.steering_angle = -7.5
            elif interpretation[2] == 1 & interpretation[3] == 1:
                Fahrzeug.steering_angle = 7.5
            elif interpretation[3] == 1 & interpretation[4] == 1:
                Fahrzeug.steering_angle = 30

    else:
        # Linie wieder suchen
        if Fahrzeug.steering_angle > 0:
            Fahrzeug.steering_angle = -40
        elif Fahrzeug.steering_angle < 0:
            Fahrzeug.steering_angle = 40
        else:
            Fahrzeug.steering_angle = random.choice([-40, 40])
        Fahrzeug.drive(40, -1)
        while linienflag == False:
            linienflag = checklinie(irMessung(20))

    #  time.sleep(0.3)

# time.sleep(0.1)


Fahrzeug.stop()
print("Fahrt nach Ablauf der Zeit beendet")
