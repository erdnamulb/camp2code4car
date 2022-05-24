import sys, time, os
import logging
sys.path.append(os.path.dirname(sys.path[0]))
from auto_code_Allan import CamCar 
 
def drive_time(car: CamCar, speed: int, direction: int, steering_angle: int, duration: int):
    """drive in defined direction for defined time
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
        time.sleep(.2)
        print(f"spped: {car._speed:3}, direction: {car._direction:2}, steering angele: {car.steering_angle:3}, time: {(time.time() - time_start):.2f}")
    car.stop()

def turn_direction(car: CamCar):
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

def avoid_crash(car: CamCar):
    """The function is intended to avoid a crash. 
    By driving backwards for 1s and then driving away for another 2s with full steering angle (left or right).
    The vehicle then continues straight ahead.
    """
    car.stop()
    drive_time(car, speed=car._speed, direction=-1, steering_angle=90, duration=1)
    drive_time(car, speed=car._speed, direction=-1, steering_angle=turn_direction(car), duration=2)
    car.steering_angle = 90
    car.drive(car._speed, 1)

def follow_line(car: CamCar, with_distance :bool = False):
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
    b_step = 25
    c_step = 35
    d_step = 45
    off_track_count_fw = 0
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
        elif ir_data in ([1,0,0,0,0],[0,0,0,0,1],[0,0,1,1,1],[1,1,1,0,0]):
            step = d_step

        # straightforward
        if	ir_data == [0,0,1,0,0]:
            steering_angle = 90
            off_track_count_fw = 0
        # turn right
        elif ir_data in ([0,1,1,0,0],[0,1,0,0,0],[1,1,0,0,0],[1,0,0,0,0],[1,1,1,0,0]):
            steering_angle = int(90 - step)
            off_track_count_fw = 0
        # turn left
        elif ir_data in ([0,0,1,1,0],[0,0,0,1,0],[0,0,0,1,1],[0,0,0,0,1],[0,0,1,1,1]):
            steering_angle = int(90 + step)
            off_track_count_fw = 0
        
        print(f"{ir_data} --> Lenkposition: {steering_angle:3} | Abstand: {distance}")

        # Abstandsüberwachung
        if with_distance:
            if distance < 12 and distance > 0:
                return True # Ende mit Abstandsproblem

        # Prüfen, ob Linie noch da ist
        if ir_data == [0,0,0,0,0]:
            off_track_count_fw += 1
            print(f"off track: {off_track_count_fw}")
            if off_track_count_fw > car.offtrack_fw:
                return False # Ende wegen fehlender Linie
        # Lenken
        car.steering_angle = steering_angle
        time.sleep(car.ir_intervall)


def back_to_line(car: CamCar):
    """Function drives the car back onto the line. 
       The steering is turned in the opposite direction and car drive backwards.
       Until line found in middle or timeout reached
    Returns:
            [int]: returns off_track_count_bw (Timeout) 
                If off_track_count_fw > car.offtrack_bw Programm can be stoped
    """
    # in den entgegengesetzten Lenkanschlag lenken
    if car.steering_angle != 90:
        tmp_angle =(90 - car.steering_angle)/abs(car.steering_angle - 90)
        tmp_angle = tmp_angle * car.angle_bw + 90
        car.steering_angle = tmp_angle
        
    # zurück zur Linie
    off_track_count_bw = 0
    car.drive(car.speed_bw,-1)
    while off_track_count_bw < car.offtrack_bw:
        _, ir_data = car.log_and_read_values
        print(f"{ir_data} --> Off track: {off_track_count_bw}")
        if ir_data[2] == 1:
            break
        off_track_count_bw += 1
        time.sleep(car.ir_intervall*2)
    car.stop()
    if car.steering_angle != 90:
        tmp_angle =(90 - car.steering_angle)/abs(car.steering_angle - 90)
        tmp_angle = tmp_angle * car.angle_fw + 90
        car.steering_angle = tmp_angle
    return off_track_count_bw


def main(modus, car: CamCar):
    """Main Function for Executing the tasks
    Args:
        modus (int): The mode that can be choosen by the user
    """
    print('------ Fahrparcours --------------------')
    modi = {
        1: 'Fahrparcours 1 - Camera line following',
        2: 'Fahrparcours 2 - xxx',
        3: 'Fahrparcours 3 - xxx',
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
            car.drive(30,1)
            
            lane_lines = self.average_slope_intercept(frame, line_segments)
            lane_lines_image = self.display_lines(frame, lane_lines)
            new_angle = self.compute_steering_angle(self, frame, lane_lines)
            self.steering_angle = new_angle
            
            
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
                drive_time(car, speed=40, direction=1, steering_angle=90, duration=1)
                time.sleep(.5)
                print("Einschlagen")
                drive_time(car, speed=40, direction=1, steering_angle=turn_angle, duration=8)
                time.sleep(1)
                print("Zurück")
                drive_time(car, speed=40, direction=-1, steering_angle=turn_angle, duration=8)
                time.sleep(.5)
                print("Rückwärts")
                drive_time(car, speed=40, direction=-1, steering_angle=90, duration=1)
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
        
        elif modus == 5: #'Fahrparcours 5 - Linienverfolgung'
            print(modi[modus])
            car.steering_angle = 90
            car.drive(30,1)
            follow_line(car)
            car.stop()
            car.steering_angle = 90
        
        elif modus == 6: #'Fahrparcours 6 - Erweiterte Linienverfolgung'
            print(modi[modus])
            #Parameter setzen

            car.steering_angle = 90
            while True:
                # Linie folgen
                car.drive(car.speed_fw,1)
                follow_line(car)

                #zurück zur Linie
                off_track_count_bw = back_to_line(car)

                # Abbruch, wenn keine Line gefunden
                if off_track_count_bw >= car.offtrack_bw:
                    break

        
        elif modus == 7:
            print(modi[modus])
            #Parameter setzen

            car.steering_angle = 90
            while True:
                # Linie folgen
                car.drive(car.speed_fw,1)
                distance_fault = follow_line(car, True)

                #warten, bis Hindernis aus dem Weg ist
                car.stop()
                while distance_fault:
                    distance, _ = car.log_and_read_values
                    print(f"wait for distance  > 20: {distance}")
                    if distance > 20:
                        break
                    time.sleep(0.5)

                #zurück zur Linie
                off_track_count_bw = back_to_line(car)

                # Abbruch, wenn keine Line gefunden
                if off_track_count_bw >= car.offtrack_bw:
                    break

        elif modus == 8: #'IR - Sensoren Kalibrieren'
            print(modi[modus])
            car.calibrate_ir()
            

        elif modus == 0: #Ende
            quit()
        
        modus = None
        break

if __name__ == '__main__':
    # car anlegen
    car = CamCar()
        
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

