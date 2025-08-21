from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from api_routes import api_router
from data_loader import load_data, get_data_stats, preview_data

import uvicorn

app = FastAPI(title="Stock Price Predictor API")
app.include_router(api_router)

@app.get("/health")
def health_check():
    return {"status": "OK"}

@app.on_event("startup")
def load_dataset():
    try:
        load_data()
    except FileNotFoundError:
        raise HTTPException(status_code=500, detail="Dataset file not found.")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)