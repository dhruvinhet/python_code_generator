from fastapi import APIRouter, HTTPException
from data_loader import get_data_stats, preview_data
from model import predict
from pydantic import BaseModel, ValidationError

api_router = APIRouter(prefix="/api")

class DataPoint(BaseModel):
    Open: float 
    High: float 
    Low: float 
    Volume: int 


@api_router.get("/stats")
def get_statistics():
    try:
        stats = get_data_stats()
        if stats is None:
            raise HTTPException(status_code=500, detail="Error getting statistics: Data not found")
        return stats.to_dict()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting statistics: {e}")

@api_router.get("/preview")
def get_data_preview():
    preview = preview_data()
    if preview is None:
        raise HTTPException(status_code=500, detail="Error getting preview: Data not found")
    return preview

@api_router.post("/predict")
def make_prediction(data_point: DataPoint):
    try:
        prediction = predict(list(data_point.model_dump().values())) # Use model_dump() for consistent dict
        return {"prediction": prediction}
    except ValidationError as e:
        raise HTTPException(status_code=422, detail=f"Validation Error: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error making prediction: {e}")