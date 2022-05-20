import basisklassen
import numpy as np
from curses.ascii import isdigit
from datetime import datetime
import os, json, time


fp_allowed = False

STEERINGE_ANGLE_MAX = 45
IR_MARK = 0.7

IR_NO_LINE = 100
IR_INVALID = 101


class Datenlogger:
    """Datenlogger Klasse
    speichert übergebene Listen mit Angabe der Zeit ab Start der Aufzeichnung in ein json-File
    """

    def __init__(self, log_file_path=None):
        """Zielverzeichnis fuer Logfiles kann beim Init mit uebergeben werden
            Wenn der Ordner nicht existiert wird er erzeugt

        Args:
            log_file_path (_type_, optional): Angabe des Zielordners. Defaults to None.
        """
        self._log_file = {}
        self._log_data = []
        self._start_timestamp = 0
        self._logger_running = False
        self._log_file_path = log_file_path

    def start(self):
        """starten des Loggers"""
        print("Logger gestartet")
        self._logger_running = True
        self._start_timestamp = time.time()
        self._log_file["start"] = str(datetime.now()).partition(".")[0]

    def append(self, data):
        """Daten an den Logger senden

        Args:
            data (list): ein Element (Liste) wird an den Logger uebergeben
        """
        if self._logger_running:
            ts = round((time.time() - self._start_timestamp), 2)
            self._log_data.append([ts] + data)

    def save(self):
        """speichert die uebergebenen Daten"""
        if self._logger_running and (len(self._log_data) > 0):
            self._logger_running = False
            self._log_file["data"] = self._log_data
            filename = self._log_file.get("start").partition(".")[0]
            filename = (
                filename.replace("-", "").replace(":", "").replace(" ", "_")
                + "_drive.log"
            )
            if self._log_file_path != None:
                logfile = os.path.join(self._log_file_path, filename)
                if not os.path.isdir(self._log_file_path):
                    os.mkdir(self._log_file_path)
            else:
                logfile = filename
            with open(logfile, "w") as f:
                json.dump(self._log_data, f)
            self._log_file.clear()
            self._log_data.clear()
            print("Log-File saved to:", logfile)


