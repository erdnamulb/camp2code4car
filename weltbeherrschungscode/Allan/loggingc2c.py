import sqlite3
import datetime as dt


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
