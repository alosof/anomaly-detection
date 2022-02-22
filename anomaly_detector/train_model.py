from collections import defaultdict
from pathlib import Path

import pandas as pd
from joblib import dump
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_percentage_error


def train(df_train):
    models = defaultdict()
    for col in df_train.columns:
        model = LinearRegression()
        model.fit(df_train.drop(columns=[col]).values, df_train[col].values)
        models[col] = model
    return models


def evaluate(trained_models, df_test):
    for col in df_test.columns:
        model = trained_models[col]
        pred = model.predict(df_test.drop(columns=col).values)
        print(f'Error for {col}: {round(mean_absolute_percentage_error(pred, df_test[col]) * 100, 2)}%')


if __name__ == "__main__":
    df = pd.read_csv(Path(__file__).parent / "data" / "data.csv")

    n_train = int(df.shape[0] * 0.7)
    train_data = df.iloc[:n_train]
    test_data = df.iloc[n_train:]

    models = train(train_data)
    for col, model in models.items():
        dump(model, Path(__file__).parent / "models" / f"model_{col}.joblib")

    evaluate(models, test_data)
