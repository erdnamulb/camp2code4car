import sys, os, time
sys.path.append(os.path.dirname(sys.path[0]))
from auto_code import SensorCar 

from datetime import datetime
import numpy as np

    
def line_follow(car: SensorCar, with_distance :bool = False):
    steering_angle = car.steering_angle
    delay = 0.0005
    a_step = 3
    b_step = 10
    c_step = 30
    d_step = 45
    speed_for = 30
    speed_back = 30
    turning_angle = 40
    off_track_count =0
    max_off_track_count =20
    turning_max = 45

    while True:
        lt_status_now = car.irm.read_digital()
        #print(lt_status_now)
        # Winkelberechnung
        if	lt_status_now == [0,0,1,0,0]:
            step = 0	
        elif lt_status_now == [0,1,1,0,0] or lt_status_now == [0,0,1,1,0]:
            step = a_step
        elif lt_status_now == [0,1,0,0,0] or lt_status_now == [0,0,0,1,0]:
            step = b_step
        elif lt_status_now == [1,1,0,0,0] or lt_status_now == [0,0,0,1,1]:
            step = c_step
        elif lt_status_now == [1,0,0,0,0] or lt_status_now == [0,0,0,0,1]:
            step = d_step
        # Richtungsberechnung
        # gerade bleiben
        if	lt_status_now == [0,0,1,0,0]:
            off_track_count = 0
            car.steering_angle= 90
        # Lenkung nach rechts
        elif lt_status_now in ([0,1,1,0,0],[0,1,0,0,0],[1,1,0,0,0],[1,0,0,0,0]):
            off_track_count = 0
            turning_angle = int(90 - step)
        # Lenkung nach links
        elif lt_status_now in ([0,0,1,1,0],[0,0,0,1,0],[0,0,0,1,1],[0,0,0,0,1]):
            off_track_count = 0
            turning_angle = int(90 + step)
        elif lt_status_now == [0,0,0,0,0]:
            off_track_count += 1
            if off_track_count > max_off_track_count:
                car.stop()
                return False


        else:
            off_track_count = 0
    
        car.steering_angle =turning_angle
        time.sleep(delay)  
        

        



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
            sens = car.irm.read_digital()
            print(sens)
            delay = 0.0005
            a_step = 3
            b_step = 10
            c_step = 30
            d_step = 45
            speed_for = 30
            speed_back = 30
            turning_angle = 40
            off_track_count =0
            max_off_track_count =25
            turning_max = 45
            
            
            car.drive(speed_for,1)
            lt_status_now = car.irm.read_digital()
            distance = car.distance
            while distance > 12 or distance < 0:
                distance = car.distance
                lt_status_now = car.irm.read_digital()
                print(lt_status_now)
                # Angle calculate
                if	lt_status_now == [0,0,1,0,0]:
                    step = 0	
                elif lt_status_now == [0,1,1,0,0] or lt_status_now == [0,0,1,1,0]:
                    step = a_step
                elif lt_status_now == [0,1,0,0,0] or lt_status_now == [0,0,0,1,0]:
                    step = b_step
                elif lt_status_now == [1,1,0,0,0] or lt_status_now == [0,0,0,1,1]:
                    step = c_step
                elif lt_status_now == [1,0,0,0,0] or lt_status_now == [0,0,0,0,1]:
                    step = d_step

                # Direction calculate
                if	lt_status_now == [0,0,1,0,0]:
                    off_track_count = 0
                    car.steering_angle= 90
                # turn right
                elif lt_status_now in ([0,1,1,0,0],[0,1,0,0,0],[1,1,0,0,0],[1,0,0,0,0]):
                    off_track_count = 0
                    turning_angle = int(90 - step)
                # turn left
                elif lt_status_now in ([0,0,1,1,0],[0,0,0,1,0],[0,0,0,1,1],[0,0,0,0,1]):
                    off_track_count = 0
                    turning_angle = int(90 + step)
                elif lt_status_now == [0,0,0,0,0]:
                    off_track_count += 1
                    if off_track_count > max_off_track_count:
                        #tmp_angle = -(turning_angle - 90) + 90
                        tmp_angle = (turning_angle-90)/abs(90-turning_angle)
                        tmp_angle *= turning_max
                        car.drive(speed_back,-1)
                        car.steering_angle = tmp_angle

                        while True:
                            lt_status = car.irm.read_digital()
                            if lt_status[2] == 1:
                                break
                        car.stop()

                        car.steering_angle = turning_angle
                        time.sleep(0.2) 
                        car.drive(speed_for,1)
                        time.sleep(0.2)


                else:
                    off_track_count = 0
            
                car.steering_angle =turning_angle
                time.sleep(delay)
                car.log()
            car.stop()
        
        elif modus == 6:
            print(modi[modus])
            car.drive(30,1)
            line_follow(car)
            
        
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
    ref= [28.19,33.345,35,35.01,34.95]
    
    car = SensorCar()
    car.irm.set_references(ref)

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

