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
        print("connection success")
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
