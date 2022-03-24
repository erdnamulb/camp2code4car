import sqlite3
import datetime as dt
import pandas as pd


# Dataframe Handling:

def init_dataframe(df_name):
    '''Dataframe df_name initial erzeugen und mit '0' in erster Zeile befüllen. 
    
    Returns
    -------
    df_name
        dataframe df_name mit Spalten: timestamp, distance, irvalue, speed, direction, angle
    '''

    data = {'timestamp':  [0],
        'distance': [0],
        'irvalue': [0],
        'speed': [0],
        'direction': [0],
        'angle': [0]
        }
    df_name = pd.DataFrame(data)
    return df_name


def add_row_df(df_name, dist, irval, speed, dir, ang):
    '''Dataframe df_name um eine Zeile mit den übergebenen Werten erweitern. 
    Spalten: timestamp, distance, irvalue, speed, direction, angle

    Returns
    -------
    df_name
        dataframe df_name mit neuen Werten in zusätzlicher Zeile.
    '''

    i = df_name.index.size
    time = str(dt.datetime.timestamp(dt.datetime.now()))
    df_name.loc[i+1] = (time , dist , irval , speed , dir , ang)
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
        print("connection success")
    except Error as e:
        print(e)

    return conn


# Funktionen zum Anlegen von Datenbanken:

def makedatabase_multitable(name: str):
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


# Funktionen für Multitable-Datenbank:

def add_usm(name, value):
    '''Hinzufügen von Werten aus Ultraschallsensor 
        mit Zeitstempel zum Zeitpunkt des Schreibens'''
    time = str(dt.datetime.timestamp(dt.datetime.now()))
    db = create_connection(name)
    db.execute("""
        INSERT INTO ultrasonic 
            (timestamp, distance)
        VALUES 
            (?, ?);""",(time, value))
    db.commit()
    db.close()


def add_driving(name, value1, value2):
    '''Hinzufügen von Geschwindigkeitswerten 
        mit Zeitstempel zum Zeitpunkt des Schreibens'''
    time = str(dt.datetime.timestamp(dt.datetime.now()))
    db = create_connection(name)
    db.execute("""
        INSERT INTO driving 
            (timestamp, speed, direction)
        VALUES 
            (?, ?, ?);""",(time, value1, value2))
    db.commit()
    db.close()


def add_steering(name, value):
    '''Hinzufügen von Werten aus Ultraschallsensor 
        mit Zeitstempel zum Zeitpunkt des Schreibens'''
    time = str(dt.datetime.timestamp(dt.datetime.now()))
    db = create_connection(name)
    db.execute("""
        INSERT INTO steering 
            (timestamp, angle)
        VALUES 
            (?, ?);""",(time, value))
    db.commit()
    db.close()


def read_steering(name):
    db = create_connection(name)
    cur = db.cursor()
    cur.execute("SELECT * FROM steering")
    rows = cur.fetchall()
    for row in rows:
        print(row)
    db.close()


def read_driving(name):
    db = create_connection(name)
    cur = db.cursor()
    cur.execute("SELECT * FROM driving")
    rows = cur.fetchall()
    for row in rows:
        print(row)
    db.close()


def read_usm(name):
    db = create_connection(name)
    cur = db.cursor()
    cur.execute("SELECT * FROM ultrasonic")
    rows = cur.fetchall()
    for row in rows:
        print(row)
    db.close()


def read_infrared(name):
    db = create_connection(name)
    cur = db.cursor()
    cur.execute("SELECT * FROM infrared")
    rows = cur.fetchall()
    for row in rows:
        print(row)
    db.close()


def read_all(name):
    db = create_connection(name)
    cur = db.cursor()
    cur.execute("SELECT * FROM ultrasonic")
    rows = cur.fetchall()
    for row in rows:
        print(row)
        cur.execute("SELECT * FROM driving")
    rows = cur.fetchall()
    for row in rows:
        print(row)
        cur.execute("SELECT * FROM steering")
    rows = cur.fetchall()
    for row in rows:
        print(row)
        cur.execute("SELECT * FROM infrared")
    rows = cur.fetchall()
    for row in rows:
        print(row)
    db.close()


# Funktionen für Singletable Datenbank:

def add_data(name, valuedist, valueir, valuespd, valuedir, valueang):
    '''Hinzufügen von Datensatz mit Zeitstempel (wird automatisch generiert) zum Zeitpunkt des Schreibens.
        Reihenfolge: Datenbankname, Ultraschall, Infrarot, Geschwindigkeit, Direcition, Lenkwinkel'''
    time = str(dt.datetime.timestamp(dt.datetime.now()))
    db = create_connection(name)
    db.execute("""
        INSERT INTO drivedata 
            (timestamp, distance, irvalue, speed, direction, angle)
        VALUES 
            (?, ?, ?, ?, ?, ?);""",(time, valuedist, valueir, valuespd, valuedir, valueang))
    db.commit()
    db.close()


def read_data(name):
    '''Auslesen aller Daten aus der Singletable-Datenbank (vollständiger DB-Name muss übergeben werden).
    Reihenfolge: Index, Zeitstempel, Ultraschall, Infrarot, Geschwindigkeit, Direcition, Lenkwinkel'''
    db = create_connection(name)
    cur = db.cursor()
    cur.execute("SELECT * FROM drivedata")
    rows = cur.fetchall()
    for row in rows:
        print(row)
    db.close()


