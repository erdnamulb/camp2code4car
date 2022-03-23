import sqlite3
import datetime as dt

def makedatabase(name: str):
    '''Anlegen einer Datenbank mit den Tabellen
        ultrasonic
        infrared
        driving
        steering'''
    try:
        db = sqlite3.connect(str+'.db')

        db.execute("""
            CREATE TABLE ultrasonic (
                id INTEGER
                , timestamp INTEGER
                , distance INTEGER
                , PRIMARY KEY(id))""")

        db.execute("""
            CREATE TABLE infrared (
                id INTEGER
                , timestamp INTEGER
                , value INTEGER
                , PRIMARY KEY(id))""")

        db.execute("""
            CREATE TABLE driving (
                id INTEGER
                , timestamp INTEGER
                , speed INTEGER
                , direction INTEGER
                , PRIMARY KEY(id))""")

        db.execute("""
            CREATE TABLE steering (
                id INTEGER
                , timestamp INTEGER
                , angle INTEGER
                , PRIMARY KEY(id))""")            
        
        db.commit()
        db.close()
        print("Datenbank erstellt.")
    except:
        print('Datenbank existiert schon.')

db = sqlite3.connect('drivedata.db')
cursor = db.Cursor()

def add_usm(time, value):
    db.execute("""
        INSERT INTO ultrasonic 
            (timestamp, distance)
        VALUES 
            (time, value)"""
    db.commit()

#db.execute(newentry_usm, (time, value))

db.commit()
print("Eintragung fertig")

print("Verifikation:")
abfrage = db.execute("""
    SELECT *
    FROM ultrasonic """)
for eintrag in abfrage:
    print(eintrag)


read_usm = "SELECT timestamp, value FROM ultrasonic"
cursor.execute(read_usm)
cursor = db.fetchall()



db.close()