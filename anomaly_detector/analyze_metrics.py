import json
from collections import defaultdict
from pathlib import Path

import loguru
import psycopg2
from joblib import load
from paho.mqtt.client import Client
from sklearn.metrics import mean_absolute_percentage_error


def analyze():
    mqtt_host = "localhost"
    mqtt_port = 1883
    client = connect_queue(mqtt_host, mqtt_port)
    client.subscribe("metrics")
    client.loop_forever()


def on_message(client, userdata, msg):
    global models
    global cursor
    global connection

    message = json.loads(msg.payload.decode("utf-8"))

    if message["cpu"] > 0:
        cols = ["cpu", "ram", "swap", "disk"]

        real = [message[col] for col in cols]
        preds = [float(models[col].predict([[message[c] for c in cols if c != col]])) for col in cols]

        errors = [mean_absolute_percentage_error([r], [p]) for (r, p) in zip(real, preds)]

        for i, err in enumerate(errors):
            if err > 0.3:
                send_alert(cursor, cols[i], real[i], preds[i], 100 * err)
                connection.commit()
                loguru.logger.warning(f"ERROR on {cols[i]}: expected {real[i]} +/- 30%, found {preds[i]}. Error = {100 * err}")


def connect():
    connection = psycopg2.connect(database="test", user="test", password="test", host="localhost", port=5432)
    cursor = connection.cursor()
    return connection, cursor


def send_alert(cursor, metric, expected, actual, diff):
    cursor.execute(f"INSERT INTO alerts.{metric} (time, expected, actual, diff) VALUES "
                   f"(now(), {expected}, {actual}, {diff});")


def connect_queue(mqtt_host: str, mqtt_port: int) -> Client:
    client = Client()
    client.on_message = on_message
    client.connect(mqtt_host, mqtt_port)
    return client


if __name__ == "__main__":
    models = defaultdict()
    for f in (Path(__file__).parent / "models").glob("*.joblib"):
        models[f.with_suffix("").name.split("_", maxsplit=1)[-1]] = load(f)

    connection, cursor = connect()

    analyze()

    cursor.close()
    connection.close()
