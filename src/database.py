"""Database wrapper

Simple interface to save and load data from database on Heroku.
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


def createDatabase(table='events'):
    """Creates database if not present."""
    with DBConnector() as cur:
        cur.execute(f"""CREATE TABLE {table}
                (id VARCHAR(30) PRIMARY KEY,
                name VARCHAR NOT NULL,
                description TEXT,
                url VARCHAR,
                img VARCHAR,
                date VARCHAR,
                time VARCHAR,
                location VARCHAR,
                cost VARCHAR,
                status VARCHAR(50),
                category VARCHAR (50),
                date_added TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT current_timestamp)
            ;""")
        print("Created database.")

def printTable(table='events'):
    with DBConnector() as cur:
        cur.execute(f"SELECT * FROM {table};")
        print(cur.fetchall())

def insertEvents(events, table='events'):
    """Inserts events into database"""
    with DBConnector() as cur:
        query = f"""INSERT INTO {table} (id, name, description, url, img, date, time, location, cost, status, category) VALUES """
        for event in events:
            id = event.id
            name = event.name
            description = event.description.replace("'","''")
            url = event.url
            img = event.img
            date = event.date
            time = event.time
            location = event.location
            cost = event.cost
            status = event.status
            category = event.category
            query += f"('{id}', '{name}', '{description}', '{url}', '{img}', '{date}', '{time}', '{location}', '{cost}', '{status}', '{category}'),"
        query = query.strip(',') + ' ON CONFLICT DO NOTHING;'
        cur.execute(query)



if __name__ == '__main__':
    printTable()
    #createDatabase()