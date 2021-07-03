"""Database wrapper

Simple interface to save and load event data of a postgres database.
"""

import os
import psycopg2
import psycopg2.extras

# Setup database
PREFIX = ''
if os.getenv("MODE") == "DEV":
    PREFIX = "DEV_"
DB_HOST = os.getenv(PREFIX+"DB_HOST")
DB_PW = os.getenv(PREFIX+"DB_PW")
DB_USER = os.getenv(PREFIX+"DB_USER")
DB_NAME = os.getenv(PREFIX+"DB_NAME")
print(f"DATABASE-INFO: HOST={DB_HOST},USER={DB_HOST},PW={'*'*len(DB_PW)},NAME={DB_NAME}")

class DBConnector():
    """
    Class helper to connect with a database using psycopg2.
    Allows to connect to database with python command:

    with DBConnector() as conn:
        # do something
    """
    def __init__(self,host=DB_HOST,user=DB_USER,password=DB_PW,database=DB_NAME):
        self.host = host
        self.user = user
        self.password = password
        self.database = database
    def __enter__(self):
        self.conn = psycopg2.connect(host=self.host,user=self.user,password=self.password,database=self.database)
        self.cur = self.conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        return self.cur
    def __exit__(self, type, value, traceback):
        self.conn.commit()
        self.cur.close()
        self.conn.close()

class DBEvent():
    """
    Class helper for saving events into an event-database.
    """
    def __init__(self,host=DB_HOST,user=DB_USER,password=DB_PW,database=DB_NAME):
        self.connector = DBConnector(host=host,user=user,password=password,database=database)
    def createDatabase(self):
        """Creates database if not present."""
        with self.connector as cur:
            cur.execute(f"""CREATE TABLE events (
                    id VARCHAR NOT NULL,
                    name VARCHAR NOT NULL,
                    description TEXT,
                    url VARCHAR,
                    img VARCHAR,
                    date_start DATE NOT NULL,
                    date_end DATE,
                    date_fuzzy VARCHAR,
                    time_start TIME WITH TIME ZONE,
                    time_end TIME WITH TIME ZONE,
                    location VARCHAR,
                    cost VARCHAR,
                    status VARCHAR,
                    other VARCHAR,
                    visibility VARCHAR,
                    source VARCHAR,
                    date_added TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT current_timestamp,
                    CONSTRAINT PK_event PRIMARY KEY (id, date_start)
                );""")
    def printTable(self):
        """Print all records in database"""
        with self.connector as cur:
            cur.execute(f"SELECT * FROM events;")
            print(cur.fetchall())
    def insertEvents(self, events):
        """Inserts events into database"""
        with self.connector as cur:
            query = f"""INSERT INTO events (id, name, description, url, img, date_start, date_end, date_fuzzy, time_start, time_end, location, cost, status, other, visibility, source) VALUES """
            for event in events:
                id = event.id
                name = event.name
                description = event.description.replace("'","''")
                url = event.url
                img = event.img
                date_start = event.date_start if event.date_start else 'NULL'
                date_end = event.date_end if event.date_end else 'NULL'
                date_fuzzy = event.date_fuzzy if event.date_fuzzy else 'NULL'
                time_start = event.time_start if event.time_start else 'NULL'
                time_end = event.time_end if event.time_end else 'NULL'
                location = event.location
                cost = event.cost
                status = event.status
                other = event.other if event.other else 'NULL'
                visibility = event.visibility
                source = event.source
                query += f"('{id}', '{name}', '{description}', '{url}', '{img}', '{date_start}', '{date_end}', '{date_fuzzy}', '{time_start}', '{time_end}', '{location}', '{cost}', '{status}', '{other}', '{visibility}', '{source}'),"
            query = query.strip(',') + ' ON CONFLICT ON CONSTRAINT PK_event DO UPDATE SET name=EXCLUDED.name, description=EXCLUDED.description, url=EXCLUDED.url, img=EXCLUDED.img, date_end=EXCLUDED.date_end, date_fuzzy=EXCLUDED.date_fuzzy, time_start=EXCLUDED.time_start, time_end=EXCLUDED.time_end, location=EXCLUDED.location, cost=EXCLUDED.cost, status=EXCLUDED.status, other=EXCLUDED.other, visibility=EXCLUDED.visibility, source=EXCLUDED.source;'
            query = query.replace("'NULL'", "NULL")
            cur.execute(query)


def createAllDatabase():
    """Creates all databases if they don't exist yet."""
    eventDB.createDatabase()
    print("[INFO] created database EVENTS.")


# Open database connections
eventDB = DBEvent(host=DB_HOST, user=DB_USER, password=DB_PW, database=DB_NAME)


if __name__ == '__main__':
    # createAllDatabase()
    eventDB.printTable()
