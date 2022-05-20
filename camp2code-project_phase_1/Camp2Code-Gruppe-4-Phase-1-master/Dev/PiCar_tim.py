"""Import der notwendigen Bibliotheken."""
import basisklassen
import click
import os, json, time
from datetime import datetime
import numpy as np
from concurrent import futures
from concurrent.futures import ThreadPoolExecutor



class BaseCar:
    """Die Klasse BaseCar implementiert die Grund-Funktionen des PiCars.

    Args:
        LOG_FREQ (float): Zeit-Interval zum Speichern von Fahrdaten im Datenlogger.
        SA_MAX (int): Maximaler Lenkwinkel des PiCars
    """

    LOG_FREQ = 0.1
    SA_MAX = 45

    def __init__(self):
        """Initialisierung der Klasse BaseCar.

        Args:
            steering_angle(float): Lenkwinkel des PiCars.
            speed(float): Geschwindigkeit des PiCars.
            direction(float): Fahrtrichtung des PiCars.
            active(bool): Flag zur Erkennung des Fahr-Zustandes.
            worker(ThreadPoolExecutor): Instanz der Klasse ThreadPoolExecutor.
            dl(Datenlogger): Instanz der Klasse Datenlogger.
            tmpspeed(int): Speichert die Geschwindigkeit bei Uebergabe in Fahrparcour.
        """
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

    def endDriveMode(self, waitingWorker=False):
        """Funktion zum Beenden des Fahr-Modus mit Multi-Threading"""

        if waitingWorker:
            self._worker.shutdown(wait=True)
        else:
            self._worker.shutdown(wait=False)
        self._active = False
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
        -45 Grad ist max links,
        +45 Grad ist max rechts
        """
        if value > self.SA_MAX:
            self._steering_angle = self.SA_MAX
        elif value < (0 - self.SA_MAX):
            self._steering_angle = 0 - self.SA_MAX
        else:
            self._steering_angle = value
        self.fw.turn(90 + self._steering_angle)

    def drive(self, geschwindigkeit, richtung):
        """Funktion zum Fahren PiCars

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
        """Funktion zum stoppen der Hinterraeder des PiCars"""

        self.bw.stop()

    def fp1(self, v=50):
        """Funktion für den Fahrparcour 1"""

        print("Fahrparcour 1 gestartet.")
        # Starte Drive Mode
        self.startDriveMode()

        # Vorwaerts 3sec
        self.drive(v, 1)
        time.sleep(3)

        # Stillstand 1sec
        self.stop()
        time.sleep(1)

        # Rueckwaerts 3sec
        self.drive(v, -1)
        time.sleep(3)

        # Ende Drive Mode
        self.endDriveMode(waitingWorker=False)
        print("Fahrparcour 1 beendet.")

    def fp2(self, v=50):
        """Funktion für den Fahrparcour 2"""

        print("Fahrparcour 2 gestartet.")
        # Starte Drive Mode
        self.startDriveMode()

        for sa in [(-self.SA_MAX + 5), (self.SA_MAX - 5)]:
            # Vorwaerts 1sec gerade
            self.steering_angle = 0
            self.drive(v, 1)
            time.sleep(1)

            # Vorwaerts 8sec Max Lenkwinkel
            self.steering_angle = sa
            time.sleep(8)

            # Stoppen
            self.stop()

            # Rueckwaerts 8sec Max Lenkwinkel
            self.drive(v, -1)
            time.sleep(8)

            # Rueckwaerts 1sec gerade
            self.steering_angle = 0
            time.sleep(1)

        # Ende Drive Mode
        self.endDriveMode(waitingWorker=False)
        print("Fahrparcour 2 beendet.")


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
            distance(int): Abstand zum aktuellen Hindernis.
            hindernis(bool): Flag zur Erkennung eines Hindernisses.
            tmpspeed(int): Speichert die Geschwindigkeit bei Uebergabe in Fahrparcour.
        """
        super().__init__()
        self.us = basisklassen.Ultrasonic()
        self._distance = self.US_OFFSET + 1
        self._hindernis = False
        self._tmpspeed = None

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
                self._cntHindernis = time.perf_counter()
            if self._hindernis == True and (self.distance - self.US_OFFSET) > 0:
                self._hindernis = False

            time.sleep(self.US_FREQ)

    def inputWorker(self):
        """Funktion zur Interaktion mit Nutzer mit Multi-Threading.

        Hinweis: Muss zur Verwendung im jeweiligen Fahrparcour hinzugefuegt werden.
                self._worker.submit(self.inputWorker)
        """
        while self._active:
            inpUser = input("Fahrbefehl eingeben: ")
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
                    self._tmpspeed = int(inpUser)
                else:
                    raise Exception
            except Exception:
                print("Kein gültiger Befehl oder gültige Geschwindigkeit!")
                continue

    def rangierenWorker(self):
        """Funktion fuehrt die Rangier-Funktionalitaeten fuer Fahrparcour 4 aus."""

        while self._active:
            if self._hindernis:

                self.drive(50, -1)
                self.steering_angle = -40

                cntTime = time.perf_counter()
                while (time.perf_counter() - cntTime) < 2.55:
                    time.sleep(0.1)

                self.steering_angle = 0
                self.drive(self._tmpspeed, 1)

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
        """Funktion für den Fahrparcour 3"""

        print("Fahrparcour 3 gestartet.")
        # Starte Drive Mode
        self.startDriveMode()

        # Starte die Fahrt
        self.drive(v, 1)
        while self._active and not self._hindernis:
            time.sleep(0.1)

        # Ende Drive Mode
        self.endDriveMode(waitingWorker=False)
        print("Fahrparcour 3 beendet.")

    def fp4(self, v=50):
        """Funktion für den Fahrparcour 4"""

        print("Fahrparcour 4 gestartet.")
        # Starte Drive Mode
        self.startDriveMode()
        self._worker.submit(self.rangierenWorker)
        # self._worker.submit(self.inputWorker)
        self._tmpspeed = v

        # Starte die Fahrt
        self.drive(v, 1)

        # Wartet auf Fertigstellung aller Threads
        self.endDriveMode(waitingWorker=True)

        # Ende Drive Mode
        print("Fahrparcour 4 beendet.")


class SensorCar(Sonic):
    """Die Klasse SensorCar fuegt die Funktion des IR-Sensors zur Sonic-Klasse hinzu.

    Args:
        SonicCar (_type_): Erbt von der Klasse SonicCar
        IF_FREQ (float): Abtastrate des IF-Sensors in Sekunden.
        IR_THRES_FAKTOR (float): Faktor fuer den Schwellwert zur Erkennung der schwarzen Linie.
    """

    IF_FREQ = 0.04
    IR_THRES_FAKTOR = 1

    def __init__(self):
        """Initialisierung der Klasse SensorCar.

        Args:
            ir_matrix (tupel): Matrix zur Berechnung der Keys fuer das Dictionary sa_from_ir
            sa_from_ir (dict): Lenkwinkel Lookup-Tabelle.
            ir_sensor_analog(list): Analoge Messwerte des IR-Sensors.
            tmp_sa (float): Letzte bekannte Lenkwinkel des PiCars.
            tmp_ir_result (float): Letzte IR-Result
            tmp_speed (int): Letzte gemerkte Geschwindigkeit des PiCars.
            line(bool): Flag zur Erkennung der Line.
            ir_calib(config.json): Importiert die kalibrierten Werte fuer den IR-Sensor aus der config.json.
        """

        super().__init__()
        self.ir = basisklassen.Infrared()
        self._ir_matrix = (-2, -1, 0, 1, 2)
        self._sa_from_ir = {
                            -2: -40,
                            -1.5: -32,
                            -1: -23,
                            -0.5: -10,
                            0: 0,
                            0.5: 10,
                            1: 23,
                            1.5: 32,
                            2: 40,
                        }
        self._ir_sensor_analog = self.ir.get_average(2)
        self._tmp_SA = 0
        self._tmp_ir_result = 0
        self._tmp_speed = 50
        self._line = True
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
        """Ausgabe der Werte der IR-Sensoren unter Beruecksichtigung der Kalibrierten IR-Sensoren.

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
        """Ausgabe des IR-Results zum Zugriff auf Uebersetzungstabelle

        Returns:
        [float]: IR-Result fuer Lenkwinkel Lookup Tabelle
        [int]: IR-Matrix der digitalen Summe
        [int]: IR-Sensor mit dem kleinsten Wert.
        """
        # IR-Sensor auslesen und anhand maximalem Value normieren
        ir_data = np.array(self.ir_sensor_analog)
        ir_data_norm = ir_data / np.max(ir_data) * 100

        # Berechnung des Thresholds
        ir_minArg = np.argmin(ir_data_norm)
        thresVal = np.min(ir_data_norm) + (np.std(ir_data_norm) * self.IR_THRES_FAKTOR)

        # Berechnung des IR-Result
        ir_digital = np.where(ir_data_norm < thresVal, 1, 0)
        ir_digital_sum = np.sum(ir_digital)
        ir_result = np.sum((self._ir_matrix * ir_digital)) / ir_digital_sum

        return ir_result, ir_digital, ir_digital_sum, ir_minArg

    def set_steering_angle(self, ir_result):
        """Funktion setzt alle Variablen zum Lenkwinkel
        
        Args:
            sa_soll (int): Lenkwinkel auf Basis der Lookup Tabelle.
            sa_mean (list): Liste der letzten beiden Lenkwinkel.
        """
        sa_soll = self._sa_from_ir.get(ir_result)
        sa_mean = int((self._tmp_SA + sa_soll)/2)

        if self._tmp_ir_result > 0:
            self.steering_angle = self._tmp_SA = sa_soll if ir_result > self._tmp_ir_result else sa_mean
        elif self._tmp_ir_result < 0:
            self.steering_angle = self._tmp_SA = sa_soll if ir_result < self._tmp_ir_result else sa_mean
        else:
            self.steering_angle = self._tmp_SA = sa_soll

        self._tmp_ir_result = ir_result

    def check_line_condition(self, ir_result, ir_digital_sum, ir_digital):
        """Funktion prueft die notwendigen Bedingungen, ob das PiCar noch der Linie folgt.

        Args:
            _ (bool): Wahrheitswert, ob PiCar noch der Linie folgt."""

        if ir_digital_sum > 2 or np.ptp([self._tmp_ir_result, ir_result]) > 1 or (ir_digital_sum == 2 and (ir_result == 0 or abs(ir_result) == 1 or (abs(ir_result) == 0.5 and ir_digital[2] == 0))):
            return False
        else:
            return True

    def lenkFunction_5(self):
        """Funktion fuehrt die Lenk-Funktionalitaeten fuer Fahrparcour 5 aus."""

        while self._active:
            ir_result, ir_digital, ir_digital_sum, ir_minArg = self.get_ir_result()

            if not self.check_line_condition(ir_result, ir_digital_sum, ir_digital):
                self._line = False
                self._active = False
            else:
                self.set_steering_angle(ir_result)

            time.sleep(self.IF_FREQ)

    def lenkFunction_6(self):
        """Funktion fuehrt die Lenk-Funktionalitaeten fuer Fahrparcour 6 aus."""

        while self._active:

            while self._active and self._line:
                ir_result, ir_digital, ir_digital_sum, ir_minArg = self.get_ir_result()

                if not self.check_line_condition(ir_result, ir_digital_sum, ir_digital):
                    self._line = False
                    if abs(self._tmp_SA) < 20:
                        self._active = False
                    else:
                        self.steering_angle = self._tmp_SA * -1
                        self.drive(self._tmp_speed, -1)
                        
                else:
                    self.set_steering_angle(ir_result)

                time.sleep(self.IF_FREQ)
                    
            while self._active and not self._line:
                ir_result, ir_digital, ir_digital_sum, ir_minArg = self.get_ir_result()

                if self.check_line_condition(ir_result, ir_digital_sum, ir_digital):
                    self._line = True
                    self.steering_angle = self._tmp_SA
                    self.drive(self._tmp_speed, 1)

                time.sleep(self.IF_FREQ)

    def lenkFunction_7(self):
        """Funktion fuehrt die Lenk-Funktionalitaeten fuer Fahrparcour 7 aus."""
        self._active = False

    def generischerFahrparcour(self, fp=5, v=50):
        """Funtion für einen generischen Fahrparcour"""

        print(f"Fahrparcour {fp} gestartet.")
        # Starte Drive Mode
        self.startDriveMode()
        self._tmp_speed = v

        if fp == 5:
            self._worker.submit(self.lenkFunction_5)
        elif fp == 6:
            self._worker.submit(self.lenkFunction_6)
        elif fp == 7:
            self._worker.submit(self.lenkFunction_7)
        else:
            print("Kein gültiger Fahrparcour ausgewählt!")

        # Starte die Fahrt
        self.drive(v, 1)

        # Wartet auf Fertigstellung aller Threads
        self.endDriveMode(waitingWorker=True)

        # Ende Drive Mode
        print(f"Fahrparcour {fp} beendet.")

    def fp5(self, v=50):
        """Funktion für den Fahrparcour 5"""
        self.generischerFahrparcour(5, v)
        
    def fp6(self, v=50):
        """Funktion für den Fahrparcour 6"""
        self.generischerFahrparcour(6, v)

    def fp7(self, v=50):
        """Funktion für den Fahrparcour 7"""
        self.generischerFahrparcour(7, v)

    def test_ir(self):
        """Funktion gibt 10 Messwerte des IR-Sensors aus."""

        for i in range(10):
            print(self.ir_sensor_analog)
            time.sleep(self.IF_FREQ)

    def calibrate_ir_sensors(self):
        """Funktion kalibriert die IR-Sensoren unter hellem Untergrund (Weisses Blatt).

        Returns:
        [config.json]: Fuegt den Key: "ir_calib" hinzu.
        """
        while True:
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


