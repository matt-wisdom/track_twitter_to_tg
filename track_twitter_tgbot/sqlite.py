import sqlite3
import logging

logger = logging.getLogger(__name__)

db_file = "data.db"


def create_connection(db_file: str):
    """create a database connection to the SQLite database
        specified by the db_file
    :param db_file: database file
    :return: Connection object or None
    """
    conn = None
    try:
        conn = sqlite3.connect(db_file, check_same_thread=False, isolation_level=None)
    except Exception as e:
        print("Error opening db file")
    try:
        conn.execute(
            """CREATE TABLE IF NOT EXISTS DATA
                        (ID INT PRIMARY KEY NOT NULL);"""
        )
    except Exception as e:
        print(e)

    return conn


def select(conn: sqlite3.Connection, tweet_id: int):
    """
    Query tasks by priority
    :param conn: the Connection object
    :param priority:
    :return:
    """
    cur = conn.cursor()
    cur.execute(f"SELECT * FROM DATA where ID=?", tweet_id)

    row = cur.fetchone()
    return row


def insert(conn: sqlite3.Connection, data: int):
    """
    Query tasks by priority
    :param conn: the Connection object
    :param priority:
    :return:
    """
    conn.execute(f"""INSERT INTO DATA (ID) VALUES (?)""", data)
    conn.commit()
