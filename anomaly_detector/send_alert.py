import random
import time

import psycopg2


def connect():
    connection = psycopg2.connect(database="test", user="test", password="test", host="localhost", port=5432)
    cursor = connection.cursor()
    return connection, cursor


def initialize(cursor):
    cursor.execute("DROP SCHEMA alerts CASCADE;")
    cursor.execute("CREATE SCHEMA alerts;")
    cursor.execute("CREATE TABLE alerts.cpu (id serial, time timestamp, expected float, actual float, diff float);")
    cursor.execute("CREATE TABLE alerts.ram (id serial, time timestamp, expected float, actual float, diff float);")
    cursor.execute("CREATE TABLE alerts.swap (id serial, time timestamp, expected float, actual float, diff float);")
    cursor.execute("CREATE TABLE alerts.disk (id serial, time timestamp, expected float, actual float, diff float);")


def send_alert(cursor):
    metric = random.choice(["cpu", "ram", "swap", "disk"])
    actual = random.randint(70, 100)
    expected = random.randint(20, 50)
    diff = (actual - expected) / expected * 100
    time.sleep(random.randint(1, 5))
    cursor.execute(f"INSERT INTO alerts.{metric} (time, expected, actual, diff) VALUES "
                   f"(now(), {expected}, {actual}, {diff});")


if __name__ == "__main__":
    connection, cursor = connect()
    initialize(cursor)
    connection.commit()
    for _ in range(20):
        send_alert(cursor)
        connection.commit()
    cursor.close()
    connection.close()
