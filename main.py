
import os
import logging
import json
from fastapi import FastAPI, HTTPException
from starlette.exceptions import HTTPException as StarletteHTTPException
from fastapi.responses import PlainTextResponse

import requests
import random
from random import randint

from opentelemetry import trace, metrics

# Acquire a tracer
tracer = trace.get_tracer("diceroller.tracer")
# Acquire a meter.
meter = metrics.get_meter("diceroller.meter")

# Now create a counter instrument to make measurements with
roll_counter = meter.create_counter(
    "dice.rolls",
    description="The number of rolls by roll value",
)
items = {"foo": "The Foo Wrestlers"}

random.seed(54321)

app = FastAPI()

logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(str(os.getenv("OTEL_PYTHON_LOG_LEVEL", "INFO")).upper())

@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request, exc):
    current_span = trace.get_current_span()
    if (current_span is not None) and (current_span.is_recording()):
        current_span.set_attributes(
            {
                "http.status_text": str(exc.detail),
                "otel.status_description": f"{exc.status_code} / {str(exc.detail)}",
                "otel.status_code": "ERROR"
            }
        )
    return PlainTextResponse(json.dumps({ "detail" : str(exc.detail) }), status_code=exc.status_code)

@app.get("/items/{id}")
async def read_item(id: str):
    logger.info(f'GET /items received - id: {id}')
    if id not in items:
        raise HTTPException(status_code=404, detail=f'Item with id:[{id}] not found')
    return {"item": items[id]}

@app.get("/health")
def health():
    logger.info('GET /health received')
    logger.debug('GET /health received - test debug message')
    return {'service':'fastapi', 'result':'ok'}

@app.get("/external-api")
def external_api():
    logger.info('GET /external-api received')
    seconds = random.uniform(0, 3)
    logger.info(f'/external-api - calling httpbin.org with {seconds} sec delay')
    response = requests.get(f"https://httpbin.org/delay/{seconds}")
    response.close()
    return "ok"

@app.get("/rolldice")
def roll_dice(player: str):
    # This creates a new span that's the child of the current one
    with tracer.start_as_current_span("roll") as roll_span:
        logger.info('GET /rolldice received')
        result = str(roll())
        roll_span.set_attribute("roll.player", player)
        roll_span.set_attribute("roll.value", result)
        # This adds 1 to the counter for the given roll value
        roll_counter.add(1, {"roll.value": result})
        logger.info(f"player [{player}] is rolling the dice: {result}")
        return result

def roll():
    return randint(1, 6)