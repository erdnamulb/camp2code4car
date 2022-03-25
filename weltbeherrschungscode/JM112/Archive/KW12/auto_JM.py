import sys
import os
from turtle import distance, speed
import loggingc2c as log


#Pfad für den Import der basisklassen
pfad = sys.path[0]
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(pfad)), "camp2code-project_phase_1", "Code"))
from basisklassen import *


#Objekte der Basisklassen
#bw = Back_Wheels()
#fw = Front_Wheels()
#usm = Ultrasonic()
#irm = Infrared()


class BaseCar():

    """Entwicklung und Testen einer Klasse BaseCar mittels der Basisklassen
        mit vorgegebenen Anforderungen. Die Klasse soll folgende Attribute (mit entsprechen-
        den Gettern und Settern) und Methoden haben:
        • steering_angle: Zugriff auf den Lenkwinkel
        • drive(int, int): Fahren mit übergebener Geschwindigkeit und Fahrrichtung
        • stop(): Anhalten des Autos
        • speed: Zugriff auf die Geschwindigkeit
        • direction: Zugriff auf die Fahrrichtung (1: vorwärts, 0: Stillstand, -1 Rückwärts)
        Die Klasse BaseCar soll mittels folgenden Aufgaben getestet werden."""

    def __init__(self):
        self._speed = 0
        self._direction = 1
        self._steering_angle = 90
        self.fw = Front_Wheels()
        self.bw = Back_Wheels()
        self.usm = Ultrasonic()
        self.irm = Infrared()
        
        

    @property
    def steering_angle(self):
        return self._steering_angle

    @steering_angle.setter
    def steering_angle(self, angle):
        self._steering_angle = angle
        self.fw.turn(angle)

    @property
    def speed(self):
        return self._speed

    @speed.setter
    def speed(self, speed):
        self._speed = speed

    @property
    def direction(self):
        return self._direction

    @direction.setter
    def direction(self, direction): 
        self._direction = direction

    def drive(self, speed_value, direction):
        self.speed = speed_value
        self.bw.speed = speed_value
        if direction == 1:
            self._direction = 1
            self.bw.forward()
        elif direction == -1:
            self._direction = -1
            self.bw.backward()
        else: 
            self._direction = 0
            self.stop()
    
    def stop(self):
            self.bw.stop()


class SonicCar(BaseCar):

    def __init__(self):
        super().__init__()
        self._distance = 0

    @property
    def distance(self):
        self._distance = self.usm.distance()
        return self._distance

    #def datalogger():
        #df_log = log.add_row_df(df_db, self.distance, [0, 0, 0, 0, 0], self.speed, self.direction, self.steering_angle)









    
