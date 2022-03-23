def parc1(): 
    print("Fahrparcours 1 - Vorwärts und Rückwärts")

def parc2(): 
    print("Fahrparcours 2 - Kreisfahrt mit maximalem Lenkwinkel")

def parc3(): 
    print("Fahrparcours 3 - Vorwärtsfahrt bis Hindernis")

def parc4(): 
    print("Fahrparcours 4 - Erkundungstour mit Hindernis")

def quit(): 
    print("Beende das Programm")
    
def handle_menu(menu):
    while True:
        for index, item in enumerate(menu, 1):
            print("{}  {}".format(index, item[0]))
        choice = int(input("Ihre Wahl? ")) - 1
        if 0 <= choice < len(menu):
            menu[choice][1]()
        else:
            print("Bitte nur Zahlen im Bereich 1 - {} eingeben".format(
                                                                    len(menu)))

menu = [
    ["- langsam Vorwärts und Rückwärts", parc1],
    ["- Kreisfahrt mit maximalem Lenkwinkel", parc2],
    ["- Vorwärtsfahrt bis Hindernis", parc3],
    ["- Erkundungstour", parc4],
    ["- Beenden", quit]
]

handle_menu(menu)