class BaseCar:
    """Class BaseCar als Basis desq Projekts
    Grundfunktionen Antrieb und Lenkung des PiCar
    Einbinden des Datenloggers
    """

    def __init__(self):
        self._steering_angle = 0
        self._speed = 0
        self._direction = 1
        data = {}
        try:
            with open("config.json", "r") as f:
                data = json.load(f)
        except FileNotFoundError:
            with open("config.json", "w") as f:
                data = {}
                data["turning_offset"] = 0
                data["forward_A"] = 0
                data["forward_B"] = 0
                data["log_file_path"] = "Logger"
                json.dump(data, f)
            print("Bitte config.json anpassen!")

        turning_offset = data.get("turning_offset")
        forward_A = data.get("forward_A")
        forward_B = data.get("forward_B")
        self._log_file_path = data.get("log_file_path")
        if self._log_file_path == None:
            self._log_file_path = "Logger"

        self.fw = basisklassen.Front_Wheels(turning_offset=turning_offset)
        self.bw = basisklassen.Back_Wheels(forward_A=forward_A, forward_B=forward_B)
        self._dl = Datenlogger(log_file_path=self._log_file_path)

    def welcome(self):
        time.sleep(0.2)
        self.steering_angle = -45
        time.sleep(0.4)
        self.steering_angle = 45
        time.sleep(0.4)
        self.steering_angle = 0

    def logger_start(self):
        """startet die Aufzeichnung des Log-Files"""
        self._dl.start()

    def logger_log(self, data):
        """Fügt der Aufzeichnung des Datenloggers Daten in Form einer Liste an

        Args:
            data (list): Liste mit Elementen die gelogged werden sollen
        """
        self._dl.append(data)

    def logger_save(self):
        """speichert die Daten die der Logger empfangen hat"""
        self._dl.save()

    def start_parcours(self, number):
        """Startet einen Fahrparcours
            Der Datenlogger wird automatisch gestartet und nach Ende des Parcours gespeichert

        Args:
            number (int): Nummer des Fahrparcours der absolviert werden soll
        """
        self.logger_start()
        fahrparcour(self, number)
        self.logger_save()

    def stop_parcours(self):
        """Abbruch des aktuell laufenden Fahrparcours"""
        print("Emergency STOP")
        fahrparcours_stop()

    @property
    def speed(self):
        return self._speed

    @speed.setter
    def speed(self, value):
        self._speed = value

    @property
    def direction(self):
        return self._direction

    @direction.setter
    def direction(self, value):
        self._direction = value

    @property
    def steering_angle(self):
        return self._steering_angle

    @steering_angle.setter
    def steering_angle(self, value):
        """Hier wird auf ein anderes Winkelsystem normiert.
        0 Grad = geradeaus,
        -45 Grad ist max links,
        +45 Grad ist max rechts"""
        if value > STEERINGE_ANGLE_MAX:
            self._steering_angle = STEERINGE_ANGLE_MAX
        elif value < (0 - STEERINGE_ANGLE_MAX):
            self._steering_angle = 0 - STEERINGE_ANGLE_MAX
        else:
            self._steering_angle = value
        self.fw.turn(90 + self._steering_angle)

    def drive(self, geschwindigkeit, richtung):
        """Längs-Steuerung des PiCar

        Args:
            geschwindigkeit (int): Geschwindigkeit in % (0...100)
            richtung (int): Fahrtrichtung (1=vor, 0=Stillstand, -1=zurück)
        """
        self.speed = geschwindigkeit
        self.bw.speed = self.speed
        self.direction = richtung
        if richtung > 0:
            self.bw.forward()
        elif richtung < 0:
            self.bw.backward()
        else:
            self.stop()

    def stop(self):
        """Anhalten des PiCar"""
        self.bw.stop()

    def get_and_log_drive_data(self):
        """Rückgabe der Fahr- und Sensordaten

        Returns:
            list: [Geschwindigkeit, Fahrtrichtung, Lenkwinkel, US-Distanz]
        """
        data = [self._speed, self._direction, self._steering_angle]
        self.logger_log(data)
        return data


class SonicCar(BaseCar):
    """Sonic-Car erweitert das BaseCar mit dem Ultraschall-Sensor

    Args:
        BaseCar (_type_): Erbt von der Klasse BaseCar
    """

    def __init__(self):
        super().__init__()
        self.us = basisklassen.Ultrasonic()
        self._us_distance = 0

    @property
    def distance(self):
        """Der Wert des US-Sensors wird hier auf 150cm limitiert da größere Werte nicht von Bedeutung sind
        Ist der empfangene Wert > 150cm wird ein Wert von -5 als Fehlerwert zurückgegeben
        Returns:
            _type_: _description_
        """
        self._us_distance = self.us.distance()
        if self._us_distance > 150:  # Werte nicht relevant
            self._us_distance = -5
        return self._us_distance

    def get_and_log_drive_data(self):
        """Rückgabe der Fahr- und Sensordaten

        Returns:
            list: [Geschwindigkeit, Fahrtrichtung, Lenkwinkel, US-Distanz]
        """
        data = [self._speed, self._direction, self._steering_angle, self._us_distance]
        self.logger_log(data)
        return data

    def usstop(self):
        self.us.stop()


