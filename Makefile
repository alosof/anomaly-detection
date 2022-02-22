SHELL := /bin/bash
.SHELLFLAGS = -ec
.ONESHELL:
.SILENT:


.PHONY: help
help:
	echo "❓ Use \`make <target>'"
	grep -E '^\.PHONY: [a-zA-Z0-9_-]+ .*?## .*$$' $(MAKEFILE_LIST) | \
		awk 'BEGIN {FS = "(: |##)"}; {printf "\033[36m%-30s\033[0m %s\n", $$2, $$3}'

.PHONY: data ## 🔢 Generate training data
data:
	python metrics_generator/generate_metrics.py -d file

.PHONY: model ## 🏋 Train model with previously generated data
model:
	python anomaly_detector/train_model.py

.PHONY: app ## 📲 Start the app
app:
	docker-compose up -d

.PHONY: monitoring ## 📈 Trigger real-time system metrics measurement
monitoring:
	python metrics_generator/generate_metrics.py -d broker

.PHONY: detection ## 🕵 Run anomaly detection model
detection:
	python anomaly_detector/analyze_metrics.py

.PHONY: stop ## 🛑 Stop the app
stop:
	docker-compose down
