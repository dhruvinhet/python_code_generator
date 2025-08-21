import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression # Placeholder model
from sklearn.metrics import mean_squared_error, r2_score
from data_loader import load_data

class CropYieldModel:
    def __init__(self):
        self.model = LinearRegression() # Replace with a more suitable model
        try:
            self.df = load_data()
            # Handle cases where there are no features
            if self.df.shape[1] <=1:
                raise ValueError("Dataset must contain at least one feature column and the target 'predicted_yield'.")
            if 'predicted_yield' not in self.df.columns:
                raise ValueError("Dataset must contain a 'predicted_yield' column.")

            self.X = self.df.drop('predicted_yield', axis=1)
            self.y = self.df['predicted_yield']
            self.X_train, self.X_test, self.y_train, self.y_test = train_test_split(self.X, self.y, test_size=0.2, random_state=42)
            self.train()
        except FileNotFoundError:
            print("Error: Data file not found. Please check the data_loader.")
            raise  # Re-raise the exception to stop execution
        except ValueError as e:
            print(f"Error: {e}")
            raise # Re-raise the exception to stop execution
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            raise # Re-raise to allow higher level handling

    def train(self):
        self.model.fit(self.X_train, self.y_train)

    def predict(self, X):
        return self.model.predict(X)

    def evaluate(self):
        y_pred = self.model.predict(self.X_test)
        mse = mean_squared_error(self.y_test, y_pred)
        r2 = r2_score(self.y_test, y_pred)
        return {'mse': mse, 'r2': r2}