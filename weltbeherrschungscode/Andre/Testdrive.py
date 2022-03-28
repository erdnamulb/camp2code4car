import sys, os, time
sys.path.append(os.path.dirname(sys.path[0]))
from auto_code import SensorCar 

from datetime import datetime
import numpy as np


def main(modus, car: SensorCar):
    """Main Function for Executing the tasks


    Args:
        modus (int): The mode that can be choosen by the user
    """
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
        print('Auswahl:')
        for m in modi.keys():
            print('{i} - {name}'.format(i=m, name=modi[m]))
        print('--' * 20)

    while True:

        while modus == None:
            modus = input("Wähle  (Abbruch mit '0'): ? ")
            if modus in ['1', '2', '3', '4', '5', '6', '7', '8', '0']:
                break
            else:
                modus = None
                print('Getroffene Auswahl nicht möglich.')
                #quit()
        modus = int(modus)

        if modus == 1:
            print(modi[modus])
            car.steering_angle = 90
            print("vorwärts")
            car.drive(30,1)
            time.sleep(3)
            print("stopp")
            car.stop()
            time.sleep(1)
            print("rückwärts")
            car.drive(30,-1)
            time.sleep(3)
            print("stopp")
            car.stop()

        elif modus == 2:
            print(modi[modus])
            car.steering_angle = 90
            time.sleep(.3)
            print("vorwärts")
            car.drive(40,1)
            time.sleep(1)
            car.stop()
            time.sleep(.5)
            print("Uhrzeigersinn")
            car.steering_angle = 135
            time.sleep(.3)
            car.drive(40,1)
            car.wait_angle(10, 135)
            car.stop()
            car.steering_angle = 90
            time.sleep(1)
            print("Zurück")
            car.steering_angle = 135
            time.sleep(.3)
            car.drive(40,-1)
            car.wait_angle(10, 135)
            car.stop()
            time.sleep(.5)
            print("Rückwärts")
            car.steering_angle = 90
            car.drive(30,-1)
            time.sleep(1)
            car.stop()
            

        elif modus == 3:
            print(modi[modus])
            distance = car.distance
            car.drive(40,1)
            while distance > 7 or distance < 0:
                distance = car.distance
                car.log()
                print(distance)
                time.sleep(.3)
            car.stop()

        elif modus == 4:
            print(modi[modus])
            loop_count = 0
            while loop_count < 2:
                car.steering_angle = 90
                car.drive(40,1)
                distance = car.distance
                while distance > 12 or distance < 0:
                    distance = car.distance
                    print(f"{distance} , {car.steering_angle}")
                    car.log()
                    time.sleep(.3)
                car.avoid_crash()
                loop_count += 1
            car.stop()
        
        elif modus == 5:
            print(modi[modus])
            high_value = 140
            line_value = 100
            car.steering_angle = 90
            #print(car.get_average(50))
            #car.cali_references()
            while True:
                ir_data = car.read_analog()
                print(f"{ir_data}")
                # Prüfen, ob Linie noch da ist
                line_found = False
                for ir in ir_data:
                    if ir < line_value:
                        line_found = True
                        time_start = 0
                if not line_found:
                    if time_start == 0:
                        time_start = datetime.timestamp(datetime.now())
                    time_now = datetime.timestamp(datetime.now())
                    print(time_now - time_start)
                    if time_now - time_start < 2:
                        ir_data = car.read_analog()
                        for ir in ir_data:
                            if ir < line_value: #line found
                                time_start = 0
                        time.sleep(.1)
                        continue
                    car.steering_angle = 90
                    car.stop()
                    break
                # Lenken
                analog = np.array(ir_data)
                min_ir = np.min(analog)
                min_pos = np.where(analog == min_ir)[0][0]
                print(f"min = {min_ir} Position: {min_pos}")
                if min_pos == 0:
                    car.steering_angle = 45
                    car.drive(30,1)
                elif min_pos == 1:
                    car.steering_angle = 65
                    car.drive(35,1)
                elif min_pos == 2:
                    car.steering_angle = 90
                    car.drive(40,1)
                elif min_pos == 3:
                    car.steering_angle = 115
                    car.drive(35,1)
                elif min_pos == 4:
                    car.steering_angle = 135
                    car.drive(30,1)
                time.sleep(.1)
        
        elif modus == 6:
            print(modi[modus])
        
        elif modus == 7:
            print(modi[modus])

        elif modus == 8:
            #print(modi[modus])
            run_loop = True
            while run_loop:
                for a in range(45, 136, 5):
                    time.sleep(.1)
                    car.steering_angle = a
                    print(f"angle : {car.steering_angle}")
                for a in range(135, 44, -5):
                    time.sleep(.1)
                    car.steering_angle = a
                    print(f"angle : {car.steering_angle}")
                run_loop = True
        
        elif modus == 0:
            print("Ende")
            quit()
        
        modus = None
        break

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

