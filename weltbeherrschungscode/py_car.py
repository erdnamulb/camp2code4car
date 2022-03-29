import sys, os, time
from auto_code import SensorCar 

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

