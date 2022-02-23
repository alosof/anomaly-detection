from pathlib import Path
from typing import List

import yaml


class Config:

    def __init__(self):
        self.path = Path(__file__).parent / "config.yml"
        self.config = self.load()
        self.metrics = self.config["metrics"]

    def load(self):
        with open(self.path) as f:
            config = yaml.safe_load(f.read())
        return config

    def active_metrics(self) -> List[str]:
        return [metric for metric in self.metrics.keys() if self.metrics[metric]["active"] is True]

    def tolerance(self, metric: str) -> float:
        return self.metrics[metric]["tolerance"]
