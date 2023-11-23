
import os
import logging
from fastapi import FastAPI

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


random.seed(54321)

app = FastAPI()

logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(str(os.getenv("OTEL_PYTHON_LOG_LEVEL", "INFO")).upper())

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