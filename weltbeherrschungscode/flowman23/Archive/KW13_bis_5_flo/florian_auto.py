import sys, os, time

from numpy import int16
sys.path.append(os.path.dirname(sys.path[0]))

import random

# hier kommen die drei Car Klassen her
from auto_code import SensorCar

def follow_line(car: SensorCar, runs: int = 200, sleep: float = 0.01):
    car.steering_angle = 90
    steering_angle = car.steering_angle
    a_step = 5
    b_step = 15
    c_step = 30
    d_step = 45
    i = 1
    count = 0
    while i <= runs:
        # Sensoren auswerten
        _, ir_data = car.log_and_read_values
        # Angle calculate
        if	ir_data == [0,0,1,0,0]:
            step = 0	
        elif ir_data == [0,1,1,0,0] or ir_data == [0,0,1,1,0]:
            step = a_step
        elif ir_data == [0,1,0,0,0] or ir_data == [0,0,0,1,0]:
            step = b_step
        elif ir_data == [1,1,0,0,0] or ir_data == [0,0,0,1,1]:
            step = c_step
        elif ir_data == [1,0,0,0,0] or ir_data == [0,0,0,0,1]:
            step = d_step

        # straightforward
        if	ir_data == [0,0,1,0,0]:
            steering_angle = 90
            count = 0
        # turn right
        elif ir_data in ([0,1,1,0,0],[0,1,0,0,0],[1,1,0,0,0],[1,0,0,0,0]):
            steering_angle = int(90 - step)
            count = 0
        # turn left
        elif ir_data in ([0,0,1,1,0],[0,0,0,1,0],[0,0,0,1,1],[0,0,0,0,1]):
            steering_angle = int(90 + step)
            count = 0
        
        print(f"{ir_data} --> Lenkposition: {steering_angle}", " -- Messung:", i)
        # Prüfen, ob Linie noch da ist
        
        if ir_data == [0,0,0,0,0]:
            count += 1
            if count > 30:
                break
                # Schleife beenden, wenn x mal keine Linie gefuden

        # Lenken
        car.steering_angle = steering_angle
        time.sleep(sleep)
        i += 1

# Eigene Funktionen

def print_data(car: SensorCar):
    print("Abstand zum Hindernis", car.distance)
    print("Geschwindigkeit:", car.speed)
    print("Fahrrichtung:", "vorwärts" if car.direction == 1 else "rückwärts")
    print("Lenkwinkel:", car.steering_angle)
    print(20*"--")


