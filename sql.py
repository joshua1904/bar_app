import os
import sqlite3
from utils import Settings

DATABASE = "test.db"
if os.environ.get("SQLFILE"):
    DATABASE = os.environ["SQLFILE"]

MIN_VALUE = 50
MAX_VALUE = 120
MIN_TIME_DIFF = 1000
TOLERANCE = 12

CREATE_STATEMENT_SERIAL_TO_NAME = """
CREATE TABLE IF NOT EXISTS serialToName (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    serial varchar(50),
    name varchar(50)
    
);
"""
CREATE_STATEMENT_SETTINGS = """
CREATE TABLE IF NOT EXISTS settings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    min_weight integer,
    max_weight integer,
    min_time_diff integer,
    tolerance integer
    
);"""

CREATE_STATEMENT_FILTER = """
CREATE TABLE IF NOT EXISTS filter (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    full integer,
    empty integer,
    not_used integer,
    offline integer
    
    
    
);"""

INSERT_STATEMENT_SERIAL_TO_NAME = """INSERT INTO serialToName (name, serial) VALUES(?, ?)"""
UPDATE_STATEMENT_SERIAL_TO_NAME = """UPDATE serialToName SET name =  ? WHERE serial = ?"""
DELETE_STATEMENT_SERIAL_TO_NAME = """DELETE FROM serialToName WHERE name = ?"""
INSERT_STATEMENT_SETTINGS = """INSERT INTO settings (min_weight, max_weight, min_time_diff, tolerance) VALUES(?, ?, ?, ?)"""
UPDATE_STATEMENT_SETTINGS = """UPDATE settings SET min_weight = ?, max_weight = ?, min_time_diff = ?, tolerance = ? WHERE id = 1"""
INSERT_STATEMENT_FILTER = """INSERT INTO filter (full, empty, not_used, offline) VALUES(?, ?, ?, ?)"""
UPDATE_STATEMENT_FILTER = """UPDATE filter SET empty = ?, full = ?, not_used = ?, offline = ? WHERE id = 1"""

def init():
    with sqlite3.connect(DATABASE) as con:
        cur = con.cursor()
        cur.execute(CREATE_STATEMENT_SERIAL_TO_NAME)
        cur.execute(CREATE_STATEMENT_SETTINGS)
        cur.execute(CREATE_STATEMENT_FILTER)
        if not get_settings():
            _add_settings(MIN_VALUE, MAX_VALUE, MIN_TIME_DIFF, TOLERANCE)
        if not get_filter():
            _add_filter()
        con.commit()


def get_filter() -> tuple:
    with sqlite3.connect(DATABASE) as con:
        cur = con.cursor()
        return cur.execute("SELECT empty, full, not_used, offline FROM filter").fetchone()


def update_filter(empty: bool, full: bool, not_used: bool, offline: bool):
    with sqlite3.connect(DATABASE) as con:
        cur = con.cursor()
        cur.execute(UPDATE_STATEMENT_FILTER, (empty, full, not_used, offline))
        con.commit()


def _add_filter():
    with sqlite3.connect(DATABASE) as con:
        cur = con.cursor()
        cur.execute(INSERT_STATEMENT_FILTER, (1, 1, 1, 1))
        con.commit()


def get_settings() -> tuple:
    with sqlite3.connect(DATABASE) as con:
        cur = con.cursor()
        return cur.execute("SELECT * FROM SETTINGS").fetchone()


def update_settings(min_weight, max_weight, min_time_diff, tolerance):
    with sqlite3.connect(DATABASE) as con:
        cur = con.cursor()
        cur.execute(UPDATE_STATEMENT_SETTINGS, (min_weight, max_weight, min_time_diff, tolerance))
        con.commit()


def _add_settings(min_weight: int, max_weight: int, min_time_diff: int, tolerance: int):
    with sqlite3.connect(DATABASE) as con:
        cur = con.cursor()
        cur.execute(INSERT_STATEMENT_SETTINGS, (min_weight, max_weight, min_time_diff, tolerance))
        con.commit()


def get_serial_name_list() -> list[tuple]:
    with sqlite3.connect(DATABASE) as con:
        cur = con.cursor()
        return cur.execute("SELECT * FROM serialToName").fetchall()


def set_serial_to_name(serial: str, name):
    with sqlite3.connect(DATABASE) as con:
        cur = con.cursor()
        if not cur.execute("SELECT * FROM serialToName WHERE serial=?", (serial,)).fetchone():
            cur.execute(INSERT_STATEMENT_SERIAL_TO_NAME, (name, serial))
        else:
            cur.execute(UPDATE_STATEMENT_SERIAL_TO_NAME, (name, serial))
        con.commit()


def get_beer_states() -> list[tuple]:
    """returns the values from the last database input of the device with the given
    serial number. (id, time_stamp, value, serial)"""
    with sqlite3.connect(DATABASE) as con:
        cur = con.cursor()
        return cur.execute(
            "SELECT stats.id, stats.time_stamp, stats.value, stats.serial, stats.last_seen, serialToName.name FROM stats Left JOIN serialToName On stats.serial = serialToName.serial").fetchall()


def delete_serial_to_name(name: str):
    with sqlite3.connect(DATABASE) as con:
        cur = con.cursor()
        if cur.execute("SELECT * FROM serialToName WHERE name = ?", (name,)).fetchone():
            return cur.execute(DELETE_STATEMENT_SERIAL_TO_NAME, (name,))
