import sys 
import click

sys.path.append('/home/pi/Projektphase1/camp2code4car/camp2code-project_phase_1/Code')
from basisklassen import *


bw = Back_Wheels()
fw = Front_Wheels()

class BaseCar():
    
    def __init__(self):
        self._steering_angle = 90
        self._speed = 0
        self._direction = 0
        
    @property
    def speed(self):
        return self._speed
        
    @property
    def direction(self, direct: int):
        return self._direction

    @property
    def steering_angle(self):
        return self._steering_angle

    @steering_angle.setter
    def steering_angle(self, angle):
        self._steering_angle = angle
        fw.turn(angle)

    def stop(self):
        bw.stop()
    
    def drive(self, speed: int, direction: int):
        self._direction = direction
        if direction == 1: #vorwärts
            bw.forward()
        elif direction == -1: #rückwärts
            bw.backward()
        else: # alles andere = stop
            self.stop()

        self._speed = speed
        bw.speed = speed

car = BaseCar()


usm = Ultrasonic()
irm = Infrared()

class SonicCar(BaseCar):
    def __init__(self):
        super().__init__()

        @property
        def distance(self):
            return self._distance

    def ValueInfrarot(self) -> None:
        """Misst durchgehend Werte für Hindernisse 
        """
        for i in range(10):
            distance = self.distance()
            if distance < 0:
                unit = 'Error'
            else:
                unit = 'cm'
            print('{} : {} {}'.format(i, distance, unit))
            time.sleep(.5)

Sonic = SonicCar()


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
        
    if modus == 6:
        print('Test Ultrasonic')
        Sonic.ValueInfrarot()


        


if __name__ == '__main__':
    main()

