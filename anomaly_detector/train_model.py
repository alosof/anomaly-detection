from collections import defaultdict
from pathlib import Path
from typing import Dict

import loguru
import pandas as pd
from joblib import dump
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_percentage_error

from config.config import Config


def train(df_train: pd.DataFrame) -> Dict[str, LinearRegression]:
    _models = defaultdict()
    for metric in df_train.columns:
        _model = LinearRegression()
        _model.fit(X=df_train.drop(columns=[metric]),
                   y=df_train[metric])
        _models[metric] = _model
    return _models


def evaluate(trained_models: Dict[str, LinearRegression], df_test: pd.DataFrame) -> None:
    for metric in df_test.columns:
        _model = trained_models[metric]
        pred = _model.predict(X=df_test.drop(columns=metric))
        loguru.logger.info(
            f'Error for {metric}: {round(mean_absolute_percentage_error(pred, df_test[metric]) * 100, 2)}%'
        )


if __name__ == "__main__":
    conf = Config()
    df = pd.read_csv(Path(__file__).parent / "data" / "data.csv")[conf.active_metrics()].copy()

    n_train = int(df.shape[0] * 0.7)
    train_data = df.iloc[:n_train]
    test_data = df.iloc[n_train:]

    models: Dict[str, LinearRegression] = train(train_data)

    for col, model in models.items():
        dump(model, Path(__file__).parent / "models" / f"model_{col}.joblib")

    evaluate(models, test_data)
