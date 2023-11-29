# Python FastAPI with OTEL

This Python FastAPI based app sends OTEL data (metrics, traces, logs) either directly of via a collector to New Relic.
The app uses OTEL auto instrumentation for Python, as well as manual instrumentation (traces, metrics)

The following OTEL collectors will be used:

1) The new *New Relic Super Agent*, which includes a New Relic maintained collector distribution (NRDOT). This is part of the New Relic Next Gen architecture, all based on OTEL and OpAMP.

2) OTEL Community based collector distribution.


<br><br>

------------

# Deployment Scenarios

This README contains the settings for various deployment scenarios:

- A) - FastAPI app runs as docker container  
    - ==> directly to the New Relic OTEL endpoint  (no collector)


- B) - FastAPI app runs as host process 
    - ==> Collector runs as host process  (New Relic Super Agent)
- C) - FastAPI app runs as docker container
    - ==> Collector runs as host process (New Relic Super Agent)
- D) - FastAPI app runs as host process 
    - ==> Collector runs as docker container (community editon)
- E) - FastAPI app runs as docker container
    - ==> Collector runs as docker container  (community editon)

Notes:
- The OTEL community collector runs in agent mode, i.e. both FastAPI app and collector run on the same host.
- The New Relic Super Agent Collector runs as a host process, not as a container, and in agent mode - see [docs](https://docs-preview.newrelic.com/docs/new-relic-super-agent).


<br><br>

------------

# OTEL Collector

There are two options, the community ediiton collector or the New Relic Super Agent collector.

### 1 - New Relic Super Agent (Host Daemon Process)

### 1.1 - Pre Installation

Always run the super agent as host daemon process, not a container.

### 1.2 - Installation

See the docs for further info on how to install and configure.  

- [New Relic Super Agent](https://docs-preview.newrelic.com/docs/new-relic-super-agent) Installation
- Further information regarding the included collector can be found here: [New Relic OTEL Collector (NRDOT)](https://docs-preview.newrelic.com/docs/new-relic-distribution-of-opentelemetry)

Note: The API key for the installation command is a User API Key. You can find it in the New Relic UI in the [API Keys](https://one.newrelic.com/launcher/api-keys-ui.api-keys-launcher) section and more info in the
[docs](https://docs.newrelic.com/docs/apis/intro-apis/new-relic-api-keys/#user-key)

### 1.3 - Post Installation

After the installation, check and verify that the file:
- /etc/nr-otel-collector/config.yaml  

does not contain ${...} env entries in the exporters:otel section, but the actual values instead.  
Note that settings via env variables are not being recognized.

Example:

``````
exporters:
  logging:
  otlp:
    endpoint: https://otlp.eu01.nr-data.net:4317
    headers:
      api-key: <New Relic INGEST LICENSE Key>
``````

- This endpoint setting sends data to EU based accounts from New Relic.  
See [docs](https://docs.newrelic.com/docs/new-relic-solutions/get-started/networks/#new-relic-endpoints) for New Relic accounts based in the US region.

- See [New Relic INGEST LICENSE Key](https://docs.newrelic.com/docs/apis/intro-apis/new-relic-api-keys/#license-key) regarding this key.


<br>


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

``````
git clone  https://github.com/berstr/fastapi_otel_auto.git
cd fastapi_otel_auto
python3 venv -m venv
source venv/bin/activate
pip install -r requirements
``````

### 2 - Common Environment

Here are the common settings across all deployment scenarios:
 
- OTEL_SERVICE_NAME=fastapi-otel-auto  
- OTEL_PYTHON_LOGGING_AUTO_INSTRUMENTATION_ENABLED=true  
- OTEL_PYTHON_LOG_LEVEL=INFO  

See further settings in each deployment scenarios.

<br><br>

--------------

# Deployment Scenarios

## Scenario A

FastAPI (host process) ==> New Relic OTEL endpoint

a) - Collector: No use of a collector

b) - FastAPI App: Environment

- See section *FastAPI App -> 2 - Common Environment* for common settings.
- OTEL_EXPORTER_OTLP_HEADERS=api-key=\<[New Relic ingest license key](https://docs.newrelic.com/docs/apis/intro-apis/new-relic-api-keys/#license-key)\> 
- OTEL_EXPORTER_OTLP_ENDPOINT=https://otlp.eu01.nr-data.net:4317  
  - For New Relic accounts based in the EU region. See the [docs](https://docs.newrelic.com/docs/new-relic-solutions/get-started/networks/#new-relic-endpoints) for further info.  

c) - Start fastAPI app:

````
opentelemetry-instrument \
  --traces_exporter console,otlp \
  --metrics_exporter console,otlp \
  --logs_exporter console,otlp \
  uvicorn main:app --host 0.0.0.0 --port 8000
````

## Scenario B

FastAPI App (host process) ==> New Relic Super Agent (collector, host daemon process)

a)  Install and run the New Relic Super Agent, see section *OTEL Collector -> New Relic Super Agent (Host Daemon Process)*

b) - FastAPI App: Environment

- See section *FastAPI App -> 2 - Common Environment* for common settings.

c) - Start fastAPI app:

````
opentelemetry-instrument \
  --traces_exporter console,otlp \
  --metrics_exporter console,otlp \
  --logs_exporter console,otlp \
  uvicorn main:app --host 0.0.0.0 --port 8000
````


## Scenario C

FastAPI App (container) ==> New Relic Super Agent (collector, host daemon process)

a)  Install and run the New Relic Super Agent, see section *OTEL Collector -> New Relic Super Agent (Host Daemon Process)*

b) - FastAPI App: Environment

- See section *FastAPI App -> 2 - Common Environment* for common settings.

c) - Start fastAPI app as container:

