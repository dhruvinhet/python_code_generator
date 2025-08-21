from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd

from data_loader import load_data
from api_routes import api_router
from config import DATA_PATH

app = FastAPI(title="Crop Yield Forecasting API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],  # Consider restricting origins in production
    allow_credentials=True,
    allow_methods=['*'],   # Consider restricting methods in production
    allow_headers=['*'],   # Consider restricting headers in production
)

@app.on_event("startup")
async def startup_event():
    try:
        load_data(DATA_PATH) # Pass DATA_PATH to load_data
    except FileNotFoundError:
        raise HTTPException(status_code=500, detail="Dataset file not found.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error loading data: {e}")

app.include_router(api_router)