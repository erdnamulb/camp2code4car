from basisklassen import *
import traceback



try:
    #Wackeln mit den Vorderrädern als Gruß
    fw = Front_Wheels()
    print(fw.get_angles)
    fw.turn(45)
    time.sleep(.5)
    fw.turn(135)
    time.sleep(.5)
    fw.turn(90)
    
    
    
    bw = Back_Wheels()
    bw.speed = 100
    bw.forward()
    time.sleep(2)
    bw.backward()
    time.sleep(2)
    bw.stop()
    
except:
    print('-- FEHLER --')
    print(traceback.format_exc())

def main(modus):
    """Main Function for Executing the tasks


    Args:
        modus (int): The mode that can be choosen by the user
    """
    print('-- Fahrparcours --------------------')
    modi = {
        1: 'Fahrparcours 1 - Vorwärts und Rückwärts',
        2: 'Fahrparcours 2 - Kreisfahrt mit max. Lenkwinkel',
        3: 'Fahrparcours 3 - Vorwärtsfahrt bis Hindernis',
        4: 'Fahrparcours 4 - Erkundungstour',
        5: 'Fahrparcours 5 - Linienverfolgung',
        6: 'Fahrparcours 6 - Erweiterte Linienverfolgung',
        7: 'Fahrparcours 7 - 6. + Hinderniserkennung',
    }

    if modus == None:
        print('--' * 20)
        print('Auswahl:')
        for m in modi.keys():
            print('{i} - {name}'.format(i=m, name=modi[m]))
        print('--' * 20)

    while modus == None:
        modus = input('Wähle  (Andere Taste für Abbruch): ? ')
        if modus in ['1', '2', '3', '4', '5']:
            break
        else:
            modus = None
            print('Getroffene Auswahl nicht möglich.')
            quit()
    modus = int(modus)

    if modus == 0:
        print('Ausrichtung der Vorderräder')
        fw = Front_Wheels()
        fw.turn(45)
        time.sleep(.5)
        fw.turn(135)
        time.sleep(.5)
        print('Servo der Lenkung auf 90 Grad/geradeaus ausgerichtet! (CRTL-C zum beenden)')
        while True:
            fw.turn(90)
            time.sleep(1)

    if modus == 1:
        x = input('ACHTUNG! Das Auto wird ein Stück fahren!\n Dücken Sie ENTER zum Start.')
        print('Test Hinterräder')
        if x == '':
            bw = Back_Wheels()
            bw.test()
        else:
            print('Abruch.')

    if modus == 2:
        print('Test Vorderräder')
        fw = Front_Wheels()
        fw.test()

    if modus == 3:
        print('Test Ultrasonic')
        usm = Ultrasonic()
        usm.test()

    if modus == 4:
        print('Test Infrared')
        irm = Infrared()
        irm.test()
    
    if modus == 5:
        with open("config.json", "r") as f:
            data = json.load(f)
            turning_offset = data["turning_offset"]
            forward_A = data["forward_A"]
            forward_B = data["forward_B"]
            print("Test der Lenkkalibrierung in config.json")
            print("Turning Offset: ", turning_offset)
            print("Forward A: ", forward_A)
            print("Forward B: ", forward_B)

        fw = Front_Wheels(turning_offset=turning_offset)
        fw.test()
        time.sleep(1)
        bw = Back_Wheels(forward_A=forward_A, forward_B=forward_B)
        bw.test()

        print('Ende des Tests der Lenkkalibrierung in config.json')

if __name__ == '__main__':
    main()
