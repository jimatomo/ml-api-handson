from typing import Union
from fastapi import FastAPI

import schemas
from ml_model import ML_API

import json
from pydantic.json import pydantic_encoder

app = FastAPI()
ml_api = ML_API()

@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.post('/prediction/online', response_model=schemas.Pred)
def online_prediction(data: schemas.Data):
    input_json = json.dumps(data.data, default=pydantic_encoder)
    prediction = ml_api.predict(input_json)

    return prediction