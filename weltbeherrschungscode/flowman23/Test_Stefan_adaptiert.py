import sys, os, time
sys.path.append(os.path.dirname(sys.path[0]))
from auto_code import SensorCar 

from datetime import datetime
import numpy as np

def wait_with_angle(car: SensorCar, waitTime: float, angle: int):
    """Function to drive with minimal steering changes over a given time 
    """
    now = 0
    while now < waitTime:
        car.steering_angle = angle
        time.sleep(.25)
        if angle > 90:
            offset = -5
        else:
            offset = 5
        car.steering_angle = angle + offset
        time.sleep(.25)

        now += .5
        print(f"time= {now:.1f} set_angle = {angle}")

def turn_direction(car: SensorCar):
    """The function alternately returns the two end stops of the steering
    """
    if car._bool_turn:
        angle = 45
    else:
        angle = 135
    car._bool_turn = not car._bool_turn
    return angle

def avoid_crash(car: SensorCar):
    """The function is intended to avoid a crash. 
    By driving backwards for 1s and then driving away for another 2s with full steering angle (left or right).
    The vehicle then continues straight ahead.
    """
    car.stop()
    time.sleep(.5)
    car.drive(car._speed,-1)
    time.sleep(1)
    car.steering_angle = turn_direction(car)
    time.sleep(2)
    car.stop()
    time.sleep(.5)
    car.steering_angle = 90
    car.drive(car._speed, 1)

def follow_line_anbalog(car: SensorCar, line_value: int):
    car.steering_angle = 90
    while True:
        # Sensoren auswerten
        _, ir_data = car.log_and_read_values
        np_ir_data = np.array(ir_data)
        min_pos = np.where(np_ir_data == np.min(np_ir_data))[0][0]
        print(f"{ir_data} --> Lenkposition: {min_pos}")
        # Prüfen, ob Linie noch da ist
        line_found = False
        for ir in ir_data:
            if ir < line_value:
                line_found = True
        if not line_found:
            break # Schleife beenden
        # Lenken
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

def follow_line(car: SensorCar, with_distance :bool = False):
    steering_angle = car.steering_angle
    a_step = 5
    b_step = 15
    c_step = 30
    d_step = 45
    off_track_count = 0
    while True:
        # Sensoren auswerten
        distance, ir_data = car.log_and_read_values
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
            off_track_count = 0
        # turn right
        elif ir_data in ([0,1,1,0,0],[0,1,0,0,0],[1,1,0,0,0],[1,0,0,0,0]):
            steering_angle = int(90 - step)
            off_track_count = 0
        # turn left
        elif ir_data in ([0,0,1,1,0],[0,0,0,1,0],[0,0,0,1,1],[0,0,0,0,1]):
            steering_angle = int(90 + step)
            off_track_count = 0
        
        print(f"{ir_data} --> Lenkposition: {steering_angle:3} | Abstand: {distance}")

        # Abstandsüberwachung
        if with_distance:
            if distance < 12 and distance > 0:
                return True # Ende mit Abstandsproblem

        # Prüfen, ob Linie noch da ist
        if ir_data == [0,0,0,0,0]:
            off_track_count += 1
            print(f"off track: {off_track_count}")
            if off_track_count > 10:
                return False # Schleifenende ohne Abstandsproblem
        # Lenken
        car.steering_angle = steering_angle
        time.sleep(.005)


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
        8: 'IR - Sensoren Kalibrieren',
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
            wait_with_angle(10, 135)
            car.stop()
            car.steering_angle = 90
            time.sleep(1)
            print("Zurück")
            car.steering_angle = 135
            time.sleep(.3)
            car.drive(40,-1)
            wait_with_angle(10, 135)
            car.stop()
            time.sleep(.5)
            print("Rückwärts")
            car.steering_angle = 90
            car.drive(30,-1)
            time.sleep(1)
            car.stop()
            

        elif modus == 3:
            print(modi[modus])
            distance, _ = car.log_and_read_values
            car.drive(40,1)
            while distance > 7 or distance < 0:
                distance, _ = car.log_and_read_values
                print(distance)
                time.sleep(.3)
            car.stop()

        elif modus == 4:
            print(modi[modus])
            loop_count = 0
            while loop_count < 2:
                car.steering_angle = 90
                car.drive(40,1)
                distance, _ = car.log_and_read_values
                while distance > 12 or distance < 0:
                    distance, _ = car.log_and_read_values
                    print(f"{distance} , {car.steering_angle}")
                    time.sleep(.3)
                avoid_crash(car)
                print(f"bool= {car._bool_turn}")
                loop_count += 1
            car.stop()
        
        elif modus == 5:
            print(modi[modus])
            car.steering_angle = 90
            car.drive(40,1)
            follow_line(car)
            car.stop()
            car.steering_angle = 90
        
        elif modus == 6:
            print(modi[modus])
            speed = 50
            car.steering_angle = 90
            while True:
                car.drive(speed,1)
                follow_line(car)
                # neuer lenkwinkel
                if car.steering_angle != 90:
                    tmp_angle =(90 - car.steering_angle)/abs(car.steering_angle - 90)
                    tmp_angle = tmp_angle * 45 + 90
                    car.steering_angle = tmp_angle
                off_track_count = 0
                car.drive(speed,-1)
                while off_track_count < 30:
                    _, ir_data = car.log_and_read_values
                    print(f"{ir_data} --> Off track: {off_track_count}")
                    if ir_data in ([0,1,1,0,0],[0,0,1,0,0],[0,0,1,1,0]):
                        break
                    off_track_count += 1
                    time.sleep(0.01)
                car.stop()
                car.steering_angle = 90
                if off_track_count >= 30:
                    break
        
        elif modus == 7:
            print(modi[modus])
            speed = 30
            car.steering_angle = 90
            while True:
                car.drive(speed,1)
                distance_fault = follow_line(car, True)
                car.stop()

                #warten, bis Hindernis aus dem Weg ist
                while distance_fault:
                    distance, _ = car.log_and_read_values
                    print(f"wait for distance  > 20: {distance}")
                    if distance > 20:
                        break
                    time.sleep(0.5)

                # neuer lenkwinkel
                if car.steering_angle != 90:
                    tmp_angle =(90 - car.steering_angle)/abs(car.steering_angle - 90)
                    tmp_angle = tmp_angle * 45 + 90
                    car.steering_angle = tmp_angle
                # zurück zur Linie
                car.drive(speed,-1)
                off_track_count = 0
                while off_track_count < 30:
                    _, ir_data = car.log_and_read_values
                    print(f"{ir_data} --> Off track: {off_track_count}")
                    if ir_data in ([0,1,1,0,0],[0,0,1,0,0],[0,0,1,1,0]):
                        break
                    off_track_count += 1
                    time.sleep(0.01)
                car.stop()
                car.steering_angle = 90
                if off_track_count >= 30:
                    break



        elif modus == 8:
            print(modi[modus])
            car.calibrate_ir()
            while True:
                print(f"Digital: {car.read_ir_digital} Analog: {car.read_ir_analog}")
                time.sleep(.5)


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
    #print(car.df)
