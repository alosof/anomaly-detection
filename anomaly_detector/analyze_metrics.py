import json
from collections import defaultdict
from pathlib import Path
from typing import Dict

import joblib
import loguru
import pandas as pd
import psycopg2
from paho.mqtt.client import Client
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_percentage_error

from config.config import Config


def analyze():
    mqtt_host = "localhost"
    mqtt_port = 1883
    client = connect_queue(mqtt_host, mqtt_port)
    client.subscribe("metrics")
    client.loop_forever()


def on_message(client, userdata, msg):
    global conf
    global models
    global cursor
    global connection

    cols = conf.active_metrics()

    message = json.loads(msg.payload.decode("utf-8"))
    observation = pd.DataFrame(data=[[message[col] for col in cols]], columns=cols)

    real = observation.iloc[0].tolist()
    preds = [float(models[col].predict(observation.drop(columns=col))) for col in cols]
    errors = [mean_absolute_percentage_error([r], [p]) for (r, p) in zip(real, preds)]

    for i, err in enumerate(errors):
        if err > conf.tolerance(cols[i]):
            send_alert(cursor, cols[i], real[i], preds[i], 100 * err)
            connection.commit()
            loguru.logger.warning(
                f"ANOMALY on {cols[i]}: expected {preds[i]} +/- {100 * conf.tolerance(cols[i])}%, found {real[i]}. Error = {100 * err}"
            )


def send_alert(_cursor, metric, expected, actual, diff):
    _cursor.execute(f"INSERT INTO alerts.{metric} (time, expected, actual, diff) VALUES "
                    f"(now(), {expected}, {actual}, {diff});")


def connect_db():
    _connection = psycopg2.connect(database="test", user="test", password="test", host="localhost", port=5432)
    _cursor = _connection.cursor()
    return _connection, _cursor


def connect_queue(mqtt_host: str, mqtt_port: int) -> Client:
    client = Client()
    client.on_message = on_message
    client.connect(mqtt_host, mqtt_port)
    return client


if __name__ == "__main__":
    conf = Config()

    models: Dict[str, LinearRegression] = defaultdict()

    for f in (Path(__file__).parent / "models").glob("*.joblib"):
        metric_name = f.with_suffix("").name.split("_", maxsplit=1)[-1]
        models[metric_name] = joblib.load(f)

    connection, cursor = connect_db()

    analyze()

    cursor.close()
    connection.close()
