import pandas as pd
import numpy as np
from joblib import load

def predict_yield(model_filepath, input_data):
    try:
        model = load(model_filepath)
        input_df = pd.DataFrame([input_data])

        # Preprocessing steps should be added here based on the model's training process.
        #  The following is a placeholder. Replace with your actual preprocessing steps.
        #  This example assumes you scaled 'feature1' and one-hot encoded 'crop_type' during training.

        # Example preprocessing (adapt to your specific features and preprocessing steps):
        try:
            scaler = load('scaler.joblib')
            if 'feature1' in input_df.columns:
                input_df['feature1'] = scaler.transform(input_df[['feature1']])
        except FileNotFoundError:
            print("Warning: scaler.joblib not found. Skipping scaling of 'feature1'.")

        try:
            onehot = load('onehot.joblib')
            if 'crop_type' in input_df.columns:
                encoded_data = onehot.transform(input_df[['crop_type']])
                encoded_df = pd.DataFrame(encoded_data.toarray(), columns=onehot.get_feature_names_out(['crop_type']))
                input_df = pd.concat([input_df, encoded_df], axis=1).drop(columns=['crop_type'])
        except FileNotFoundError:
            print("Warning: onehot.joblib not found. Skipping one-hot encoding of 'crop_type'.")


        prediction = model.predict(input_df)
        return prediction[0] # Return a single value instead of an array

    except FileNotFoundError:
        return "Error: Model file not found."
    except Exception as e:
        return f"An error occurred: {e}"