class SensorCar(SonicCar):
    """Die Klasse SensorCar fuegt die Funtkion des IR-Sensors zu SonicCar hinzu

    Args:
        SonicCar (_type_): Erbt von der Klasse SonicCar
    """

    def __init__(self, filter_deepth: int = 2):
        super().__init__()
        self.ir = basisklassen.Infrared()
        self._ir_sensors = [0] * 5
        self._steering_soll = [0] * filter_deepth
        self._ir_calib = None
        with open("config.json", "r") as f:
            data = json.load(f)
            ir_calib = data.get("ir_calib")
            if ir_calib != None:
                self._ir_calib = ir_calib
            else:
                self._ir_calib = [1, 1, 1, 1, 1]
        self.angle_from_sensor = {
            0: IR_NO_LINE,
            1: -40,
            3: -32,
            2: -18,
            7: -18,
            6: -8,
            4: 0,
            14: 0,
            12: 8,
            8: 18,
            28: 18,
            24: 32,
            16: 40,
            31: IR_NO_LINE,
        }
        self.lookup = np.array([1, 2, 4, 8, 16])
        # ir_sensor_digital = [0,1,1,0,0]
        # winkel den die Lenkung stellen muss um zur Linie zu kommen:
        # winkel = angle_from_sensor.get(ir_sensor_digital*lookup.sum()) #wenn unbekannt kommt "None" zurück

    @property
    def ir_sensor_analog(self):
        """Ausgabe der Werte der IR-Sensoren

        Returns:
            list: Analogwerte der 5 IR-Sensoren
        """
        # self._ir_sensors = self.ir.read_analog()
        self._ir_sensors = (
            (self.ir.get_average(2) * np.array(self._ir_calib)).round(2).tolist()
        )
        return self._ir_sensors

    def calibrate_ir_sensors(self, fromDash: bool = False, menu_point=0):
        """Kalibrierung der einzelnen IR-Sensoren damit die Ergebnise vergleichbar werden
        Die Kalibrier-Werte werden in der config.json mit abgelegt.
        """
        if fromDash:
            if menu_point == 0:
                return "Sensor auf hellem Untergrund plazieren"
            if menu_point == 1:
                a = self.ir.get_average(100)
                return f"Messergebnis: {a}"
            if menu_point == 2:
                messung = np.array(a)
                ir_calib = messung.mean() / messung
                self._ir_calib = ir_calib.round(4)
                data = {}
                try:
                    with open("config.json", "r") as f:
                        data = json.load(f)
                except:
                    return "File read Error!"
                data["ir_calib"] = self._ir_calib.tolist()
                try:
                    with open("config.json", "w") as f:
                        json.dump(data, f)
                    return f"Kalibrierwerte {self._ir_calib} gespeichert"
                except:
                    return "File write Error"

        else:
            while True:
                print("-" * 13, "IR Sensor Kalibrierung", "-" * 13)
                print()
                input("Sensoren auf hellem Untergrund platzieren, dann Taste drücken")
                a = self.ir.get_average(100)
                print("Messergebnis:", a)
                user_in = input("Ergebnis verwenden? (j/n/q)")
                if user_in == "n":
                    print("Neue Messung")
                elif user_in == "j":
                    messung = np.array(a)
                    ir_calib = messung.mean() / messung
                    self._ir_calib = ir_calib.round(4)
                    print("Kalibrierwerte:", self._ir_calib)
                    data = {}
                    try:
                        with open("config.json", "r") as f:
                            data = json.load(f)
                    except:
                        print("File error read")
                    data["ir_calib"] = self._ir_calib.tolist()
                    try:
                        with open("config.json", "w") as f:
                            json.dump(data, f)
                    except:
                        print("File error write")
                    break
                else:
                    print("Abbruch durch Beutzer")
                    break
            print("IR Kalibrierung beendet")
            print("_" * 50)
            print()

    def angle_from_ir(self):
        """berechnet den Soll-Lenkeinschlag damit das Fahrzeug der Linie folgen kann

        Returns:
            int: Soll-Lenkeinschlag
            Wert 100: keine Linie erkannt -> IR_NO_LINE
            Wert 101: undefinierter Wert -> IR_INVALID
        """
        ir_data = np.array(self.ir_sensor_analog)
        compValue = IR_MARK * ir_data.max()
        sd = np.where(ir_data < compValue, 1, 0)
        lookupValue = (self.lookup * sd).sum()
        ir_result = self.angle_from_sensor.get(lookupValue)
        if ir_result == None:
            return IR_INVALID  # undefinierter Wert
        else:
            #  return ir_result
            if ir_result < 100:
                self._steering_soll = self._steering_soll[1:]
                self._steering_soll.append(ir_result)
                ir_out = np.mean(self._steering_soll)
                return ir_out
            else:
                return IR_NO_LINE

    def get_and_log_drive_data(self):
        """Rückgabe der Fahr- und Sensordaten

        Returns:
            list: [Geschwindigkeit, Fahrtrichtung, Lenkwinkel, US-Distanz, IR-Sensor1 , , , ,IR-Sensor5]
        """
        data = [
            self._speed,
            self._direction,
            self._steering_angle,
            self._us_distance,
        ] + self._ir_sensors

        self.logger_log(data)
        return data


