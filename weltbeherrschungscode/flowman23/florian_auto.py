import sys, os, time
sys.path.append(os.path.dirname(sys.path[0]))

# hier kommen die drei Car Klassen her
from auto_code import SensorCar


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
    ref = [65.85, 73.55, 76.58, 77.595, 84.835]

    print('------ Fahrparcours --------------------')
    modi = {
        1: 'Fahrparcours 1 - Vorwärts und Rückwärts',
        2: 'Fahrparcours 2 - Kreisfahrt mit max. Lenkwinkel',
        3: 'Fahrparcours 3 - Vorwärtsfahrt bis Hindernis',
        4: 'Fahrparcours 4 - Erkundungstour',
        5: 'Fahrparcours 5 - Linienverfolgung',
        6: 'Fahrparcours 6 - Erweiterte Linienverfolgung',
        7: 'Fahrparcours 7 - 6. + Hinderniserkennung',
        0: 'Ende'
    }

    if modus == None:
        print('--' * 20)
        print('Auswahl:')
        for m in modi.keys():
            print('{i} - {name}'.format(i=m, name=modi[m]))
        print('--' * 20)

    while True:

        while modus == None:
            modus = input('Wähle  (Andere Taste für Abbruch): ? ')
            if modus in ['1', '2', '3', '4', '5', '6', '7', '0']:
                break
            else:
                modus = None
                print('Getroffene Auswahl nicht möglich.')
                #quit()
        modus = int(modus)

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
            car.drive(20,1)
            distance = car.distance
            while distance > 7 or distance < 0:
                distance = car.distance
                print_data(car)
                car.log()
                time.sleep(.3)
            car.stop()
            print("Auto angehalten")
       
        elif modus == 4:
            print(modi[modus])
            
            i=0
            while i < 2:
                print(i)
                print("Los geht's")
                car.drive(20,1)
                distance = car.distance
                while distance > 7 or distance < 0:
                    distance = car.distance
                    print_data(car)
                    car.log()
                    time.sleep(.5)
                print("Auto angehalten")
                car.stop()
                time.sleep(1.0)

                print("Retour")
                car.drive(20, -1)
                while distance < 20:
                    distance = car.distance
                    print_data(car)
                    car.log()
                    time.sleep(.5)
                time.sleep(0.5)
                
                print("links lenken")
                car.steering_angle = 70
                
                print("Retour")
                car.drive(20, -1)
                while distance < 70:
                    distance = car.distance
                    print_data(car)
                    car.log()
                    time.sleep(.5)
                time.sleep(.5)            
                
                i += 1
           
        elif modus == 5:
            print(modi[modus])
            distance = car.distance
            car.irm.set_references(ref)
            print ("Eingestellte digitale IR-Schwellenwerte:", car.irm._references)
            while distance > 7 or distance < 0:
                distance = car.distance
                print(car.read_ir_sensors)                
                print(car.irm.read_digital())
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
        
        elif modus == 6:
            print(modi[modus])
        
        elif modus == 7:
            print(modi[modus])
        
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