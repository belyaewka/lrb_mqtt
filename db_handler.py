import sqlite3 as sq
from datetime import datetime
from config import DB_NAME


def db_create(db_name):
    with sq.connect(db_name) as con:
        cur = con.cursor()
        cur.execute("""
        """)


def create_table():
    with sq.connect(DB_NAME) as con:
        cur = con.cursor()
        cur.execute("""CREATE TABLE IF NOT EXISTS temp (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT,
            time TEXT,
            temper REAL)""")


def db_record(temperature: float) -> None:
    with sq.connect(DB_NAME) as con:
        cur = con.cursor()
        date = datetime.now().strftime('%d-%m-%Y')
        cur.execute(
            f'INSERT INTO temp (date, time, temper) VALUES ("{date}",time("now", "localtime"), "{temperature}")')


if __name__ == '__main__':
    # creating new db
    try:
        db_create(DB_NAME)
    except Exception as e:
        print(f'Database creation error {e}')

    # creating new table
    try:
        create_table()
    except Exception as e:
        print(f'Table creation error {e}')
