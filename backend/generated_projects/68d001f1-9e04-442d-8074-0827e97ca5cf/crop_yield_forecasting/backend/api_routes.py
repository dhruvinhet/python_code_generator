from fastapi import APIRouter, HTTPException
import pandas as pd
import json
from model import CropYieldModel
from data_loader import load_data

api_router = APIRouter(prefix="/api")

model = CropYieldModel()

@api_router.get('/data_preview')
async def data_preview():
    df = load_data()
    preview = df.head().to_json(orient='records')
    return json.loads(preview)

@api_router.get('/data_stats')
async def data_stats():
    df = load_data()
    stats = df.describe().to_json(orient='records')
    return json.loads(stats)

@api_router.post('/predict')
async def predict(input_data: dict):
    try:
        input_df = pd.DataFrame([input_data])
        prediction = model.predict(input_df)[0]
        return {"predicted_yield": prediction}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")

@api_router.get('/model_evaluation')
async def model_evaluation():
    try:
        return model.evaluate()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Model evaluation failed: {str(e)}")