class Datenlogger:
    """Datenlogger Klasse

    Funktion:
    Speichert übergebene Tupels oder Listen mit Angabe des Zeitdeltas seid Start der Aufzeichnung in ein json-File

    Returns:
        [*json]: Messwerte aus uebergebenen Daten mit bliebigem Interval.
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
        """Funktion startet den Datenlogger"""

        self._logger_running = True
        self._start_timestamp = time.time()
        self._log_file["start"] = str(datetime.now()).partition(".")[0]

    def append(self, data):
        """Funktionen fuegt Daten in die Liste des Datenloggers hinzu."""

        if self._logger_running:
            ts = round((time.time() - self._start_timestamp), 2)
            self._log_data.append([ts] + data)

    def save(self):
        """Funktion speichert die uebergebenen Daten"""

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
    Main-Programm: Manuelles Ansteuern der implementierten Fahrparcours 1-7

    Args[Klassen]:
                    PiCar.BaseCar()
                    PiCar.Sonic()
                    PiCar.SensorCar()
    Funktionen der Klassen:
                    fp1() - fp7()
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
    warnung = "ACHTUNG! Das Auto wird ein Stück fahren!\n Dücken Sie ENTER zum Start."

    if modus == None:
        print("--" * 20)
        print("Auswahl:")
        for m in modi.keys():
            print("{i} - {name}".format(i=m, name=modi[m]))
        print("--" * 20)

    while modus == None:
        modus = input("Wähle  (Andere Taste für Abbruch): ? ")
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
        x = input(warnung)
        if x == "":
            SensorCar().fp1()
        else:
            print("Abbruch")

    if modus == 2:
        x = input(warnung)
        if x == "":
            SensorCar().fp2()
        else:
            print("Abbruch")

    if modus == 3:
        x = input(warnung)
        if x == "":
            SensorCar().fp3()
        else:
            print("Abbruch")

    if modus == 4:
        x = input(warnung)
        if x == "":
            SensorCar().fp4()
        else:
            print("Abbruch")

    if modus == 5:
        x = input(warnung)
        if x == "":
            SensorCar().fp5()
        else:
            print("Abbruch")

    if modus == 6:
        x = input(warnung)
        if x == "":
            SensorCar().fp6()
        else:
            print("Abbruch")

    if modus == 7:
        x = input(warnung)
        if x == "":
            SensorCar().fp7()
        else:
            print("Abbruch")

    if modus == 9:
        SensorCar().test_ir()


if __name__ == "__main__":
    main()
