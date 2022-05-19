"""Import der notwendigen Bibliotheken und Klassen."""
import basisklassen
import click
import os, json, time
from datetime import datetime
import numpy as np
from collections import deque
from concurrent import futures
from concurrent.futures import ThreadPoolExecutor



class BaseCar:
    """Die Klasse BaseCar implementiert die Grund-Funktionalitaeten des PiCars.

    Args:
        LOG_FREQ (float): Zeit-Interval zum Speichern von Fahrdaten im Datenlogger.
        SA_MAX (int): Maximaler zulaessiger Lenkwinkel des PiCars.
    """

    LOG_FREQ = 0.1
    SA_MAX = 45

    def __init__(self):
        """Initialisierung der Klasse BaseCar.

        Args:
            steering_angle (float): Lenkwinkel des PiCars.
            speed (int): Geschwindigkeit des PiCars.
            direction (int): Fahrtrichtung des PiCars.
            tmp_speed(int): Speichert die Geschwindigkeit bei Uebergabe in Fahrparcour.
            log_file_path (string): Speichert den Ordner-Pfad fuer die Log-Dateien des Datenloggers.
            active (bool): Flag zur Erkennung des Fahr-Zustandes.
            worker (ThreadPoolExecutor): Instanz der Klasse ThreadPoolExecutor.
            dl (Datenlogger): Instanz der Klasse Datenlogger.
        """
        self._steering_angle = 0
        self._speed = 0
        self._direction = 1
        self._tmp_speed = 0
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
        self._active = False
        self._worker = None
        self._dl = None

    def startDriveMode(self):
        """Funktion zur Initalisierung des Fahr-Modus mit Multi-Threading"""

        self._active = True
        self.steering_angle = 0
        self._dl = Datenlogger(log_file_path=self._log_file_path)
        self._worker = ThreadPoolExecutor(max_workers=5)
        self._worker.submit(self.dlWorker)

    def endDriveMode(self):
        """Funktion zum Beenden des Fahr-Modus mit Multi-Threading"""

        self._worker.shutdown(wait=True)
        self.steering_angle = 0
        self.stop()

    def dlWorker(self):
        """Funktion zur Nutzung des Datenloggers mit Multi-Threading.

        Hinweis: Wird automatisch in der Funktion startDriveMode() im BaseCar genutzt.
        """
        self._dl.start()
        while self._active:
            self._dl.append(self.drive_data)
            time.sleep(self.LOG_FREQ)
        self._dl.save()

    @property
    def drive_data(self):
        """Ausgabe der Fahrdaten fuer den Datenlogger.

        Returns:
            [list]: speed, direction, steering_angle
        """
        return [self.speed, self.direction, self.steering_angle]

    @property
    def speed(self):
        """Returns speed.

        Returns:
            [int]: speed.
        """
        return self._speed

    @speed.setter
    def speed(self, value):
        """Sets speed.

        Args:
            [int]: speed.
        """
        self._speed = value

    @property
    def direction(self):
        """Returns direction.

        Returns:
            [int]: direction.
        """
        return self._direction

    @direction.setter
    def direction(self, value):
        """Sets direction.

        Args:
            [int]: direction.
        """
        self._direction = value

    @property
    def steering_angle(self):
        """Returns steering angle.

        Returns:
            [float]: steering angle.
        """
        return self._steering_angle

    @steering_angle.setter
    def steering_angle(self, value):
        """Sets steering angle.

        Args:
            [float]: steering angle.

        Hinweis:
        Hier wird auf ein anderes Winkelsystem normiert.
        0 Grad = geradeaus,
        -45 Grad ist maximaler Lenkwinkel links,
        +45 Grad ist maximal Lenkwinkel rechts
        """
        if value > self.SA_MAX:
            self._steering_angle = self.SA_MAX
        elif value < (0 - self.SA_MAX):
            self._steering_angle = 0 - self.SA_MAX
        else:
            self._steering_angle = value
        self.fw.turn(90 + self._steering_angle)

    def drive(self, geschwindigkeit, richtung):
        """Funktion zum Fahren PiCars.

        Args:
            [int]: geschwindigkeit
            [int]: richtung
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
        """Funktion zum Stoppen der Hinterraeder des PiCars."""

        self.bw.stop()

    def generischerFahrparcour(self, fp, v=50):
        """Funktion fuer den generischen Fahrparcour des PiCars.
        
        Args:
            [tupel]: validFP
        """
        validFP = (1, 2, 3, 4, 5, 6, 7)

        if fp in validFP:
            print(f"Fahrparcour {fp} gestartet.")

            # Starte Drive Mode
            self.startDriveMode()
            self._tmp_speed = v

            if fp == 1:
                self.fp1(v)
            elif fp == 2:
                self.fp2(v)
            elif fp == 3:
                self.fp3(v)
            elif fp == 4:
                self.fp4(v)
            elif fp == 5:
                self.fp5(v)
            elif fp == 6:
                self.fp6(v)
            elif fp == 7:
                self.fp7(v)

            # Ende Drive Mode
            self.endDriveMode()

            print(f"Fahrparcour {fp} beendet.")
        else:
            print("Es wurde kein gueltiger Fahrparcour ausgewaehlt!")

    def fp1(self, v=50):
        """Funktion für den Fahrparcour 1.
        
        Beschreibung:
            3 Sekunden Vorwaerts / 1 Sekunde Stillstand / 3 Sekunden Rueckwaerts
        """
        self.drive(v, 1)
        time.sleep(3)

        self.stop()
        time.sleep(1)

        self.drive(v, -1)
        time.sleep(3)

        # Drive-Mode Ende setzen
        self._active = False

    def fp2(self, v=50):
        """Funktion für den Fahrparcour 2.
        
        Beschreibung:
            1 Sekunde Vorwaerts / 8 Sekunden Vorwaerts mit max. neg. Lenkwinkel 
            / 8 Sekunden Rueckwaerts mit max. neg. Lenkwinkel / 1 Sekunde Rueckwarts

            Identische Fahrparcour nochmals mit max. pos. Lenkwinkel.
        """
        for sa in [(-self.SA_MAX + 5), (self.SA_MAX - 5)]:
            self.steering_angle = 0
            self.drive(v, 1)
            time.sleep(1)

            self.steering_angle = sa
            time.sleep(8)

            self.stop()

            self.drive(v, -1)
            time.sleep(8)

            self.steering_angle = 0
            time.sleep(1)

        # Drive-Mode Ende setzen
        self._active = False



class Sonic(BaseCar):
    """Die Klasse Sonic fuegt die Funktion des US-Sensors zur BaseCar-Klasse hinzu.

    Args:
        BaseCar (_type_): Erbt von der Klasse BaseCar.
        US_FREQ (float): Abtastrade des US-Sensors in Sekunden.
        US_OFFSET (float): Offset fuer den US-Sensor bis zur Erkennung eines Hindernisses.
    """

    US_FREQ = 0.05
    US_OFFSET = 20

    def __init__(self):
        """Initialisierung der Klasse Sonic.

        Args:
            distance (int): Abstand zum aktuellen Hindernis.
            hindernis (bool): Flag zur Erkennung eines Hindernisses.
            timerHindernis (time): Messung der Zeit waehrend ein Hindernis erkannt wird.
        """
        super().__init__()
        self.us = basisklassen.Ultrasonic()
        self._distance = self.US_OFFSET + 1
        self._hindernis = False
        self._timerHindernis = 0

    def startDriveMode(self):
        """Funktion zur Initalisierung des Fahr-Modus mit Multi-Threading"""

        super().startDriveMode()
        self._worker.submit(self.usWorker)
        self._hindernis = False

    def usWorker(self):
        """Funktion zur Abtastung des US-Sensors mit Multi-Threading.

        Hinweis: Wird automatisch in der Funktion startDriveMode() im SensorCar genutzt.
        """
        while self._active:
            if self._hindernis == False and not (self.distance - self.US_OFFSET) > 0:
                self._hindernis = True
                self._timerHindernis = time.perf_counter()
            if self._hindernis == True and (self.distance - self.US_OFFSET) > 0:
                self._hindernis = False

            time.sleep(self.US_FREQ)

    def inputWorker(self):
        """Funktion zur Interaktion mit dem Nutzer mit Multi-Threading.

        Hinweis: Muss zur Verwendung im jeweiligen Fahrparcour hinzugefuegt werden.
                self._worker.submit(self.inputWorker)
        """
        while self._active:
            inpUser = input("Bitte einen Fahrbefehl eingeben: ")
            dictBefehle = {
                "f": "self.direction = 1",
                "b": "self.direction = -1",
                "e": "self._active = False",
            }
            try:
                if inpUser in dictBefehle:
                    exec(dictBefehle[inpUser])
                elif type(int(inpUser)) and int(inpUser) >= 0 and int(inpUser) <= 100:
                    self.speed = int(inpUser)
                    self._tmp_speed = int(inpUser)
                else:
                    raise Exception
            except Exception:
                print("Kein gueltiger Befehl oder gueltige Geschwindigkeit!")
                continue

    def rangierenWorker(self):
        """Funktion fuehrt die Rangier-Funktionalitaeten fuer Fahrparcour 4 aus.
        
        Beschreibung:
            Wenn Hindernis erkannt wird, max. neg. Lenkwinkel
            und Rueckwarts Fahrt mit v=50 fuer 2.55 Sekunden.
            Danach geradeaus mit vorheriger Geschwindigkeit.
        """

        while self._active:
            if self._hindernis:

                self.drive(50, -1)
                self.steering_angle = -self.SA_MAX + 5

                timerRangieren = time.perf_counter()
                while (time.perf_counter() - timerRangieren) < 2.55:
                    time.sleep(0.1)

                self.steering_angle = 0
                self.drive(self._tmp_speed, 1)

    @property
    def distance(self):
        """Returns distance in cm.

        Returns:
            [int]: Distance in cm for a single measurement.
            (Konstante US_OFFSET+1 fuer < 0cm oder > 150cm)
        """
        dist = self.us.distance()
        self._distance = dist if (dist >= 0 and dist <= 150) else (self.US_OFFSET + 1)
        return self._distance

    @property
    def drive_data(self):
        """Ausgabe der Fahrdaten fuer den Datenlogger.

        Returns:
            [list]: speed, direction, steering_angle, distance
        """
        return [self.speed, self.direction, self.steering_angle, self._distance]

    def fp3(self, v=50):
        """Funktion für den Fahrparcour 3.
        
        Beschreibung:
            Vorwaerts Fahrt bis ein Hindernis mit dem US-Sensor erkannt wird.
        """
        self.drive(v, 1)

        while self._active and not self._hindernis:
            time.sleep(0.1)

        # Drive-Mode Ende setzen
        self._active = False

    def fp4(self, v=50):
        """Funktion für den Fahrparcour 4.
        
        Beschreibung:
            Vorwarts Fahrt bis ein Hindernis mit dem US-Sensor erkannt wird.
            Dann Reaktion mit der Rangieren-Funktion.
        """
        self._worker.submit(self.rangierenWorker)
        self._worker.submit(self.inputWorker)

        self.drive(v, 1)



class SensorCar(Sonic):
    """Die Klasse SensorCar fuegt die Funktion des IR-Sensors zur Sonic-Klasse hinzu.

    Args:
        SonicCar (_type_): Erbt von der Klasse SonicCar.
        IF_FREQ (float): Abtastrate des IF-Sensors in Sekunden.
        IR_FAKTOR (float): Faktor zur Definition des Schwellwert (Threshold) zur Erkennung der schwarzen Linie.
        filter_depth (int): Anzahl der gespeicherten Lenkwinkel in temporaerer Liste.
        sa_from_ir_result (dict): Lookup Dictionary fuer den Soll-Lenkwinkel auf Basis der IR-Result.
    """

    IF_FREQ = 0.05
    IR_FAKTOR = 0.75
    IR_NO_LINE = 100
    IR_INVALID = 101
    SA_FROM_IR_RESULT = {
                        0: IR_NO_LINE,
                        1: -40,
                        3: -32,
                        2: -23,
                        7: -23,
                        6: -10,
                        4: 0,
                        14: 0,
                        12: 10,
                        8: 23,
                        28: 23,
                        24: 32,
                        16: 40,
                        31: IR_NO_LINE,
                        101: IR_INVALID,
                    }

    def __init__(self, filter_depth: int = 2):
        """Initialisierung der Klasse SensorCar.

        Args:
            line (bool): Flag zur Erkennung der Line.
            ir_sensor_analog (list): Analoge Messwerte des IR-Sensors.
            ir_matrix (tupel): Multiplikationsmatrix zur Binaerumwandlung.
            tmp_sa (list):  Liste der letzten n Lenkwinkel. (n=filter_depth)
            ir_calib (config.json): Importiert die kalibrierten Werte fuer den IR-Sensor aus der config.json.
        """

        super().__init__()
        self.ir = basisklassen.Infrared()
        self._line = True
        self._ir_sensor_analog = self.ir.get_average(2)
        self._ir_matrix = (1, 2, 4, 8, 16)
        self._tmp_sa = deque([0] * filter_depth)
        self._ir_calib = None
        with open("config.json", "r") as f:
            data = json.load(f)
            ir_calib = data.get("ir_calib")
            if ir_calib != None:
                self._ir_calib = ir_calib
            else:
                self._ir_calib = [1, 1, 1, 1, 1]

    def startDriveMode(self):
        """Funktion zur Initalisierung des Fahr-Modus mit Multi-Threading"""

        super().startDriveMode()
        self._line = True

    @property
    def ir_sensor_analog(self):
        """Ausgabe der Werte der IR-Sensoren unter Beruecksichtigung der kalibrierten IR-Sensoren.

        Returns:
            [list]: Analogwerte der 5 IR-Sensoren
        """
        self._ir_sensor_analog = ((self.ir.get_average(2) * np.array(self._ir_calib)).round(2).tolist())
        return self._ir_sensor_analog

    @property
    def drive_data(self):
        """Ausgabe der Fahrdaten fuer den Datenlogger.

        Returns:
            [list]: speed, direction, steering_angle, distance, ir_sensors
        """
        data = [
            self._speed,
            self._direction,
            self._steering_angle,
            self._distance,
        ]
        data += self._ir_sensor_analog

        return data

    def get_ir_result(self):
        """Ausgabe des IR-Results (Key-Value) fuer Uebersetzungstabelle

        Returns:
            [int]: IR-Key für Uebersetzungstabelle.
        """
        ir_data = np.array(self.ir_sensor_analog)
        thresVal = self.IR_FAKTOR * ir_data.max()

        ir_digital = np.where(ir_data < thresVal, 1, 0)
        ir_result = (self._ir_matrix * ir_digital).sum()

        return ir_result

    def get_steering_angle(self):
        """Ausgabe des Lenkwinkels fuer das PiCar (Mean)
        
        Returns:
            [float]: Mittleren Lenkwinkel.
        """
        ir_result = self.get_ir_result()

        sa_lookup = self.SA_FROM_IR_RESULT.get(ir_result) if self.SA_FROM_IR_RESULT.get(ir_result) is not None else self.IR_INVALID
        sa_soll = sa_lookup if sa_lookup < self.IR_NO_LINE else self._tmp_sa[-1]

        self._tmp_sa.popleft()
        self._tmp_sa.append(sa_soll)

        return np.mean(self._tmp_sa), sa_lookup

    def fp5(self, v=50):
        """Funktion für den Fahrparcour 5.
        
        Beschreibung:
            Vorwaerts Fahrt mit Linienverfolgung bis die Linie nicht mehr erkannt wird.
        """
        self.drive(v, 1)

        while self._active:

            sa_mean, sa_lookup = self.get_steering_angle()

            if sa_lookup < self.IR_NO_LINE:
                self.steering_angle = sa_mean
            elif sa_lookup == self.IR_NO_LINE:
                self._active = False
            else:
                print("Invalid IR-Result")

            time.sleep(self.IF_FREQ)

    def fp6(self, v=50):
        """Funktion für den Fahrparcour 6.
        
        Beschreibung:
            Vorwaerts Fahrt mit Linienverfolgung bis die Linie nicht mehr erkannt wird.
            Wenn Linie nicht mehr erkannt wird, entweder Rueckwaerts Fahrt mit gegensaetlichem 
            Lenkwinkel bis die Linie wieder erkannt wird oder Abbruch, wenn Lenkwinkel < 20 bei
            Verlust der Linie war.
        """
        self.drive(v, 1)

        while self._active:

            while self._active and self._line:
                sa_mean, sa_lookup = self.get_steering_angle()

                if sa_lookup < self.IR_NO_LINE:
                    self.steering_angle = sa_mean
                elif sa_lookup == self.IR_NO_LINE:
                    self._line = False
                    if abs(self._tmp_sa[-1]) < 20:
                        self._active = False
                        break
                    else:
                        self.drive(self._tmp_speed, -1)
                        self.steering_angle = self._tmp_sa[-1] * -1
                else:
                    print("Invalid IR-Result")

                time.sleep(self.IF_FREQ)

            while self._active and not self._line:
                sa_mean, sa_lookup = self.get_steering_angle()
                
                if sa_lookup < self.IR_NO_LINE:
                    self._line = True
                    self.drive(self._tmp_speed, 1)
                    break

                time.sleep(self.IF_FREQ)

    def fp7(self, v=50):
        """Funktion für den Fahrparcour 7.
        
        Beschreibung:
            Vorwaerts Fahrt mit Linienverfolgung bis die Linie nicht mehr erkannt wird.
            Wenn Linie nicht mehr erkannt wird, entweder Rueckwaerts Fahrt mit gegensaetlichem 
            Lenkwinkel bis die Linie wieder erkannt wird oder Abbruch, wenn Lenkwinkel < 20 bei
            Verlust der Linie war.
            Bei Erkennung eines Hindernisses wird gestoppt. Wenn Hindernis laenger als 5 Sekunden
            erkannt wird, wird die Fahrt beendet.
        """
        self.drive(v, 1)
        
        while self._active:
            while self._active and not self._hindernis:
                while self._active and self._line and not self._hindernis:
                    sa_mean, sa_lookup = self.get_steering_angle()

                    if sa_lookup < self.IR_NO_LINE:
                        self.steering_angle = sa_mean
                    elif sa_lookup == self.IR_NO_LINE:
                        self._line = False
                        if abs(self._tmp_sa[-1]) < 20:
                            self._active = False
                        else:
                            self.drive(self._tmp_speed, -1)
                            self.steering_angle = self._tmp_sa[-1] * -1
                    else:
                        print("Invalid IR-Result")
                        
                    time.sleep(self.IF_FREQ)

                while self._active and not self._line and not self._hindernis:
                    sa_mean, sa_lookup = self.get_steering_angle()
                    
                    if sa_lookup < self.IR_NO_LINE:
                        self._line = True
                        self.drive(self._tmp_speed, 1)
                        break

                    time.sleep(self.IF_FREQ)

            while self._active and self._hindernis:
                self.stop()
                if (time.perf_counter() - self._timerHindernis) > 5:
                    self._active = False
                time.sleep(self.US_FREQ)
            else:
                self.drive(self._tmp_speed, 1)

    def print_ir_values(self):
        """Funktion gibt 10 Messwerte des IR-Sensors aus."""

        for i in range(10):
            print(self.ir_sensor_analog)
            time.sleep(self.IF_FREQ)

    def calibrate_ir_sensors(self):
        """Funktion kalibriert die IR-Sensoren auf hellem Untergrund (Weisses Blatt).

        Returns:
        [config.json]: Fuegt den Key: "ir_calib" der JSON-Datei hinzu.
        """
        while True:
            input("Bitte das PiCar auf hellem Untergrund platzieren, dann Taste druecken!")
            a = self.ir.get_average(100)
            print("Messergebnis: ", a)
            user_in = input("Ergebnis verwenden? (j/n/q)")
            if user_in == "n":
                print("Neue Messung!")
            elif user_in == "j":
                messung = np.array(a)
                ir_calib = messung.mean() / messung
                self._ir_calib = ir_calib.round(4)
                print("Kalibrierwerte: ", self._ir_calib)
                data = {}
                try:
                    with open("config.json", "r") as f:
                        data = json.load(f)
                except:
                    print("Datei konnte nicht gelesen werden.")
                data["ir_calib"] = self._ir_calib.tolist()
                try:
                    with open("config.json", "w") as f:
                        json.dump(data, f)
                except:
                    print("Datei konnte nicht geschrieben werden.")
                break
            else:
                print("Abbruch durch Benutzer.")
                break

        print("IR-Kalibrierung wurde beendet.")


class Datenlogger:
    """Datenlogger Klasse

    Funktion:
    Speichert uebergebene Tupels oder Listen mit Angabe des Zeitdeltas ab Start der Aufzeichnung in ein JSON-File.

    Returns:
        [*.json]: Messwerte aus uebergebenen Daten mit bliebigem Zeitinterval.
    """

    def __init__(self, log_file_path=None):
        """Zielverzeichnis fuer Logfiles kann beim Init mit uebergeben werden.
            Wenn der Ordner nicht existiert wird er erzeugt.

        Args:
            log_file_path (_type_, optional): Angabe des Zielordners. Defaults to None.
        """
        self._log_file = {}
        self._log_data = []
        self._start_timestamp = 0
        self._logger_running = False
        self._log_file_path = log_file_path

    def start(self):
        """Funktion startet den Datenlogger."""

        self._logger_running = True
        self._start_timestamp = time.time()
        self._log_file["start"] = str(datetime.now()).partition(".")[0]

    def append(self, data):
        """Funktionen fuegt Daten in die Liste des Datenloggers hinzu."""

        if self._logger_running:
            ts = round((time.time() - self._start_timestamp), 2)
            self._log_data.append([ts] + data)

    def save(self):
        """Funktion speichert die uebergebenen Daten."""

        if self._logger_running and (len(self._log_data) > 0):
            self._logger_running = False
            self._log_file["data"] = self._log_data
            self._log_file["ende"] = str(datetime.now()).partition(".")[0]
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


@click.command()
@click.option(
    "--modus",
    "--m",
    type=int,
    default=None,
    help="Startet Auswahl der Fahrzeug-Funktionen",
)
def main(modus):
    """
    Main-Programm: Manuelles Ansteuern der implementierten Fahrparcours 1-7 sowie Kalibrierung und Ausgabe der IR-Sensoren.

    Args[Klassen]:
                    PiCar.BaseCar()
                    PiCar.Sonic()
                    PiCar.SensorCar()
    Funktionen der Klassen:
                    fp1() - fp7()
                    calibrate_ir_sensors()
                    print_ir_values()
    Args[Fahrparcour]:
                    v (int): Geschwindigkeit. Default 50
    """

    print("-- Manuelle Auswahl der Fahrzeug-Funktionen --")
    modi = {
        0: "Kalibrierung der IR-Sensoren",
        1: "Fahrparcour 1",
        2: "Fahrparcour 2",
        3: "Fahrparcour 3",
        4: "Fahrparcour 4",
        5: "Fahrparcour 5",
        6: "Fahrparcour 6",
        7: "Fahrparcour 7",
        9: "Ausgabe IR-Werte",
    }
    str_warnung = "ACHTUNG! Das Auto wird ein Stück fahren!\n Druecken Sie ENTER zum Start."
    str_abbruch = "Abbruch!"

    if modus == None:
        print("--" * 23)
        print("Auswahl:")
        for m in modi.keys():
            print("{i} - {name}".format(i=m, name=modi[m]))
        print("--" * 23)

    while modus == None:
        modus = input("Wähle Ziffer! (Andere Taste für Abbruch): ? ")
        if modus in ["0", "1", "2", "3", "4", "5", "6", "7", "9"]:
            break
        else:
            modus = None
            print("Getroffene Auswahl nicht möglich.")
            quit()
    modus = int(modus)

    if modus == 0:
        print(modi[modus])
        SensorCar().calibrate_ir_sensors()

    if modus == 1:
        x = input(str_warnung)
        SensorCar().generischerFahrparcour(1) if x == "" else print(str_abbruch)

    if modus == 2:
        x = input(str_warnung)
        SensorCar().generischerFahrparcour(2) if x == "" else print(str_abbruch)

    if modus == 3:
        x = input(str_warnung)
        SensorCar().generischerFahrparcour(3) if x == "" else print(str_abbruch)

    if modus == 4:
        x = input(str_warnung)
        SensorCar().generischerFahrparcour(4) if x == "" else print(str_abbruch)

    if modus == 5:
        x = input(str_warnung)
        SensorCar().generischerFahrparcour(5) if x == "" else print(str_abbruch)

    if modus == 6:
        x = input(str_warnung)
        SensorCar().generischerFahrparcour(6) if x == "" else print(str_abbruch)

    if modus == 7:
        x = input(str_warnung)
        SensorCar().generischerFahrparcour(7) if x == "" else print(str_abbruch)

    if modus == 9:
        SensorCar().print_ir_values()


if __name__ == "__main__":
    main()