def main(modus, car: SensorCar):

    # mit folgenden vier Zeilen bei Bedarf den IR Sensor rekalibrieren und den wert unten hart eincoden
    #car.irm.cali_references()
    #print(car.irm._references)
    #ref = car.irm._references
    #print (ref)
    
    # Hard-coded digitale Schwellenwerte IR Sensor:
    #ref = [65.85, 73.55, 76.58, 77.595, 84.835]
    # Ist jetzt über Programm 8 einzustellen

    print('--' * 27)
    print('-------------------- Fahrparcours --------------------')
    modi = {
        1: 'Fahrparcours 1 - Vorwärts und Rückwärts',
        2: 'Fahrparcours 2 - Kreisfahrt mit max. Lenkwinkel',
        3: 'Fahrparcours 3 - Vorwärtsfahrt bis Hindernis',
        4: 'Fahrparcours 4 - Erkundungstour',
        5: 'Fahrparcours 5 - Linienverfolgung',
        6: 'Fahrparcours 6 - Erweiterte Linienverfolgung',
        7: 'Fahrparcours 7 - 6. + Hinderniserkennung',
        8: 'Infrarot-Sensor kalibrieren und Setting in JSON schreiben',
        0: 'Ende'
    }

    if modus == None:
        print('--' * 27)
        print('Auswahl:')
        for m in modi.keys():
            print('{i} - {name}'.format(i=m, name=modi[m]))
        print('--' * 20)

    while True:

        while modus == None:
            modus = input('Wähle (Andere Taste für Abbruch): ? ')
            if modus in ['1', '2', '3', '4', '5', '6', '7', '8', '0']:
                break
            else:
                modus = None
                print('Getroffene Auswahl nicht möglich.')
                quit()
        modus = int(modus)
        print('--' * 15)

        if modus == 1:
            print(modi[modus])
            car.drive(50,1)
            time.sleep(3)
            car.stop()
            time.sleep(1)
            car.drive(50,-1)
            time.sleep(3)
            car.stop()

        elif modus == 2:
            print(modi[modus])
            car.drive(50, 1)
            time.sleep(1)
            car.stop()
            time.sleep(1)
            car.steering_angle = 135
            car.drive(50, 1)
            time.sleep(8)
            car.stop()
            car.steering_angle = 90

        elif modus == 3:
            print(modi[modus])
            car.drive(50,1)
            distance, _ = car.log_and_read_values
            while distance > 60 or distance < 0:
                distance, _ = car.log_and_read_values
                print_data(car)
                time.sleep(.3)
            car.drive(20,1)
            while distance > 15 or distance < 0:
                distance, _ = car.log_and_read_values
                print_data(car)
                time.sleep(.3)
            car.stop()
            print("Auto angehalten")
       
        elif modus == 4:
            print(modi[modus])
            
            i=1
            anzahl_durchlauf = 3
            while i <= anzahl_durchlauf:
                print("--" * 10)
                print("Durchlauf:", i, "von", anzahl_durchlauf)
                set_distance = 30
                print("Fahre Vorwärts bis Abstand:", set_distance)
                car.steering_angle = 90
                car.drive(40,1)
                distance, _ = car.log_and_read_values
                while distance > set_distance or distance < 0:
                    distance, _ = car.log_and_read_values
                    print_data(car)
                    car.log()
                    time.sleep(.5)
                print("Hindernis erkannt - Auto angehalten")
                car.stop()
                time.sleep(1.0)

                set_distance = 60
                print("Fahre Rückwärts bis Abstand:", set_distance)
                car.drive(40, -1)
                while distance < set_distance:
                    distance, _ = car.log_and_read_values
                    print_data(car)
                    car.log()
                    time.sleep(.5)
                time.sleep(.5)
                                
                car.steering_angle = random.randint(45,135)
                print("Lenkwinkel:", car.steering_angle)

                set_distance = set_distance + 30
                print("Fahre Rückwärts bis Abstand:", set_distance)
                car.drive(40, -1)
                while distance < set_distance:
                    distance, _ = car.log_and_read_values
                    print_data(car)
                    car.log()
                    time.sleep(.5)
                time.sleep(.5)            
                
                i += 1
           
        elif modus == 5:
            print(modi[modus])
            distance, _ = car.log_and_read_values
            #car.irm.set_references(ref)
            print ("Eingestellte digitale IR-Schwellenwerte:", car.irm._references)
            print('--' * 15)
            """while distance > 7 or distance < 0:
                distance, _ = car.log_and_read_values
                print(car.read_ir_analog)                
                print(car.read_ir_digital)
                print("hell" if car.irm.read_digital()[0] == 0 else "dunkel",\
                        ",hell" if car.irm.read_digital()[1] == 0 else ",dunkel",\
                        ",hell" if car.irm.read_digital()[2] == 0 else ",dunkel",\
                        ",hell" if car.irm.read_digital()[3] == 0 else ",dunkel",\
                        ",hell" if car.irm.read_digital()[4] == 0 else ",dunkel",)
                print("-----")
                car.log()
                time.sleep(.5)"""
            car.drive(45,1)
            follow_line(car, 300, 0.005)
            car.stop()
            print("Auto angehalten")
        
        elif modus == 6:
            print(modi[modus])

            distance, _ = car.log_and_read_values
            print ("Eingestellte digitale IR-Schwellenwerte:", car.irm._references)
            print('--' * 15)
            while distance > 7 or distance < 0:
                distance, _ = car.log_and_read_values
                print(car.read_ir_analog)                
                print(car.read_ir_digital)
                print("hell" if car.irm.read_digital()[0] == 0 else "dunkel",\
                        ",hell" if car.irm.read_digital()[1] == 0 else ",dunkel",\
                        ",hell" if car.irm.read_digital()[2] == 0 else ",dunkel",\
                        ",hell" if car.irm.read_digital()[3] == 0 else ",dunkel",\
                        ",hell" if car.irm.read_digital()[4] == 0 else ",dunkel",)
                print("-----")
                car.log()
                time.sleep(.5)

            car.stop()
            print("Auto angehalten")
        
        elif modus == 7:
            print(modi[modus])
        
        elif modus == 8:
            print(modi[modus])
            car.calibrate_ir()


        elif modus == 0:
            print("Ende")
            quit()
        
        modus = None
        break

    
if __name__ == '__main__':
    
    # Erstellen des Fahrzeuges
    car = SensorCar()
    
    # Ggf. den Timeout des Ultraschallsensors anpassen:
    #car.usm.timeout = 0.06
    #print(car.usm.timeout)

    # Setzen des Modus, wenn er als Argument bei der Dateiausführung mitgegeben wird
    # Ohne Argument kommt das Auswahlmenü
    try:
        modus = sys.argv[1]
    except:
        modus = None

    # Aufrufen der main-function und Übergabe des Farzeuges und des Modus
    main(modus, car)
    
    # Anzeige der Timeout-Einstellung des Ultraschallsensors, falls gesetzt
    #print(car.usm.timeout)
    #print(car.usm.timeout)

    # Zum Programmende alles abschalten/reseten
    car.steering_angle = 90     # Räder gerade stellen
    car.stop()                  # Auto anhalten
    car.usm.stop()              # Ulraschall-Sensor ausschalten    
    
    # PandasDataFrame Daten anzeigen und schreiben
    print(car.df)
    car.write_log_to_db()