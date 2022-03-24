import sys
from turtle import speed 
import click
import datetime as dt
import os

sys.path.append('/home/pi/Projektphase1/camp2code4car/camp2code-project_phase_1/Code')
from basisklassen import *
sys.path.append('/home/pi/Projektphase1/camp2code4car/camp2code-project_phase_1/weltbeherrschungscode/Allan')
import loggingc2c as db 


db.makedatabase(f"{sys.path[0]}/AllanDB.db")
pfad_db = f"{sys.path[0]}/AllanDB.db"

class BaseCar():
    
    def __init__(self):
        self.bw = Back_Wheels()
        self.fw = Front_Wheels()
        self.usm = Ultrasonic()
        self.irm = Infrared()
        self._steering_angle = 90
        self._speed = 0
        self._direction = 0
        
    @property
    def speed(self):
        return self._speed
        
    @property
    def direction(self):
        return self._direction

    @property
    def steering_angle(self):
        return self._steering_angle

    @steering_angle.setter
    def steering_angle(self, angle):
        self._steering_angle = angle
        self.fw.turn(angle)

    def stop(self):
        self.bw.stop()
    
    def drive(self, speed: int, direction: int):
        self._direction = direction
        if direction == 1: #vorwärts
            self.bw.forward()
        elif direction == -1: #rückwärts
            self.bw.backward()
        else: # alles andere = stop
            self.stop()

        self._speed = speed
        self.bw.speed = speed

car = BaseCar()

class SonicCar(BaseCar):
    def __init__(self):
        super().__init__()
        self._distance = 0

    @property
    def distance(self):
        self._distance = self.usm.distance()
        return self._distance


Sonic = SonicCar()

def hindernisumfahren():
    car.steering_angle = -135
    car.drive(40, -1)
    time.sleep(3)
    car.stop()
    car.steering_angle = 90
    car.drive(40, 1)

    


@click.command()
@click.option('--modus', '--m', type=int, default=None, help="Startet Test für Klasse direkt.")
def main(modus):
    
    print('Abarbeitung Aufgaben')
    modi = {
        0: 'Abbruch',
        1: 'Fahrpacour 1',
        2: 'Fahrpacour 2',
        3: 'SonicCar',
        4: 'Fahrpacour 3',
        5: 'Fahrpacour 4',
        6: 'Befehle testen'
    }

    if modus == None:
        print('--' * 20)
        print('Auswahl:')
        for m in modi.keys():
            print('{i} - {name}'.format(i=m, name=modi[m]))
        print('--' * 20)

    while modus == None:
        modus = input('Wähle  (Andere Taste für Abbruch): ? ')
        if modus in ['0', '1', '2', '3', '4', '5', '6']:
            break
        else:
            modus = None
            print('Getroffene Auswahl nicht möglich.')
            quit()
    modus = int(modus)

    if modus == 0:
        print('Programm wird abgebrochen')
        

    if modus == 1:
        x = input('ACHTUNG! Das Auto wird ein Stück fahren!\n Dücken Sie ENTER zum Start.')
        print('Abfolge Fahrparcour1')
        if x == '':
            car.drive(50,1)
            time.sleep(3)
            car.drive(50,-1)
            time.sleep(3)
            car.stop()
        else:
            print('Abruch.')

    if modus == 2:
        x = input('ACHTUNG! Das Auto wird ein Stück fahren!\n Dücken Sie ENTER zum Start.')
        print('Abfolge Fahrparcour1')
        if x == '':
            car.drive(50, 1)
            time.sleep(1)
            car.stop()
            time.sleep(1)
            car.steering_angle = 135
            car.drive(50, 1)
            time.sleep(8)
            car.stop()
            car.steering_angle = 90
        else:
            print('Abruch.')


    if modus == 3:
        x = input('ACHTUNG! Das Auto wird fahren. Dücken Sie ENTER zum Start.')
        print('Test SonyCar')
        if x == '':
            distance = Sonic.distance
            car.drive(40,1)
            while distance > 7 or distance < 0:
                distance = Sonic.distance
                time.sleep(.1)
                print("Entferneung zum nächsten Hindernis:", distance,"cm")
                db.add_usm(pfad_db, distance)
                print("Aktuelle Geschwindigkeit:", car.speed,"cm/sek")
                db.add_driving(pfad_db, car.speed, car.direction)
                print("Aktueller Lenkeinschlag:", car.steering_angle)
                db.add_steering(pfad_db, car.steering_angle)
            car.stop()
            car.usm.stop
        else:
            print('Abruch.')

    if modus == 4:
        x = input('ACHTUNG! Das Auto wird fahren. Dücken Sie ENTER zum Start.')
        print('Fahrparcour 3')
        if x == '':
            distance = Sonic.distance
            car.drive(40,1)
            while distance > 7 or distance < 0:
                distance = Sonic.distance
                time.sleep(.1)
                print("Entferneung zum nächsten Hindernis:", distance,"cm")
                db.add_usm(pfad_db, distance)
                print("Aktuelle Geschwindigkeit:", car.speed,"cm/sek")
                db.add_driving(pfad_db, car.speed, car.direction)
                print("Aktueller Lenkeinschlag:", car.steering_angle)
                db.add_steering(pfad_db, car.steering_angle)
            car.stop()
            car.usm.stop
        else:
            print('Abruch.')  

    if modus == 5:
        x = input('ACHTUNG! Das Auto wird fahren. Dücken Sie ENTER zum Start.')
        print('Fahrparcour 4')
        if x == '':
            distance = Sonic.distance
            car.drive(40,1)
            while distance > 7 or distance < 0:
                distance = Sonic.distance
                time.sleep(.1)
                print("Entferneung zum nächsten Hindernis:", distance,"cm")
                db.add_usm(pfad_db, distance)
                print("Aktuelle Geschwindigkeit:", car.speed,"cm/sek")
                db.add_driving(pfad_db, car.speed, car.direction)
                print("Aktueller Lenkeinschlag:", car.steering_angle)
                db.add_steering(pfad_db, car.steering_angle)
            car.stop()
            hindernisumfahren()
            car.usm.stop
        else:
            print('Abruch.') 



if __name__ == '__main__':
    main()

