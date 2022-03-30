import sys, time
from auto_code import SensorCar 

def drive_with_log(car: SensorCar, speed: int, direction: int, steering_angle: int, duration: int):
    """drive in defined direction
    Args:
            speed (int): drive speed
            direction(int): 1 = forward, -1 = backward
            steering_angle(int): direction of travel of the front wheels (90 = straight forward)
            duration(int): time to travel in definded direction
    """
    car.steering_angle = steering_angle
    car.drive(speed,direction)
    time_start = time.time()
    while time.time() - time_start < duration:
        print(f"spped: {car._speed:3}, direction: {car._direction:2}, steering angele: {car.steering_angle:3}, time: {(time.time() - time_start):.2f}")
        time.sleep(.2)
    car.stop()


def turn_direction(car: SensorCar):
    """The function alternately returns the two end stops of the steering
    Returns:
            [int]: returns alternately 45° an 135°
    """
    if car._bool_turn:
        turn_angle = 45
    else:
        turn_angle = 135
    car._bool_turn = not car._bool_turn
    return turn_angle

def avoid_crash(car: SensorCar):
    """The function is intended to avoid a crash. 
    By driving backwards for 1s and then driving away for another 2s with full steering angle (left or right).
    The vehicle then continues straight ahead.
    """
    car.stop()
    drive_with_log(car, speed=car._speed, direction=-1, steering_angle=90, duration=1)
    drive_with_log(car, speed=car._speed, direction=-1, steering_angle=turn_direction(car), duration=2)
    car.steering_angle = 90
    car.drive(car._speed, 1)

def follow_line(car: SensorCar, with_distance :bool = False):
    """Function to follow lines using the IR sensors
    Args:
            with_distance (bool): activates or deactivates distance monitoring
    Returns:
            [bool]: returns reason for aborting. 
                True  = Stop due to obstacle (ultrasonic sensors)
                False = Stop due to lost line (infrared sensors)
    """
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
                return False # Ende ohne Abstandsproblem
        # Lenken
        car.steering_angle = steering_angle
        time.sleep(.01)

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

        if modus == 1: #'Fahrparcours 1 - Vorwärts und Rückwärts'
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

        elif modus == 2: #'Fahrparcours 2 - Kreisfahrt mit max. Lenkwinkel'
            print(modi[modus])
            loop_count = 0
            while loop_count < 2:
                if loop_count == 0:
                    print("--- Uhrzeigersinn ---")
                    turn_angle = 130
                else:
                    print("--- gegehn Uhrzeigersinn ---")
                    turn_angle = 50

                print("vorwärts")
                drive_with_log(car, speed=40, direction=1, steering_angle=90, duration=1)
                time.sleep(.5)
                print("Einschlagen")
                drive_with_log(car, speed=40, direction=1, steering_angle=turn_angle, duration=8)
                time.sleep(1)
                print("Zurück")
                drive_with_log(car, speed=40, direction=-1, steering_angle=turn_angle, duration=8)
                time.sleep(.5)
                print("Rückwärts")
                drive_with_log(car, speed=40, direction=-1, steering_angle=90, duration=1)
                loop_count += 1


        elif modus == 3: #'Fahrparcours 3 - Vorwärtsfahrt bis Hindernis'
            print(modi[modus])
            distance, _ = car.log_and_read_values
            car.drive(40,1)
            while distance > 7 or distance < 0:
                distance, _ = car.log_and_read_values
                print(f"distance: {distance}")
                time.sleep(.3)
            car.stop()

        elif modus == 4: #'Fahrparcours 4 - Erkundungstour'
            print(modi[modus])
            loop_count = 0
            while loop_count < 4:
                car.steering_angle = 90
                car.drive(40,1)
                distance, _ = car.log_and_read_values
                while distance > 12 or distance < 0:
                    distance, _ = car.log_and_read_values
                    print(f"distance {distance}")
                    time.sleep(.3)
                avoid_crash(car)
                loop_count += 1
            car.stop()
        
        elif modus == 8: #'IR - Sensoren Kalibrieren'
            print(modi[modus])
            car.calibrate_ir()
            while True:
                print(f"Digital: {car.read_ir_digital} Analog: {car.read_ir_analog}")
                time.sleep(.5)

        elif modus == 0: #Ende
            quit()
        
        modus = None
        break

if __name__ == '__main__':
    # car anlegen
    car = SensorCar()
    
    # ggf. Inputs übernehmen
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


