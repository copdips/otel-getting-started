install:
	pip install -U pip
	pip install -r requirements.txt

run-otel-manual-instrument-with-console:
	OTEL_PYTHON_LOGGING_AUTO_INSTRUMENTATION_ENABLED=true opentelemetry-instrument \
		--traces_exporter console \
		--metrics_exporter console \
		--logs_exporter console \
		--service_name dice-server \
		python manual_instrument.py

run-otel-flask-with-console:
	OTEL_PYTHON_LOGGING_AUTO_INSTRUMENTATION_ENABLED=true opentelemetry-instrument \
		--traces_exporter console \
		--metrics_exporter console \
		--logs_exporter console \
		--service_name dice-server \
		flask run -p 8080

run-otel-collector:
	docker run -p 4317:4317 \
		-v ./otel-collector-config.yaml:/etc/otel-collector-config.yaml \
		otel/opentelemetry-collector:latest \
		--config=/etc/otel-collector-config.yaml

run-otel-flask-with-exporter:
	OTEL_PYTHON_LOGGING_AUTO_INSTRUMENTATION_ENABLED=true opentelemetry-instrument \
		--logs_exporter otlp flask run -p 8080
