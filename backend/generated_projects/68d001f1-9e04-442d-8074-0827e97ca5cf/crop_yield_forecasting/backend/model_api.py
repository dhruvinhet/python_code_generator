from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from model_trainer import train_model
from model_predictor import predict_yield
from model_evaluator import evaluate_model
from model_explainer import explain_prediction
from joblib import load, dump
import pandas as pd
import os

app = FastAPI()

# Placeholder InputData model. Replace with your actual features and types.
class InputData(BaseModel):
    feature1: str = Field(...)
    feature2: float = Field(...)


@app.post("/predict")
def predict(input_data: InputData):
    try:
        input_dict = input_data.model_dump()
        prediction = predict_yield("trained_model.joblib", input_dict)
        return {"predicted_yield": prediction}
    except FileNotFoundError:
        raise HTTPException(status_code=500, detail="Trained model not found.  Run /train first.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")


@app.post("/train")
def train(filepath: str):
    try:
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"Dataset file not found at {filepath}")
        model, params = train_model(filepath)
        dump(model, "trained_model.joblib") #Save the trained model
        return {"message": "Model trained successfully", "params": params}
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except pd.errors.EmptyDataError:
        raise HTTPException(status_code=400, detail="Dataset is empty.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Training failed: {str(e)}")


@app.get("/evaluate")
def evaluate():
    try:
        model = load("trained_model.joblib")
        metrics = evaluate_model(model) # Assuming evaluate_model returns a dictionary of metrics.
        return {"evaluation_metrics": metrics}
    except FileNotFoundError:
        raise HTTPException(status_code=500, detail="Trained model not found.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Evaluation failed: {str(e)}")

@app.post("/explain")
def explain(input_data: InputData):
    try:
        input_dict = input_data.model_dump()
        explanation = explain_prediction("trained_model.joblib", input_dict)
        return {"explanation": explanation}
    except FileNotFoundError:
        raise HTTPException(status_code=500, detail="Trained model not found.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Explanation failed: {str(e)}")