#Hauptprogramm
@click.command()
@click.option('--modus', '--m', type=int, default=None, help="Startet Test für Klasse direkt.")
def main(modus):

    car = BaseCar()
    scar = SonicCar()

    #db_w_path = f"{sys.path[0]}/JM.sqlite" #Pfadrückgabe: /home/pi/git/camp2code4car/weltbeherrschungscode/JM112/JM.sqlite
    #log.makedatabase_multitable(db_w_path)

    #DB singletable anlegen
    db_w_path_single = f"{sys.path[0]}/JMsingle.sqlite"
    log.makedatabase_singletable(db_w_path_single)

    #Pandas Dataframe
    df_db = log.init_dataframe()

    def f_vorwärts():
        while True:
            if scar.distance >= 12 or scar.distance < 0:
                pass
            else:
                scar.stop()
                print("Hindernis")
                break
        



    print('-- Auswahl Fahrparcours --------------------')
    modi = {
        0: 'Frei',
        1: 'Fahrparcours 1 - Vorwärts und Rückwärts',
        2: 'Fahrparcours 2 - Kreisfahrt mit maximalem Lenkwinkel',
        3: 'Fahrparcours 3 - Vorwärtsfahrt bis Hindernis',
        4: 'Fahrparcours 4 - Erkundungstour',
        5: 'Fahrparcours 5 - Linienverfolgung',
        6: 'Fahrparcours 6 - Erweiterte Linienverfolgung',
        7: 'Fahrparcours 7 - Erweiterte Linienverfolgung mit Hindernisserkennung',
    }

    if modus == None:
        print('--' * 20)
        print('Auswahl:')
        for m in modi.keys():
            print('{i} - {name}'.format(i=m, name=modi[m]))
        print('--' * 20)

    while modus == None:
        modus = input('Wähle  (Andere Taste für Abbruch): ? ')
        if modus in ['0', '1', '2', '3', '4', '5', '6', '7']:
            break
        else:
            modus = None
            print('Getroffene Auswahl nicht möglich.')
            quit()
    modus = int(modus)

    if modus == 1:
        print("Fahrparcours 1 - Vorwärts und Rückwärts")
        car.drive(30, 1)
        time.sleep(3)
        car.stop()
        time.sleep(1)
        car.drive(50, -1)
        time.sleep(3)
        car.stop()
        print("Fahrparcours 1 - beendet")
        

    elif modus == 2:
        print('Fahrparcours 2 - Kreisfahrt mit maximalem Lenkwinkel')
        car.steering_angle = 90
        car.drive(30, 1)
        time.sleep(1)
        car.steering_angle = 135
        time.sleep(8)
        car.stop()
        car.drive(30, -1)
        time.sleep(8)
        car.steering_angle = 90
        car.drive(30, -1)
        time.sleep(1)
        car.stop()
        #entgegengesetzter Uhrzeigersinn
        car.steering_angle = 90
        car.drive(30, -1)
        time.sleep(1)
        car.steering_angle = 135
        time.sleep(8)
        car.stop()
        car.drive(30, 1)
        time.sleep(8)
        car.steering_angle = 90
        car.drive(30, 1)
        time.sleep(1)
        car.stop()

    elif modus == 3:
        print('Test Ultrasonic')
        scar.drive(50, 1)
        while True:
            if scar.distance >= 7 or scar.distance < 0:
                db_distance = scar.distance
                db_speed = scar.speed
                db_direction = scar.speed
                db_steering_angle = scar.steering_angle
                #log.add_data(db_w_path_single,db_distance, 0, 0, 0, 0, 0, db_speed, db_direction, db_steering_angle)
                df_db = log.add_row_df(df_db, db_distance, [0, 0, 0, 0, 0], db_speed, db_direction, db_steering_angle)
                print(df_db)
                print("-" * 20)
                time.sleep(0.5)
            else:
                scar.stop()
                print("Hindernis")
                conn = log.create_connection(db_w_path_single)
                df_db.to_sql('drivedata', conn, if_exists = 'append', index = False)
                break
        print(df_db)

    elif modus == 4: #Leider ohne coolen Datenlogger :(
        print('Erkundungstour')
        i = 0
        while i <= 3:
            scar.drive(30, 1)
            if scar.distance >= 12 or scar.distance < 0:
                df_db = log.add_row_df(df_db, scar.distance, [0, 0, 0, 0, 0], scar.speed, scar.direction, scar.steering_angle)
                time.sleep(0.5)
                print("if1")
            else:
                scar.stop()
                print("Hindernis")
                df_db = log.add_row_df(df_db, scar.distance, [0, 0, 0, 0, 0], scar.speed, scar.direction, scar.steering_angle)
                car.steering_angle = 55
                while scar.distance < 250:
                    scar.drive(25, -1)
                    df_db = log.add_row_df(df_db, scar.distance, [0, 0, 0, 0, 0], scar.speed, scar.direction, scar.steering_angle)
                    time.sleep(0.5)
                i += 1
        scar.stop()
        print("Erkundungstour beendet")
        conn = log.create_connection(db_w_path_single)
        df_db.to_sql('drivedata', conn, if_exists = 'append', index = False)
        print("Daten in DB")





if __name__ == '__main__':
    main()


    



