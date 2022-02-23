import json
import time
from os.path import expanduser
from pathlib import Path
from typing import List

import click
import loguru
import psutil
from paho.mqtt.client import Client

from config.config import Config


@click.command()
@click.option("-d", "--destination", type=click.Choice(['file', 'broker', 'stdout']))
def generate(destination: str) -> None:
    conf = Config()
    active_metrics = conf.active_metrics()
    if destination == 'file':
        write_to_file(active_metrics, nb_lines=5000, sleep=0.2)
    elif destination == 'broker':
        send_to_broker(active_metrics, sleep=0.2)
    else:
        write_to_stdout(active_metrics, sleep=0.2)


def send_to_broker(active_metrics: List[str], sleep: float):
    mqtt_host = "localhost"
    mqtt_port = 1883
    client = connect(mqtt_host, mqtt_port)
    while True:
        time.sleep(sleep)
        measurement = measure_metrics(active_metrics)
        client.publish("metrics", json.dumps(measurement))


def write_to_file(active_metrics: List[str], nb_lines: int, sleep: float):
    data_path: str = Path(__file__).parent.parent / "anomaly_detector" / "data" / "data.csv"
    lines = []
    while len(lines) < nb_lines:
        time.sleep(sleep)
        measurement = measure_metrics(active_metrics)
        lines.append(",".join([str(measurement[metric]) for metric in active_metrics]) + "\n")
        if len(lines) % 50 == 0:
            loguru.logger.info(f"{len(lines)} training rows generated.")
    with open(data_path, 'w') as f:
        f.write(",".join(active_metrics) + "\n")
        f.writelines(lines)


def write_to_stdout(active_metrics: List[str], sleep: float):
    while True:
        time.sleep(sleep)
        measurement = measure_metrics(active_metrics)
        loguru.logger.info(measurement)


def connect(mqtt_host: str, mqtt_port: int) -> Client:
    client = Client()
    client.connect(mqtt_host, mqtt_port)
    return client


def measure_metrics(active_metrics: List[str]) -> dict[str, float]:
    metrics = {
        "cpu": psutil.cpu_percent,
        "cpu_temp": lambda: sum([cpu.current for cpu in psutil.sensors_temperatures()['coretemp']]) /
                            len(psutil.sensors_temperatures()['coretemp']),
        "ram": lambda: psutil.virtual_memory().percent,
        "swap": lambda: psutil.swap_memory().percent,
        "disk": lambda: psutil.disk_usage(expanduser("~")).percent
    }
    return {metric: func() for (metric, func) in metrics.items() if metric in active_metrics}


if __name__ == "__main__":
    generate()
