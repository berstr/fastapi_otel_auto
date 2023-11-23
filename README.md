
## ENVIRONMENT

To send OTEL data via OTEL collector to New Relic, use:
- OTEL_EXPORTER_OTLP_ENDPOINT=\<hostname\>\<port\>

To send OTEL directly to New Relic:
- for EU region accounts:
  - OTEL_EXPORTER_OTLP_ENDPOINT=https://otlp.eu01.nr-data.net:4317
- for US region based accounts:
  - OTEL_EXPORTER_OTLP_ENDPOINT=https://otlp.nr-data.net:4317

OTEL_EXPORTER_OTLP_HEADERS=api-key=\<ingest license key\>  
OTEL_SERVICE_NAME=fastapi-otel-auto  
OTEL_PYTHON_LOGGING_AUTO_INSTRUMENTATION_ENABLED=true  
OTEL_PYTHON_LOG_LEVEL=info  


## CLI

opentelemetry-instrument --traces_exporter console,otlp --metrics_exporter console,otlp --logs_exporter console,otlp uvicorn main:app --host 0.0.0.0 --port 8000

---------------------

## Docker

**Note**: replace X.Y with the image version tags

docker build -t bstransky/fastapi_otel_auto:X.Y .

docker run -dit --rm --name fastapi_otel_auto \\  
-e OTEL_EXPORTER_OTLP_ENDPOINT \\  
-e OTEL_EXPORTER_OTLP_HEADERS \\  
-e OTEL_SERVICE_NAME \\  
-e OTEL_PYTHON_LOGGING_AUTO_INSTRUMENTATION_ENABLED \\  
-e OTEL_PYTHON_LOG_LEVEL \\  
-p8000:8000 bstransky/fastapi_otel_auto:X.Y

----------------------

## OTEL Collector

### ENV

NEW_RELIC_LICENSE_KEY=\<ingest license key\>  

- for EU region accounts:
  - OTEL_EXPORTER_OTLP_ENDPOINT=https://otlp.eu01.nr-data.net:4317
- for US region based accounts:
  - OTEL_EXPORTER_OTLP_ENDPOINT=https://otlp.nr-data.net:4317

-it --rm -p 4317:4317 -p 4318:4318

docker run --rm -it \\  
  -p 4317:4317  -p 4318:4318 \\  
  -v "${PWD}/otel-collector-config.yaml":/otel-collector-config.yaml \\  
  --name otelcol \\  
  -h otel-collector \\  
  --network="otel-collector-demo" \\  
  otel/opentelemetry-collector \\  
  --config otel-collector-config.yaml


docker run --rm \
  -e OTEL_EXPORTER_OTLP_ENDPOINT \
  -e NEW_RELIC_LICENSE_KEY \
  -p 4317:4317 \
  -v "${PWD}/otel-config.yaml":/otel-config.yaml \
  --name otelcol \
  otel/opentelemetry-collector \
  --config otel-config.yaml