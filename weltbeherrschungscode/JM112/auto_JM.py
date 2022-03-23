import sys
import os


#Pfad für den Import der basisklassen
pfad = sys.path[0]
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(pfad)), "camp2code-project_phase_1", "Code"))
from basisklassen import *


#Objekte der Basisklassen
bw = Back_Wheels()
fw = Front_Wheels()
usm = Ultrasonic()
irm = Infrared()


class BaseCar():

    """Entwicklung und Testen einer Klasse BaseCar mittels der Basisklassen
        mit vorgegebenen Anforderungen. Die Klasse soll folgende Attribute (mit entsprechen‑
        den Gettern und Settern) und Methoden haben:
        • steering_angle: Zugriff auf den Lenkwinkel
        • drive(int, int): Fahren mit übergebener Geschwindigkeit und Fahrrichtung
        • stop(): Anhalten des Autos
        • speed: Zugriff auf die Geschwindigkeit
        • direction: Zugriff auf die Fahrrichtung (1: vorwärts, 0: Stillstand, ‑1 Rückwärts)
        Die Klasse BaseCar soll mittels folgenden Aufgaben getestet werden."""

    def __init__(self):
        self._speed = 0
        self._direction = 1
        self._steering_angle = 90
        
        

    @property
    def steering_angle(self):
        return self._steering_angle

    @steering_angle.setter
    def steering_angle(self, angle):
        self._steering_angle = angle
        fw.turn(angle)

    @property
    def speed(self):
        return self._speed

    @speed.setter
    def speed(self, speed):
        self._speed = speed

    @property
    def direction(self):
        return self._direction

    @direction.setter
    def direction(self, direction): 
        self._direction = direction

    def drive(self, speed_value, direction):
        self.speed = speed_value
        bw.speed = speed_value
        if direction == 1:
            self._direction = 1
            bw.forward()
        elif direction == -1:
            self._direction = -1
            bw.backward()
        else: 
            self._direction = 0
            self.stop()
    
    def stop(self):
            bw.stop()


class SonicCar(BaseCar):

    def __init__(self):
        super().__init__()
        self._distance = 0

    @property
    def distance(self):
        self._distance = usm.distance()
        return self._distance








    
#Hauptprogramm
@click.command()
@click.option('--modus', '--m', type=int, default=None, help="Startet Test für Klasse direkt.")
def main(modus):

    car = BaseCar()
    scar = SonicCar()

    print('-- Auswahl Fahrparcours --------------------')
    modi = {
        0: 'Frei',
        1: 'Fahrparcours 1 - Vorwärts und Rückwärts',
        2: 'Fahrparcours 2 - Kreisfahrt mit maximalem Lenkwinkel',
        3: 'Fahrparcours 3 - Vorwärtsfahrt bis Hindernis',
        4: 'Fahrparcours 4 - Erkundungstour',
        5: 'Fahrparcours 5 - Linienverfolgung',
        6: 'Fahrparcours 6 - Erweiterte Linienverfolgung',
        7: 'Fahrparcours 7 - Erweiterte Linienverfolgung mit Hindernisserkennung',
    }

    if modus == None:
        print('--' * 20)
        print('Auswahl:')
        for m in modi.keys():
            print('{i} - {name}'.format(i=m, name=modi[m]))
        print('--' * 20)

    while modus == None:
        modus = input('Wähle  (Andere Taste für Abbruch): ? ')
        if modus in ['0', '1', '2', '3', '4', '5', '6', '7']:
            break
        else:
            modus = None
            print('Getroffene Auswahl nicht möglich.')
            quit()
    modus = int(modus)

    if modus == 1:
        print("Fahrparcours 1 - Vorwärts und Rückwärts")
        car.drive(30, 1)
        time.sleep(3)
        car.stop()
        time.sleep(1)
        car.drive(50, -1)
        time.sleep(3)
        car.stop()
        print("Fahrparcours 1 - beendet")
        

    elif modus == 2:
        print('Fahrparcours 2 - Kreisfahrt mit maximalem Lenkwinkel')
        car.steering_angle = 90
        car.drive(30, 1)
        time.sleep(1)
        car.steering_angle = 135
        time.sleep(8)
        car.stop()
        car.drive(30, -1)
        time.sleep(8)
        car.steering_angle = 90
        car.drive(30, -1)
        time.sleep(1)
        car.stop()
        #entgegengesetzter Uhrzeigersinn
        car.steering_angle = 90
        car.drive(30, -1)
        time.sleep(1)
        car.steering_angle = 135
        time.sleep(8)
        car.stop()
        car.drive(30, 1)
        time.sleep(8)
        car.steering_angle = 90
        car.drive(30, 1)
        time.sleep(1)
        car.stop()

    elif modus == 3:
        print('Test Ultrasonic')
        scar.drive(50, 1)
        while True:
            if scar.distance >= 7 or scar.distance < 0:
                print(scar.distance)
                time.sleep(0.5)
            else:
                scar.stop()
                print("Hindernis")
                break

    elif modus == 4:
        print('Test Infrared')
        pass
    
    elif modus == 5:
        pass


if __name__ == '__main__':
    main()


    