``````
docker run -dit --rm --name fastapi_otel_auto \
-e OTEL_SERVICE_NAME \
-e OTEL_PYTHON_LOGGING_AUTO_INSTRUMENTATION_ENABLED \
-e OTEL_PYTHON_LOG_LEVEL \
--network host \
-p8000:8000 bstransky/fastapi_otel_auto:latest
``````


## Scenario D

FastAPI App (host process) ==> Collector (community editon, container)

a) - Collector: start it as a docker container, see section *Community Edition (Docker Container)* above.

b) - FastAPI App: Environment

- See section *FastAPI App -> 2 - Common Environment* for common settings.


c) - Command

````
opentelemetry-instrument \
  --traces_exporter console,otlp \
  --metrics_exporter console,otlp \
  --logs_exporter console,otlp \
  uvicorn main:app --host 0.0.0.0 --port 8000
````

## Scenario E

FastAPI App (container) ==> Collector (community editon, container)

a) - Collector: start it as a docker container, see section *Community Edition (Docker Container)* above.

b) - FastAPI App: Environment

- See section *FastAPI App -> 2 - Common Environment* for common settings.
- OTEL_EXPORTER_OTLP_ENDPOINT=http://otel-collector:4317

c) - FastAPI App: Startup

````
docker run -it --rm --name fastapi_otel_auto \
-e OTEL_EXPORTER_OTLP_ENDPOINT \
-e OTEL_SERVICE_NAME \
-e OTEL_PYTHON_LOGGING_AUTO_INSTRUMENTATION_ENABLED \
-e OTEL_PYTHON_LOG_LEVEL \
--network="otel-collector" \
-p8000:8000 bstransky/fastapi_otel_auto:latest
````

<br><br>

--------------


# MISC

## Further Super Agent Observability

## New Relic Preview Docs

- [Set up the New Relic super agent](https://docs-preview.newrelic.com/docs/new-relic-super-agent)

- [New Relic OpenTelemetry collector](https://docs-preview.newrelic.com/docs/new-relic-distribution-of-opentelemetry)

- [New Relic Fleet Manager](https://docs-preview.newrelic.com/docs/new-relic-fleet-manager)

## FastAPI Requests

Here are sample requests for the FastAPI service:

``````
curl http://localhost:8000/health

curl http://localhost:8000/external-api

curl http://localhost:8000/rolldice\?player=millivanilla
``````
