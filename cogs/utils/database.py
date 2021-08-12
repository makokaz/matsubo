"""Database wrapper

Simple interface to save and load event data of a postgres database.
"""

import os
import psycopg2
import psycopg2.extras
import datetime
from .event import Event

# Setup database
DB_HOST = os.getenv("DB_HOST")
DB_PW = os.getenv("DB_PW")
DB_USER = os.getenv("DB_USER")
DB_NAME = os.getenv("DB_NAME")
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
    TABLE = "events"
    def __init__(self,host=DB_HOST,user=DB_USER,password=DB_PW,database=DB_NAME):
        self.connector = DBConnector(host=host,user=user,password=password,database=database)
    def createTable(self):
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
                );""") #BUG: current_timestamp will use timezone of PC, but it should use Japan timezone!
    def printTable(self):
        """Print all records in database"""
        with self.connector as cur:
            cur.execute(f"SELECT * FROM events;")
            print(cur.fetchall())
    def getEvents(self, visibility:list[str]=None, from_date:datetime.datetime.date=None, until_date:datetime.datetime.date=None) -> list[Event]:
        """Return events of given visibility, in the given date duration"""
        with self.connector as cur:
            # Construct query and data based on arguments given
            query = f"set time zone 'Asia/Tokyo'; SELECT * FROM {self.TABLE} WHERE "
            data = ()
            if visibility:
                query += f"(visibility = ANY(%s)) AND "
                data += (visibility,)
            if from_date:
                query += f"date_start >= %s AND "
                data += (from_date,)
            if until_date:
                query += f"date_end <= %s AND "
                data += (until_date,)
            query = query.rstrip(' AND ').rstrip(' WHERE ')
            query += f";"
            # Execute query
            cur.execute(query, data)
            # Construct Event objects and return them as a list
            events = []
            for ret in cur:
                event = Event(id=ret[0], name=ret[1], description=ret[2], url=ret[3], img=ret[4], date_start=ret[5], date_end=ret[6],
                                date_fuzzy=ret[7], time_start=ret[8], time_end=ret[9], location=ret[10], cost=ret[11], status=ret[12],
                                other=ret[13], visibility=ret[14], source=ret[15], date_added=ret[16])
                events.append(event)
            return events
    def insertEvents(self, events):
        """Inserts events into database"""
        with self.connector as cur:
            query = f"""set time zone 'Asia/Tokyo'; INSERT INTO events (id, name, description, url, img, date_start, date_end, date_fuzzy, time_start, time_end, location, cost, status, other, visibility, source) VALUES """
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


class DBDiscord():
    """
    Class helper for saving Discord-related data, for example:
    - Where should events be posted
    - ...
    """
    TABLE = "discord"
    def __init__(self,host=DB_HOST,user=DB_USER,password=DB_PW,database=DB_NAME):
        self.connector = DBConnector(host=host,user=user,password=password,database=database)
    def createTable(self):
        """Creates table if not present."""
        with self.connector as cur:
            cur.execute(f"""CREATE TABLE {self.TABLE} (
                    channel_id BIGINT NOT NULL,
                    visibility VARCHAR[],
                    CONSTRAINT PK_discord PRIMARY KEY (channel_id)
                );""")
    def executeQuery(self, query : str, retval : bool = False):
        """Executes any query. Returns output if retval flag is set to true."""
        with self.connector as cur:
            cur.execute(query)
            if retval:
                return cur.fetchall()
            else:
                return None
    def printTable(self):
        """Print all records in database"""
        with self.connector as cur:
            cur.execute(f"SELECT * FROM {self.TABLE};")
            print(cur.fetchall())
    def updateChannel(self, channel_id : int, visibility : list[str]):
        """Updates channel info in database. If it does not exist, it will be newly created"""
        with self.connector as cur:
            query = f"""INSERT INTO {self.TABLE} (channel_id, visibility) VALUES (%s, %s)
                        ON CONFLICT ON CONSTRAINT PK_discord DO UPDATE SET visibility=EXCLUDED.visibility;"""
            data = (channel_id, visibility)
            cur.execute(query,data)
    def getChannelVisibility(self, channel_id : int) -> set[str]:
        """Returns the visibility of events to this channel"""
        with self.connector as cur:
            cur.execute(f"SELECT visibility FROM {self.TABLE} WHERE (channel_id = %s);", (channel_id,))
            ret = cur.fetchone()
            if ret:
                return set(ret[0])
            return set([])
    def removeChannel(self, channel_id : int):
        """Removes channel from table"""
        with self.connector as cur:
            cur.execute(f"DELETE FROM {self.TABLE} WHERE (channel_id = %s);", (channel_id,))
    def getAllChannelVisibility(self):
        """Returns all channels with their visibility"""
        with self.connector as cur:
            cur.execute(f"SELECT channel_id, visibility FROM {self.TABLE};")
            return cur.fetchall()



def createDatabase():
    """Creates database (all tables) if they don't exist yet."""
    eventDB.createTable()
    print(f"[INFO] created database {eventDB.TABLE}.")
    discordDB.createTable()
    print(f"[INFO] created database {discordDB.TABLE}.")


# Open database connections
eventDB = DBEvent(host=DB_HOST, user=DB_USER, password=DB_PW, database=DB_NAME)
discordDB = DBDiscord(host=DB_HOST, user=DB_USER, password=DB_PW, database=DB_NAME)


if __name__ == '__main__':
    # createDatabase()
    #discordDB.createTable()
    discordDB.updateChannel('ch1',['kanto'])
    print(discordDB.getChannelVisibility('ch1'))
    discordDB.removeChannel('ch1')
    discordDB.printTable()
    print("Special query:")
    #print(discordDB.executeQuery(f"SELECT * FROM {discordDB.TABLE};"))
    discordDB.executeQuery(f"INSERT INTO {discordDB.TABLE} (channel_id, visibility) VALUES ('ch7', ARRAY['kanto','kansai']);")
    #print(discordDB.getChannelVisibility('abc'))
