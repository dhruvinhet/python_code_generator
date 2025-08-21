import pandas as pd
from joblib import load
import shap


def explain_prediction(model_filepath, input_data):
    try:
        model = load(model_filepath)
        
        # Handle empty feature list gracefully
        if not input_data:
            return {'error': 'Input data is empty. Please provide features.'}

        input_df = pd.DataFrame([input_data])

        #Check if all expected columns are present.  Replace [] with your actual feature names.
        expected_features = [] # Replace [] with your actual feature names
        missing_features = set(expected_features) - set(input_df.columns)
        if missing_features:
            return {'error': f'Missing features in input data: {missing_features}'}

        # Add preprocessing steps here if needed.  Example below assumes numerical features.  Adapt as needed.
        for col in expected_features:
            if input_df[col].dtype == object: #handle potential string data
                try:
                    input_df[col] = pd.to_numeric(input_df[col])
                except ValueError:
                    return {'error': f"Could not convert '{col}' to numeric."}


        explainer = shap.Explainer(model)
        #Handle potential errors during shap explanation.  Shap can be picky about input data types and model types
        try:
            shap_values = explainer(input_df)
            #added this line to return something useful
            return shap_values.values[0].tolist(), shap_values.feature_names
        except Exception as e:
            return {'error': f'Error during SHAP explanation: {e}'}

    except Exception as e:
        return {'error': f'Error loading model or during explanation: {e}'}