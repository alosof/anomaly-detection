import json
import time
from os.path import expanduser
from pathlib import Path

import click
import loguru
import psutil
from paho.mqtt.client import Client


@click.command()
@click.option("-d", "--destination", type=click.Choice(['file', 'broker']))
def generate(destination: str) -> None:
    if destination == 'file':
        write_to_file()
    else:
        send_to_broker()


def send_to_broker():
    mqtt_host = "localhost"
    mqtt_port = 1883
    client = connect(mqtt_host, mqtt_port)
    while True:
        time.sleep(0.2)
        values = measure_metrics()
        client.publish("metrics", json.dumps(values))


def write_to_file():
    data_path: str = Path(__file__).parent.parent / "anomaly_detector" / "data" / "data.csv"
    cols = ["cpu", "ram", "swap", "disk"]
    lines = []
    while len(lines) < 5000:
        time.sleep(0.1)
        values = measure_metrics()
        if values["cpu"] > 0.:
            lines.append(",".join([str(values[col]) for col in cols]) + "\n")
            if len(lines) % 50 == 0:
                loguru.logger.info(f"{len(lines)} training rows generated.")
    with open(data_path, 'w') as f:
        f.write(",".join(cols) + "\n")
        f.writelines(lines)


def connect(mqtt_host: str, mqtt_port: int) -> Client:
    client = Client()
    client.connect(mqtt_host, mqtt_port)
    return client


def measure_metrics() -> dict[str, float]:
    metrics = {
        "cpu": psutil.cpu_percent(),
        "ram": psutil.virtual_memory().percent,
        "swap": psutil.swap_memory().percent,
        "disk": psutil.disk_usage(expanduser("~")).percent
    }
    return metrics


if __name__ == "__main__":
    generate()
