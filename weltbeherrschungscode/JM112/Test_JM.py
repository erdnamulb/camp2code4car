import sys, os, time
sys.path.append(os.path.dirname(sys.path[0]))
from auto_code import SensorCar

from datetime import datetime
import numpy as np

def linienfahrt():
    #Kalibrierung
        #car.irm.cali_references()
        #print(car.irm._references)
        #Setze Kalibrierreferenz
        #set_references([132.64, 125.52, 124.655, 125.995, 118.575])

        a_angle = 3
        b_angle = 10
        c_angle = 30
        d_angle = 45

        off_track_count = 0

        #car.drive(40, 1)

        while True:
            time.sleep(.01)
            #als Klassenmethode
            irm_status = car.irm.read_digital()
            print(irm_status)

            #benötigter Lenkwinkel ermitteln
            if irm_status == [0, 0, 1, 0, 0]:
                angle = 0
                print(0)
            elif irm_status == [0, 1, 1, 0, 0] or irm_status == [0, 0, 1, 1, 0]:
                angle = a_angle
                print("a")
            elif irm_status == [0, 1, 0, 0, 0] or irm_status == [0, 0, 0, 1, 0]:
                angle = b_angle
                print("b")
            elif irm_status == [1, 1, 0, 0, 0] or irm_status == [0, 0, 0, 1, 1]:
                angle = c_angle
                print("c")
            elif irm_status == [1, 0, 0, 0, 0] or irm_status == [0, 0, 0, 0, 1]:
                angle = d_angle
                print("d")

            #Lenkwinkel einstellen
            if irm_status == [0, 0, 1, 0, 0]:
                car.steering_angle = 90
                off_track_count = 0
                print(90)
            elif irm_status in ([0, 1, 1, 0, 0], [0, 1, 0, 0, 0], [1, 1, 0, 0, 0], [1, 0, 0, 0, 0]):
                car.steering_angle = int(90 - angle)
                off_track_count = 0
                print("links")
            elif irm_status in ([0, 0, 1, 1, 0], [0, 0, 0, 1, 0], [0, 0, 0, 1, 1], [0, 0, 0, 0, 1]):
                car.steering_angle = int(90 + angle)
                off_track_count = 0
                print("rechts")
            elif irm_status == [0, 0, 0, 0, 0]:
                off_track_count += 1
                if off_track_count > 25:
                    car.stop()
                    print("fehlende Fahrbahn")
                    break


def linienfahrt_Hindernisserkennung():
    

        a_angle = 3
        b_angle = 10
        c_angle = 30
        d_angle = 45

        off_track_count = 0

        #car.drive(40, 1)

        while True:
            if car.distance >= 12 or car.distance < 0:
                time.sleep(.01)
                irm_status = car.irm.read_digital()
                print(irm_status)

                #benötigter Lenkwinkel ermitteln
                if irm_status == [0, 0, 1, 0, 0]:
                    angle = 0
                    print(0)
                elif irm_status == [0, 1, 1, 0, 0] or irm_status == [0, 0, 1, 1, 0]:
                    angle = a_angle
                    print("a")
                elif irm_status == [0, 1, 0, 0, 0] or irm_status == [0, 0, 0, 1, 0]:
                    angle = b_angle
                    print("b")
                elif irm_status == [1, 1, 0, 0, 0] or irm_status == [0, 0, 0, 1, 1]:
                    angle = c_angle
                    print("c")
                elif irm_status == [1, 0, 0, 0, 0] or irm_status == [0, 0, 0, 0, 1]:
                    angle = d_angle
                    print("d")

                #Lenkwinkel einstellen
                if irm_status == [0, 0, 1, 0, 0]:
                    car.steering_angle = 90
                    off_track_count = 0
                    print(90)
                elif irm_status in ([0, 1, 1, 0, 0], [0, 1, 0, 0, 0], [1, 1, 0, 0, 0], [1, 0, 0, 0, 0]):
                    car.steering_angle = int(90 - angle)
                    off_track_count = 0
                    print("links")
                elif irm_status in ([0, 0, 1, 1, 0], [0, 0, 0, 1, 0], [0, 0, 0, 1, 1], [0, 0, 0, 0, 1]):
                    car.steering_angle = int(90 + angle)
                    off_track_count = 0
                    print("rechts")
                elif irm_status == [0, 0, 0, 0, 0]:
                    off_track_count += 1
                    if off_track_count > 25:
                        car.stop()
                        print("fehlende Fahrbahn")
                        break
            else:
                car.stop()
                print("Hinderniss entfernen")
                while car.distance <= 50:
                    time.sleep(1)
                car.drive(30, 1)
                


        


