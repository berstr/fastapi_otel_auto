# Deployment Scenarios

This README contains the settings for various runtime configurations:

A) FastAPI app send OTEL data directly to ==> the New Relic OTEL endpoint  

B) FastAPI app sends OTEL data to a collector (in agent mode), which forwards it to the New Relic endpoint. This can be the New Relic Super Agent collector, or a community based collector. 
- B.1) FastAPI app runs as host process 
    - ==> Collector runs as docker container (community editon)
- B.2) FastAPI app runs as docker container
    - ==> Collector runs as docker container  (community editon)
- B.3) FastAPI app runs as docker container
    - ==> Collector runs as host process (New Relic Super Agent)
- B.4) FastAPI app runs as host process 
    - ==> Collector runs as host process  (New Relic Super Agent)

Notes:
- OTEL Collector agent mode: both FastAPI app and collector run on the same host.
- The New Relic Super Agent Collector runs as a host process, not as a container, and in agent mode - see [docs](https://docs-preview.newrelic.com/docs/new-relic-super-agent).
<br><br>

------------

# OTEL Collector

There are two options, the community ediiton collector or the New Relic Super Agent collector.

### 1 - New Relic Super Agent (Host Daemon Process)

Always run the super agent as host daemin process, not a container.

See the docs for further info on how to install and configure.  

- [New Relic Super Agent](https://docs-preview.newrelic.com/docs/new-relic-super-agent)
- [New Relic OTEL Collector (NRDOT)](https://docs-preview.newrelic.com/docs/new-relic-distribution-of-opentelemetry)



### 2 - Community Edition (Docker Container)

Always runs as a container.

a) - Set the environment:

- NEW_RELIC_LICENSE_KEY=\<[New Relic ingest license key](https://docs.newrelic.com/docs/apis/intro-apis/new-relic-api-keys/#license-key)\>  

- OTEL_EXPORTER_OTLP_ENDPOINT=https://otlp.eu01.nr-data.net:4317  
  - This send data to EU based accounts from New Relic. See [docs](https://docs.newrelic.com/docs/new-relic-solutions/get-started/networks/#new-relic-endpoints) for New Relic accounts based in the US region.


b) - Create a docker network, so other containers can talk to the collector:

    docker network create --driver=bridge -o "com.docker.network.bridge.enable_icc"="true" otel-collector

c) - Command to start collector as a container:

    docker run --rm -it \
      -e OTEL_EXPORTER_OTLP_ENDPOINT \
      -e NEW_RELIC_LICENSE_KEY \
      -p 4317:4317 -p 4318:4318 \
      -v "${PWD}/otel-collector-config.yaml":/otel-collector-config.yaml \
      --name otelcol \
      --network="otel-collector" \
      -h otel-collector \
      otel/opentelemetry-collector \
      --config otel-collector-config.yaml


<br><br>

--------------

# FastAPI App

### 1 - Download & Install

git clone  
create venv  
source venv  
pip install -r req...


### 1 - Common Environment

Here are the common settings across all deployment scenarios:

- OTEL_EXPORTER_OTLP_HEADERS=api-key=\<[New Relic ingest license key](https://docs.newrelic.com/docs/apis/intro-apis/new-relic-api-keys/#license-key)\>  
- OTEL_SERVICE_NAME=fastapi-otel-auto  
- OTEL_PYTHON_LOGGING_AUTO_INSTRUMENTATION_ENABLED=true  
- OTEL_PYTHON_LOG_LEVEL=INFO  

The value for OTEL_EXPORTER_OTLP_ENDPOINT is depending on the deployment scenario.

## 2 - Scenario A

FastAPI (host process) ==> New Relic OTEL endpoint

a) - Collector: no use of a collector

b) - Environment:

- OTEL_EXPORTER_OTLP_ENDPOINT=https://otlp.eu01.nr-data.net:4317  
  - For New Relic accounts based in the EU region. See the [docs](https://docs.newrelic.com/docs/new-relic-solutions/get-started/networks/#new-relic-endpoints) for further info.  

c) - Command

````
opentelemetry-instrument \
  --traces_exporter console,otlp \
  --metrics_exporter console,otlp \
  --logs_exporter console,otlp \
  uvicorn main:app --host 0.0.0.0 --port 8000
````

## 3 - Scenario B.1

FastAPI App (host process) ==> Collector (community editon, container)


a) - Collector: start it as a docker container

b) - Environment:

- OTEL_EXPORTER_OTLP_ENDPOINT=http://127.0.0.1:4317  

c) - Command

````
opentelemetry-instrument \
  --traces_exporter console,otlp \
  --metrics_exporter console,otlp \
  --logs_exporter console,otlp \
  uvicorn main:app --host 0.0.0.0 --port 8000
````

## 4 - Scenario B.2

FastAPI App (container) ==> Collector (community editon, container)

a) - Collector: start it as a docker container

b) - Environment:

- OTEL_EXPORTER_OTLP_ENDPOINT=http://otel-collector:4317  

c) - Command

````
docker run -dit --rm --name fastapi_otel_auto \\  
-e OTEL_EXPORTER_OTLP_ENDPOINT \\  
-e OTEL_EXPORTER_OTLP_HEADERS \\  
-e OTEL_SERVICE_NAME \\  
-e OTEL_PYTHON_LOGGING_AUTO_INSTRUMENTATION_ENABLED \\  
-e OTEL_PYTHON_LOG_LEVEL \\  
--network="otel-collector" \\  
-p8000:8000 bstransky/fastapi_otel_auto:latest
````

docker build -t bstransky/fastapi_otel_auto:X.Y .


## 5 - Scenario B.3

FastAPI App (container) ==> Collector (New Relic Super Agent, host daemon process)

a) - Collector: start it as a docker container

b) - Environment:

- OTEL_EXPORTER_OTLP_ENDPOINT=http://????:4317  





  # Further Links