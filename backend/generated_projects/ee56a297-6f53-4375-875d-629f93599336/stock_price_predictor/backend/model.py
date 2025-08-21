import pandas as pd
from sklearn.linear_model import LinearRegression
from data_loader import load_data

model = None

def train_model():
    global model
    df = load_data()
    # Feature Engineering would go here (needs actual features from dataset)
    # Assuming 'Close Price' as target and other cols as features (replace with actual features)
    try:
        X = df.drop('Close Price', axis=1)
        y = df['Close Price']
        model = LinearRegression()
        model.fit(X, y)
    except KeyError as e:
        print(f"Error: Could not find column in dataframe: {e}")
        return None


def predict(data_point):
    if model is None:
        if train_model() is None: #Check if training failed.
            return None
    try:
        return model.predict([data_point])[0]
    except ValueError as e:
        print(f"Error during prediction: {e}")
        return None