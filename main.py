
import os
import logging
#from fastapi import HTTPException, status
from fastapi import FastAPI
#from starlette.responses import FileResponse 
from opentelemetry.instrumentation.logging import LoggingInstrumentor

import requests
import random
#from opentelemetry.trace.status import Status, StatusCode



#from fastapi.staticfiles import StaticFiles

random.seed(54321)

app = FastAPI()

# logging.basicConfig(level=os.environ.get("LOGLEVEL", "INFO"))

# LoggingInstrumentor(log_level=logging.DEBUG)

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger('bernd')

@app.get("/health")
def health():
    logger.info('GET /health received')
    return {'service':'fastapi', 'result':'ok'}


@app.get("/external-api")
def external_api():
    logging.info('GET /external-api received')
    seconds = random.uniform(0, 3)
    logging.info(f'/external-api - calling httpbin.org with {seconds} sec delay')
    response = requests.get(f"https://httpbin.org/delay/{seconds}")
    response.close()
    return "ok"