def driveCar(car: SensorCar, speed, direction, angle, duration):
    """Hilfsfunktion um des PiCar für eine definierte Zeit mit vorgegebenen Parametern zu fahren

    Args:
        car (PiCar): Eine Instanz eines PiCar
        speed (int): Geschwindigkeit in %
        direction (int): Fahrtrichtung
        angle (int): Lenkwinkel
        duration (int): Fahrdauer
    """
    global fp_allowed
    i = 0
    while fp_allowed and (i < (10 * duration)):
        car.steering_angle = angle
        car.drive(speed, direction)
        car.get_and_log_drive_data()
        time.sleep(0.1)
        i += 1
    car.stop()


def fahrparcours_stop():
    """Abbruch des laufenden Fahrprogramms"""
    global fp_allowed
    fp_allowed = False


def fahrparcour(car: SensorCar, pos):
    """Fahrparcours abspielen

    Args:
        car (PiCar): eine Instanz des PiCar
        pos (int): die Nummer des gewünschten Parcours
    """
    global fp_allowed
    fp_allowed = True
    if pos == 1:
        print("Fahrparcours 1 gewaehlt:")
        print("3 Sekunden gerade vor")
        counter = 0
        state = 0
        while fp_allowed:
            car.get_and_log_drive_data()
            if state == 0:
                counter = 30
                car.drive(40, 1)
                car.steering_angle = 0
                state = 1
            elif state == 1:
                if counter > 0:
                    counter -= 1
                else:
                    print("eine Sekunde Pause")
                    counter = 10
                    car.drive(0, 0)
                    state = 2
            elif state == 2:
                if counter > 0:
                    counter -= 1
                else:
                    print("3 Sekunden gerade zurueck")
                    counter = 30
                    car.drive(40, -1)
                    car.steering_angle = 0
                    state = 3
            elif state == 3:
                if counter > 0:
                    counter -= 1
                else:
                    counter = 0
                    car.drive(0, 0)
                    break
            time.sleep(0.1)

    elif pos == 2:
        print("Fahrparcours 2 gewaehlt:")
        print("2 Sekunden gerade vor")
        driveCar(car, 40, 1, 0, 2)
        print("8 Sekunden vorwarts links herum")
        driveCar(car, 45, 1, -45, 8)
        print("1 Sekunde Pause")
        driveCar(car, 0, 0, 0, 1)
        print("8 Sekunden rueckwarts links herum")
        driveCar(car, 45, -1, -45, 8)
        print("2 Sekunden gerade zurueck")
        driveCar(car, 40, -1, 0, 2)
        car.stop()
        print()

    elif pos == 3:
        print("Fahrparcours 3 gewaehlt:")
        print("gerade vor bis Abstand < x")
        max_time = 200
        drive_time = 0
        distance = car.distance
        car.get_and_log_drive_data()
        while fp_allowed:
            while (distance > 20 or distance < 5) and drive_time < max_time:
                car.steering_angle = 0
                car.drive(40, 1)
                time.sleep(0.1)
                distance = car.distance
                car.get_and_log_drive_data()
                print("Abstand:", distance)
                drive_time += 1
            car.stop()
        car.stop()

    elif pos == 4:
        print("Erkundungsfahrt:")
        max_time = 1000  # 100s
        drive_time = 0
        while fp_allowed:
            for i in range(10):
                print("Fahrt:", i + 1)
                distance = car.distance
                car.get_and_log_drive_data()
                while (distance > 25 or distance < 1) and drive_time < max_time:
                    car.steering_angle = 0
                    car.drive(40, 1)
                    time.sleep(0.1)
                    distance = car.distance
                    car.get_and_log_drive_data()
                    print("Abstand:", distance)
                    drive_time += 1
                car.stop()
                print("zuruecksetzen")
                car.steering_angle = 45
                car.drive(40, -1)
                time.sleep(2)
                car.stop()
                car.steering_angle = 0
        car.stop()

    elif pos == 5:
        print("Line Follower")
        speed_limit = 100
        speed_soll = 40
        counter_stop = 0
        time_period = 0.01
        time_run = 25  # Sekunden
        ignore_stop = 0.25 / time_period
        while counter_stop < (time_run / time_period) and fp_allowed:
            if ignore_stop > 0:
                ignore_stop -= 1
            car_data = car.get_and_log_drive_data()
            ir_sens = car_data[4:9]
            st_angle = car.angle_from_ir()

            if st_angle == IR_INVALID:
                pass
                # print("invalid result") # nur zu Debug-Zwecken aktivieren
            if st_angle == IR_NO_LINE:
                print("STOP gefunden")
                if not ignore_stop:
                    break
            else:
                car.steering_angle = st_angle
            car.drive(speed_soll, 1)
            time.sleep(time_period)
            counter_stop += 1
        car.stop()
        car.steering_angle = 0
        print("Ende der Strecke")

    elif pos == 6:
        print("Line Follower enge Kurve")
        speed_limit = 100
        speed_soll = 40
        counter_stop = 0
        time_period = 0.01
        time_run = 25  # Sekunden
        ignore_stop = 0.25 / time_period
        last_angle = 0
        drive_reverse = 0
        time_drive_reverse = 1  # max. Zeit für Rückwärtsfahrt
        counter_reverse = time_drive_reverse / time_period
        while counter_stop < (time_run / time_period) and fp_allowed:
            if ignore_stop > 0:
                ignore_stop -= 1
            st_angle = car.angle_from_ir()
            if not drive_reverse:
                car_data = car.get_and_log_drive_data()
                if st_angle == IR_INVALID:
                    print("invalid result")
                if st_angle == IR_NO_LINE and not ignore_stop:
                    if abs(last_angle) >= 30:  # war ausserhalb des Bereichs
                        drive_reverse = 1
                        counter_reverse = time_drive_reverse / time_period
                        car.drive(0, 0)
                    else:
                        print("STOP gefunden")
                        if not ignore_stop:
                            break
                else:
                    car.steering_angle = st_angle
                    car.drive(speed_soll, 1)
                    last_angle = st_angle

            else:  # Rückwärtsfahrt
                if counter_reverse > 0:
                    counter_reverse -= 1
                    car.steering_angle = 0 - last_angle
                    car.drive(35, -1)
                    if abs(st_angle) < 20:  # Linie wieder unter Mitte des PiCar
                        car.drive(0, 0)
                        drive_reverse = 0
                else:
                    car.drive(0, 0)
                    drive_reverse = 0

            time.sleep(time_period)
            counter_stop += 1
        car.stop()
        car.steering_angle = 0
        print("Ende der Strecke")

    elif pos == 7:
        print("Line Follower mit US")
        speed_limit = 100
        speed_soll = 40
        counter_stop = 0
        time_period = 0.01
        time_run = 25  # Sekunden
        ignore_stop = 0.25 / time_period
        last_angle = 0
        drive_reverse = 0
        us_flag = False
        time_drive_reverse = 1  # max. Zeit für Rückwärtsfahrt
        us_distance = 150
        counter_reverse = time_drive_reverse / time_period
        while counter_stop < (time_run / time_period) and fp_allowed:
            if ignore_stop > 0:
                ignore_stop -= 1
            us_distance = car.distance
            st_angle = car.angle_from_ir()
            car_data = car.get_and_log_drive_data()
            if us_flag and us_distance > 25:
                us_flag = False

            if not drive_reverse:
                if us_flag or (us_distance < 15 and us_distance > 0):
                    us_flag = True
                    car.stop()
                    print("US-Distanz zu gering --> STOP")
                    # break
                else:
                    if st_angle == IR_INVALID:
                        print("invalid result")
                    if st_angle == IR_NO_LINE and not ignore_stop:
                        if abs(last_angle) >= 20:  # war ausserhalb des Bereichs
                            drive_reverse = 1
                            counter_reverse = time_drive_reverse / time_period
                            car.drive(0, 0)
                        else:
                            print("STOP gefunden")
                            if not ignore_stop:
                                break
                    else:
                        car.steering_angle = st_angle
                        car.drive(speed_soll, 1)
                        last_angle = st_angle

            else:  # Rückwärtsfahrt
                if counter_reverse > 0:
                    counter_reverse -= 1
                    car.steering_angle = 0 - last_angle
                    car.drive(35, -1)
                    if abs(st_angle) < 20:  # Linie wieder unter Mitte des PiCar
                        car.drive(0, 0)
                        drive_reverse = 0
                else:
                    car.drive(0, 0)
                    drive_reverse = 0

            time.sleep(time_period)
            counter_stop += 1
        car.stop()
        car.steering_angle = 0
        print("Ende der Strecke")

    elif pos == 8:
        i = 0
        counts = 0
        print("Datenaufzeichnung IR Sensoren")
        car.stop()
        duration = 3  # Sekunden
        mps = 10
        user_in = input("Messungen pro Sekunde:")
        try:
            mps = int(user_in)
        except:
            print("das war keine Zahl!")

        user_in = input("Messdauer in Sekunden:")
        try:
            duration = int(user_in)
        except:
            print("das war keine Zahl!")
        counts = mps * duration
        while i < counts and fp_allowed:
            a = car.get_and_log_drive_data()
            print("IR-Sensors:", a[4:10], "US-Sensor:", a[3])
            time.sleep(1 / mps)
            i += 1
        print()

    elif pos == 9:
        print("Fahrparcours 9 gewaehlt:")
        print("gerade zuruecksetzen")
        driveCar(50, -1, 0, 2)
        car.stop()
        print()

    else:
        print("Fahrparcours", pos, "nicht bekannt!")
    car.us.stop()


