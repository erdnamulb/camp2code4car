import sys, time, os
sys.path.append(os.path.dirname(sys.path[0]))
from auto_code import CamCar 
import cv2

def follow_road(car: CamCar, with_distance :bool = False):
    """Function to follow lines using the IR sensors
    Args:
            with_distance (bool): activates or deactivates distance monitoring
    Returns:
            [bool]: returns reason for aborting. 
                True  = Stop due to obstacle (ultrasonic sensors)
                False = Stop due to lost line (infrared sensors)
    """
    
    while True:
        # Lenkwinkel berechnen lassen
        steering_angle, frame, lane_lines = car.get_steering_angle_from_cam()


        """# Abstandsüberwachung
        if with_distance:
            if distance < 12 and distance > 0:
                return True # Ende mit Abstandsproblem"""

        # Lenken
        car.steering_angle = steering_angle

        # Display des Frames
        frame_with_lane_lines = car.lane_lines_on_frame(frame, lane_lines)
        cv2.imshow("Display window (press q to quit)", frame_with_lane_lines)
        # Ende bei Drücken der Taste q
        if cv2.waitKey(1) == ord('q'):
            break
        
        #time.sleep(car.ir_intervall)
        
    cv2.destroyAllWindows()


def main(modus, car: CamCar):
    """Main Function for Executing the tasks
    Args:
        modus (int): The mode that can be choosen by the user
    """
    print('------ Fahrparcours --------------------')
    modi = {
        1: 'Modus 1 - Fahrbahnerkennung mit OpenCV',
        2: 'Modus 2 - Fahrbahnerkennung mit Tensorflow',
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
            if modus in ['1', '2', '0']:
                break
            else:
                modus = None
                print('Getroffene Auswahl nicht möglich.')
                #quit()
        modus = int(modus)

        if modus == 1: #'Modus 1 - Fahrbahnerkennung mit OpenCV'
            pass

        elif modus == 2: #'Modus 2 - Fahrbahnerkennung mit Tensorflow'
            pass          

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

    #main(modus, car)
    car.drive(20,1)
    follow_road(car)

    car.stop()
    car.usm.stop()
    car.release_cam()
    # Dataframe in DB schreiben
    car.write_log_to_db()
    #print(car.df)


