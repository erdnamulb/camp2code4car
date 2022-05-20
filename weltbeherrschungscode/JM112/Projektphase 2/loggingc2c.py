import sqlite3
import datetime as dt
import pandas as pd


# Dataframe Handling:

def init_dataframe():
    """Dataframe df_name initial erzeugen und mit '0' in erster Zeile befüllen.
        Beispiel: my_dataframe = init_dataframe()

    Returns:
        df_name: dataframe Objekt mit Spalten (10): 
        timestamp, distance, irvalues 1-5, speed, direction, angle
    """    

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
    """Hängt ans Ende von Dataframe df_name eine Zeile mit den übergebenen Werten (Args) an.

    Args:
        df_name (string): Name des Dataframe
        dist (int): Ultraschall Abstandswert 
        irval (list): Infrarot Sensorwerte (Liste aus 5 Elementen (int))
        speed (int): Setzwert Geschwindigkeit 
        dir (int): Setzwert Richtung 
        ang (int): Setzwert Lenkwinkel

    Returns:
        df_name: Aktualisiertes Dataframe Objekt
    """    
    
    ir1 = irval[0]
    ir2 = irval[1]
    ir3 = irval[2]
    ir4 = irval[3]
    ir5 = irval[4]
    i = df_name.index.size
    time = str(dt.datetime.timestamp(dt.datetime.now()))
    df_name.loc[i] = (time , dist , ir1, ir2, ir3, ir4, ir5 , speed , dir , ang)
    return df_name


# Datenbank Verbindung herstellen:

def create_connection(path: str):
    """Erstellt ein Verbindungsobjekt zur SQLite Datenbank db_file.
        Beispiel: my_conn = create_connection('db_path')

    Args:
        path (string): database file

    Returns:
        _type_: Connection object oder None
    """
    
    conn = None
    try:
        conn = sqlite3.connect(path)
    except Exception as e:
        print(e)

    return conn


# Funktionen zum Anlegen der Datenbank:

def makedatabase(path: str):
    """Anlegen einer Datenbank mit der Tabelle 'drivedata' (voreingestellt) mit den Spalten:
        timestamp,
        distance,
        ir1,
        ir2,
        ir3,
        ir4,
        ir5,
        speed,
        direction,
        angle

    Args:
        path (str): Name der Datenbank (z.B. 'mydatabase.sql')
    """    

    try:
        db = sqlite3.connect(path)

        db.execute("""
            CREATE TABLE drivedata (
                id INTEGER
                , timestamp VARCHAR(20)
                , distance INTEGER
                , ir1 INTEGER
                , ir2 INTEGER
                , ir3 INTEGER
                , ir4 INTEGER
                , ir5 INTEGER
                , speed INTEGER
                , direction INTEGER
                , angle INTEGER
                , PRIMARY KEY(id))""")
        
        db.commit()
        db.close()
        print("Datenbank {} erstellt.",format(path))
    except:
        print('Datenbank existiert schon.')


# Funktionen für Schreiben und Lesen der Datenbank:

def add_data(path: str, valuedist, valueir, valuespd, valuedir, valueang):
    """Hinzufügen zu Tabelle 'drivedata' (fest definiert) von Datensatz mit Zeitstempel (wird automatisch generiert) zum Zeitpunkt des Schreibens.
        Reihenfolge: Datenbankname, Ultraschall, Infrarot (Liste mit 5 Elementen), Geschwindigkeit, Direcition, Lenkwinkel

    Args:
        path (string): Datenbankname
        valuedist (_type_): Ultraschall Abstandswert (int)
        valueir (_type_): Infrarot Sensorwerte (Liste aus 5 Elementen (int))
        valuespd (_type_): Setzwert Geschwindigkeit (int)
        valuedir (_type_): Setzwert Richtung (int)
        valueang (_type_): Setzwert Lenkwinkel (int)
    """    
    
    ir1 = valueir[0]
    ir2 = valueir[1]
    ir3 = valueir[2]
    ir4 = valueir[3]
    ir5 = valueir[4]
    time = str(dt.datetime.timestamp(dt.datetime.now()))
    db = create_connection(path)
    db.execute("""
        INSERT INTO drivedata 
            (timestamp, distance, ir1, ir2, ir3, ir4, ir5, speed, direction, angle)
        VALUES 
            (?, ?, ?, ?, ?, ?, ?, ?, ?, ?);""",(time, valuedist, valueir, valuespd, valuedir, valueang))
    db.commit()
    db.close()


def read_data(path: str):
    """Auslesen der kompletten Tabelle 'drivedata' (vordefiniert) aus Datenbank 'name' mit den Spalten:
        Ultraschall, Infrarot 1 , Infrarot 2 , Infrarot 3 , Infrarot 4 , Infrarot 5, Geschwindigkeit, Direcition, Lenkwinkel

    Args:
        path (string): Datenbankname + Pfrad
    """ 
    db = create_connection(path)
    cur = db.cursor()
    cur.execute("SELECT * FROM drivedata")
    rows = cur.fetchall()
    for row in rows:
        print(row)
    db.close()

def write_log_to_db(path: str, df: pd.DataFrame):
        """Function to save log Dataframe to sqlite DB

        Args:
        path (string): Datenbankname + Pfrad
        """
        conn = create_connection(path)
        df.to_sql('drivedata', conn, if_exists='append', index = False)
        print("Dataframe succesfully written to sqlite DB")
