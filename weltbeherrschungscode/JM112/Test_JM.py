import sys, os, time
sys.path.append(os.path.dirname(sys.path[0]))
from auto_code import SensorCar

from datetime import datetime
import numpy as np

#Hauptprogramm
#@click.command()
#@click.option('--modus', '--m', type=int, default=None, help="Startet Test für Klasse direkt.")
def main(modus, car: SensorCar):

   
  

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
        print("vorwärts")
        car.drive(30, 1)
        time.sleep(3)
        print("stop")
        car.stop()
        time.sleep(1)
        print("rückwärts")
        car.drive(50, -1)
        time.sleep(3)
        print("stop")
        car.stop()
        print("Fahrparcours 1 - beendet")
        

    elif modus == 2:
        print('Fahrparcours 2 - Kreisfahrt mit maximalem Lenkwinkel')
        car.steering_angle = 90
        print("vorwärts")
        car.drive(30, 1)
        time.sleep(1)
        print("Lenkwinkel")
        car.steering_angle = 135
        time.sleep(8)
        print("stop")
        car.stop()
        print("rückwärts")
        car.drive(30, -1)
        time.sleep(8)
        print("Lenkwinkel")
        car.steering_angle = 90
        print("rückwärts")
        car.drive(30, -1)
        time.sleep(1)
        print("stop")
        car.stop()
        #entgegengesetzter Uhrzeigersinn
        car.steering_angle = 90
        print("rückwärts")
        car.drive(30, -1)
        time.sleep(1)
        print("Lenkwinkel")
        car.steering_angle = 135
        time.sleep(8)
        print("stop")
        car.stop()
        print("vorwärts")
        car.drive(30, 1)
        time.sleep(8)
        print("Lenkwinkel")
        car.steering_angle = 90
        print("vorwärts")
        car.drive(30, 1)
        time.sleep(1)
        print("stop")
        car.stop()

    elif modus == 3:
        print('Test Ultrasonic')
        car.drive(50, 1)
        while True:
            if car.distance >= 12 or car.distance < 0:
                print(car.distance)
                car.log()
                print("-" * 20)
                time.sleep(0.5)
            else:
                car.stop()
                print("Hindernis")
                print(car.distance)
                car.log()
                break
        

    elif modus == 4: 
        print('Erkundungstour')
        i = 0
        while i <= 3:
            car.drive(30, 1)
            while car.distance >= 12 or car.distance < 0:
                car.log()
                time.sleep(0.5)
                print("if1")
            else:
                car.stop()
                print("Hindernis")
                print(car.distance)
                car.steering_angle = 55
                car.drive(25, -1)
                while car.distance < 25:
                    car.log()
                    time.sleep(0.5)
                i += 1
        car.stop()
        print("Erkundungstour beendet")
        print("Daten in DB")





if __name__ == '__main__':
    # car anlegen
    car = SensorCar()

    try:
        modus = sys.argv[1]
    except:
        modus = None

    main(modus, car)
    car.stop()
    car.usm.stop()
    # Dataframe in DB schreiben
    car.write_log_to_db()
    print(car.df)