def main():
    """Menü für die Solo-Steuerung des PiCar ohne Dash"""
    myCar = SensorCar(filter_deepth=2)
    myCar.stop()
    myCar.steering_angle = 0
    use_logger = False
    while True:
        print("Test des PiCar:")
        user_in = input("Sollen die Daten aufgezeichnet werden (j/n/q/)?: ")
        if user_in.lower() == "j":
            use_logger = True
        else:
            use_logger = False
        if user_in.lower() == "q":
            break
        user_in = input(
            """Fahrparcours Auswahl: 
                0 = IR-Sensor-Kalibrierung
                1 = vor / zurueck
                2 = Kurvenfahrt
                3 = vor bis Hindernis
                4 = Erkundungsfahrt
                5 = LineFollower
                6 = LineFollower enge Kurve
                7 = LineFollower mit US
                8 = Sensor-Test
                9 = gerade zuruecksetzen
                "x" = abbrechen
                "q" = beenden 
                Bitte waehlen: """
        )
        if isdigit(user_in):
            if int(user_in) == 0:
                myCar.calibrate_ir_sensors()
            else:
                if use_logger == True:
                    myCar.logger_start()
                fahrparcour(myCar, int(user_in))
                myCar.logger_save()
                print("Parcours beendet")
        else:
            if user_in.lower() == "x":
                pass
            elif user_in.lower() == "q":
                print("Programm beendet")
                break
            else:
                print("Das habe ich nicht verstanden!")


if __name__ == "__main__":
    main()
