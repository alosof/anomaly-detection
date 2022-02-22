# Anomaly detection

## Prerequisites

```bash
pip install -r requirements.txt
```

## Quickstart

- To list available commands:

```bash
make
```

## Training a model

- Generate training data

```bash
make data
```

- Train a model on the generated data

```bash
make model
```

## Using the model

- Start the app (Grafana, MQTT broker, Alerts DB). The app will be accessible at `localhost:3000`.

```bash
make app
```
  
- Stream real time data to the app. Data points should appear in real-time on the dashboard.

```bash
make monitoring
```

- Run the trained anomaly detection model. You should see warning logs in your terminal, and alerts appearing in the Grafana dashboard. 

```bash
make detection
```

- Stop the app.

```bash
make stop
```
