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
	python -m metrics_generator.generate_metrics -d file

.PHONY: model ## 🏋 Train model with previously generated data
model:
	python -m anomaly_detector.train_model

.PHONY: app ## 📲 Start the app
app:
	docker-compose up -d

.PHONY: monitoring ## 📈 Trigger real-time system metrics measurement
monitoring:
	python -m metrics_generator.generate_metrics -d broker

.PHONY: detection ## 🕵 Run anomaly detection model
detection:
	python -m anomaly_detector.analyze_metrics

.PHONY: stop ## 🛑 Stop the app
stop:
	docker-compose down