#Hauptprogramm
#@click.command()
#@click.option('--modus', '--m', type=int, default=None, help="Startet Test für Klasse direkt.")
def main(modus, car: SensorCar):

    #Digitale Infrarot Sensoren kalibrieren
    #car.irm.set_references([132.64, 125.52, 124.655, 125.995, 118.575])
    #print("Aufruf Kalibrierung")
    #car.calibrate_ir()
    #print("Ende Kalibrierung")
   
  

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
        9: 'Lenkungsdauertest',
    }

    if modus == None:
        print('--' * 20)
        print('Auswahl:')
        for m in modi.keys():
            print('{i} - {name}'.format(i=m, name=modi[m]))
        print('--' * 20)

    while modus == None:
        modus = input('Wähle  (Andere Taste für Abbruch): ? ')
        if modus in ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']:
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
        #car.drive(50, 1)
        while True:
            if car.distance >= 12 or car.distance < 0:
                print(car.distance)
                #Nur Infrarot Sensor Test
                print(car.irm.read_digital())
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


    elif modus == 5:
        print(modi[modus])
        car.drive(30, 1)
        print("Folge der der Fahrbahn")
        linienfahrt()
        car.stop()
        print("Ende")



    elif modus == 6:
        print(modi[modus])
        print("Folge der Fahrbahn")
        while True:
            car.drive(30, 1)
            linienfahrt()
            if car.steering_angle < 50 or car.steering_angle > 50:
                tmp_angle = (car.steering_angle - 90) / abs(90 - car.steering_angle)
                tmp_angle = tmp_angle * 45 + 90
                car.steering_angle = tmp_angle

                off_track_count = 0
                car.drive(25, -1)
                while off_track_count < 15:
                    off_track_count += 1
                    irm_status = car.irm.read_digital()
                    if irm_status in ([1, 1, 0, 0, 0], [0, 1, 0, 0, 0], [0, 0, 0, 1, 1], [0, 0, 0, 1, 0]):
                        break
                    time.sleep(.05)
                car.stop()
                if off_track_count >= 15:
                    print("Zeitüberschreitung bei der Fahrbahnsuche")
                    break
            else:
                print("Fahrparcour beendet")
                break
                    

                    
     elif modus == 7:
        print(modi[modus])
        print("Folge der Fahrbahn")
        while True:
                car.drive(30, 1)
                linienfahrt_Hindernisserkennung()
                if car.steering_angle < 50 or car.steering_angle > 50:
                    tmp_angle = (car.steering_angle - 90) / abs(90 - car.steering_angle)
                    tmp_angle = tmp_angle * 45 + 90
                    car.steering_angle = tmp_angle

                    off_track_count = 0
                    car.drive(25, -1)
                    while off_track_count < 15:
                        off_track_count += 1
                        irm_status = car.irm.read_digital()
                        if irm_status in ([1, 1, 0, 0, 0], [0, 1, 0, 0, 0], [0, 0, 0, 1, 1], [0, 0, 0, 1, 0]):
                            break
                        time.sleep(.05)
                    car.stop()
                    if off_track_count >= 15:
                        print("Zeitüberschreitung bei der Fahrbahnsuche")
                        break
                else:
                    print("Fahrparcour beendet")
                    break
            else:
                car.stop()
                print("Hinderniss entfernen")
                while car.distance <= 50:
                    time.sleep(1)
    

            



   

    elif modus == 9:
        for i in range(20):
            print(modi[modus])
            print(50)
            car.steering_angle = 50
            time.sleep(1)
            print(90)
            car.steering_angle = 90
            time.sleep(1)
            print(130)
            car.steering_angle = 130
            time.sleep(1)
            print(90)
            car.steering_angle = 90
            time.sleep(1)








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
