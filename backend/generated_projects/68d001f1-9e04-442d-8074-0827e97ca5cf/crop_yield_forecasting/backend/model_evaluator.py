import pandas as pd
import numpy as np
from sklearn.model_selection import cross_val_score, KFold
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.pipeline import Pipeline
from joblib import load

def evaluate_model(model_filepath, filepath):
    try:
        model = load(model_filepath)
        df = pd.read_csv(filepath)

        # Handle missing features gracefully.  This assumes 'predicted_yield' is always present.
        #  Adjust feature names as needed based on your actual dataset.
        if 'predicted_yield' not in df.columns:
            raise ValueError("Dataset missing 'predicted_yield' column.")
        
        #Identify features excluding 'predicted_yield' and handle potential errors.
        try:
            features = [col for col in df.columns if col != 'predicted_yield']
            X = df[features]
            y = df['predicted_yield']
        except KeyError as e:
            raise ValueError(f"Error accessing features in dataset: {e}") from None

        #Check for empty feature set
        if X.empty:
          raise ValueError("No features found in the dataset after removing 'predicted_yield'.")


        # Cross-validation
        kf = KFold(n_splits=5, shuffle=True, random_state=42)
        scores = cross_val_score(model, X, y, cv=kf, scoring='neg_mean_squared_error')
        rmse_scores = np.sqrt(-scores)
        mean_rmse = np.mean(rmse_scores)
        std_rmse = np.std(rmse_scores)

        # R-squared
        y_pred = model.predict(X)
        r2 = r2_score(y, y_pred)

        return mean_rmse, std_rmse, r2

    except FileNotFoundError:
        raise FileNotFoundError("Model file or dataset file not found.")
    except Exception as e:
        raise Exception(f"An error occurred: {e}") from None