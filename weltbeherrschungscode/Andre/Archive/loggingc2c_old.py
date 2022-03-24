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


def add_usm(name, value):
    '''Hinzufügen von Werten aus Ultraschallsensor 
        mit Zeitstempel zum Zeitpunkt des Schreibens'''
    time = str(dt.datetime.timestamp(dt.datetime.now()))
    try:
        sqliteConnection = sqlite3.connect(name)
        cursor = sqliteConnection.cursor()
        print("Successfully Connected to SQLite")
        sqlite_insert_query = """INSERT INTO ultrasonic
                            (timestamp, distance) 
                            VALUES 
                            ( ?, ?)"""
        count = cursor.execute(sqlite_insert_query, (time, value))
        sqliteConnection.commit()
        print("Record inserted successfully into ultrasonic table ", cursor.rowcount)
        cursor.close()
    except sqlite3.Error as error:
        print("Failed to insert data into sqlite table", error)
    finally:
        if sqliteConnection:
            sqliteConnection.close()
            print("The SQLite connection is closed")

    ''' db = create_connection(name)
    db.execute("""
        INSERT INTO ultrasonic 
            (timestamp, distance)
        VALUES 
            (time, value);""")
    db.commit()
    db.close()
    '''


def read_usm(name):
    db = create_connection(name)
    cur = db.cursor()
    cur.execute("SELECT * FROM ultrasonic")
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
