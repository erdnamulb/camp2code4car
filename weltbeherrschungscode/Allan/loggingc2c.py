import sqlite3
import datetime as dt
import pandas as pd

# Dataframe Handling:

def init_dataframe():
    '''Dataframe df_name initial erzeugen und mit '0' in erster Zeile befüllen. 
    
    Returns
    -------
    df_name
        dataframe df_name mit Spalten (10): timestamp, distance, irvalues 1-5, speed, direction, angle
    '''

    data = {'timestamp':  [0],
        'distance': [0],
        'ir1': [0],
        'ir2': [0],
        'ir3': [0],
        'ir4': [0],
        'ir5': [0],
        'speed': [0],
        'direction': [0],
        'angle': [0]
        }
    df_name = pd.DataFrame(data)
    return df_name


def add_row_df(df_name, dist, irval, speed, dir, ang):
    '''Dataframe df_name um eine Zeile mit den übergebenen Werten erweitern. 
    Spalten: timestamp, distance, irvalues (Liste aus 5 Elementen), speed, direction, angle

    Returns
    -------
    df_name
        dataframe df_name mit neuen Werten in zusätzlicher Zeile.
    '''
    ir1 = irval[0]
    ir2 = irval[1]
    ir3 = irval[2]
    ir4 = irval[3]
    ir5 = irval[4]
    i = df_name.index.size
    time = str(dt.datetime.timestamp(dt.datetime.now()))
    df_name.loc[i] = (time , dist , ir1, ir2, ir3, ir4, ir5 , speed , dir , ang)
    return df_name


def create_connection(db_file):
    """ create a database connection to the SQLite database
        specified by the db_file
    :param db_file: database file
    :return: Connection object or None
    """
    conn = None
    try:
        conn = sqlite3.connect(db_file)
    except Error as e:
        print(e)

    return conn


def makedatabase(name: str):
    '''Anlegen einer Datenbank mit den Tabellen
        ultrasonic
        infrared
        driving
        steering'''
    try:
        db = sqlite3.connect(name)

        db.execute("""
            CREATE TABLE ultrasonic (
                id INTEGER
                , timestamp VARCHAR(20)
                , distance INTEGER
                , PRIMARY KEY(id))""")

        db.execute("""
            CREATE TABLE infrared (
                id INTEGER
                , timestamp VARCHAR(20)
                , value INTEGER
                , PRIMARY KEY(id))""")

        db.execute("""
            CREATE TABLE driving (
                id INTEGER
                , timestamp VARCHAR(20)
                , speed INTEGER
                , direction INTEGER
                , PRIMARY KEY(id))""")

        db.execute("""
            CREATE TABLE steering (
                id INTEGER
                , timestamp VARCHAR(20)
                , angle INTEGER
                , PRIMARY KEY(id))""")            
        
        db.commit()
        db.close()
        print("Datenbank erstellt.")
    except:
        print('Datenbank existiert schon.')

def makedatabase_singletable(name: str):
    '''Anlegen einer Datenbank mit der Tabelle
        drivedata  
            Erfasst werden 
            timestamp,
            distance,
            irvalue,
            speed,
            direction,
            angle'''
    try:
        db = sqlite3.connect(name)

        db.execute("""
            CREATE TABLE drivedata (
                id INTEGER
                , timestamp VARCHAR(20)
                , distance INTEGER
                , irvalue INTEGER
                , speed INTEGER
                , direction INTEGER
                , angle INTEGER
                , PRIMARY KEY(id))""")
        
        db.commit()
        db.close()
        print("Datenbank {} erstellt.",format(name))
    except:
        print('Datenbank existiert schon.')

def add_data(name, value1, value2, value3, value4, value5):
    '''Hinzufügen von Werten für die Multidatenbank'''
    db = create_connection(name)
    time = str(dt.datetime.timestamp(dt.datetime.now()))
    db.execute("""
        INSERT INTO drivedata
            (timestamp, distance, irvalue, speed, direction, angle)
        VALUES 
            (?, ?, ?, ?, ?, ?); """,(time, value1, value2, value3, value4, value5))
    db.commit()
    db.close()


def add_usm(name, value):
    '''Hinzufügen von Werten aus Ultraschallsensor 
        mit Zeitstempel zum Zeitpunkt des Schreibens'''
    db = create_connection(name)
    time = str(dt.datetime.timestamp(dt.datetime.now()))
    db.execute("""
        INSERT INTO ultrasonic 
            (timestamp, distance)
        VALUES 
            (?, ?); """,(time, value))
    db.commit()
    db.close()

def add_driving(name, value1, value2):
    '''Hinzufügen von Werten aus Ultraschallsensor 
        mit Zeitstempel zum Zeitpunkt des Schreibens'''
    db = create_connection(name)
    time = str(dt.datetime.timestamp(dt.datetime.now()))
    db.execute("""
        INSERT INTO driving 
            (timestamp, speed, direction)
        VALUES 
            (?, ?, ?); """,(time, value1, value2))
    db.commit()
    db.close()

def add_steering(name, value):
    '''Hinzufügen von Werten aus Ultraschallsensor 
        mit Zeitstempel zum Zeitpunkt des Schreibens'''
    db = create_connection(name)
    time = str(dt.datetime.timestamp(dt.datetime.now()))
    db.execute("""
        INSERT INTO steering 
            (timestamp, angle)
        VALUES 
            (?, ?); """,(time, value))
    db.commit()
    db.close()

def read_usm(name):
    db = create_connection(name)
    cursor = db.Cursor()
    cursor.execute("SELECT * FROM ultrasonic")
    rows = cur.fetchall()
    for row in rows:
        print(row)
    db.close()

def read_infrared(name):
    db = create_connection(name)
    cursor = db.Cursor()
    cursor.execute("SELECT * FROM infrared")
    rows = cur.fetchall()
    for row in rows:
        print(row)
    db.close()
    
def read_driving(name):
    db = create_connection(name)
    cursor = db.Cursor()
    cursor.execute("SELECT * FROM driving")
    rows = cur.fetchall()
    for row in rows:
        print(row)
    db.close()

def read_steering(name):
    db = create_connection(name)
    cursor = db.Cursor()
    cursor.execute("SELECT * FROM steering")
    rows = cur.fetchall()
    for row in rows:
        print(row)
    db.close() 
'''

#db.execute(newentry_usm, (time, value))
#db = sqlite3.connect('drivedata.db')
#cursor = db.Cursor()

print("Verifikation:")
abfrage = db.execute("""
    SELECT *
    FROM ultrasonic """)
for eintrag in abfrage:
    print(eintrag)
'''
