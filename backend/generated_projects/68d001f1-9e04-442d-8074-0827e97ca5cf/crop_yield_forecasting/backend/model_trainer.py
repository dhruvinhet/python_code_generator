import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from xgboost import XGBRegressor
from sklearn.metrics import mean_squared_error, r2_score
from joblib import dump, load

# Placeholder for actual dataset loading. Replace with your data loading mechanism.
def load_dataset(filepath):
    try:
        df = pd.read_csv(filepath)
        return df
    except FileNotFoundError:
        raise FileNotFoundError("Dataset file not found.")
    except pd.errors.EmptyDataError:
        raise ValueError("Dataset file is empty.")
    except pd.errors.ParserError as e:
        raise ValueError(f"Error parsing the dataset file: {e}")


def train_model(filepath, target_variable, model_filepath="trained_model.joblib"):
    try:
        df = load_dataset(filepath)

        #Check if target variable exists
        if target_variable not in df.columns:
            raise ValueError(f"Target variable '{target_variable}' not found in the dataset.")

        # Identify numerical and categorical features automatically
        X = df.drop(target_variable, axis=1)
        y = df[target_variable]
        numerical_features = X.select_dtypes(include=np.number).columns.tolist()
        categorical_features = X.select_dtypes(include=['object', 'category']).columns.tolist()

        #Handle empty feature lists
        if not numerical_features and not categorical_features:
            raise ValueError("Dataset contains no features.")

        preprocessor = ColumnTransformer(
            transformers=[
                ('num', StandardScaler(), numerical_features),
                ('cat', OneHotEncoder(), categorical_features)
            ])

        pipeline = Pipeline([
            ('preprocessor', preprocessor),
            ('regressor', XGBRegressor())
        ])

        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

        # Add hyperparameter tuning with GridSearchCV for better performance.
        param_grid = {
            'regressor__n_estimators': [100, 500],
            'regressor__learning_rate': [0.01, 0.1],
            'regressor__max_depth': [3, 6]
        }

        grid_search = GridSearchCV(pipeline, param_grid, cv=5, scoring='neg_mean_squared_error', n_jobs=-1)
        grid_search.fit(X_train, y_train)

        best_model = grid_search.best_estimator_
        y_pred = best_model.predict(X_test)

        mse = mean_squared_error(y_test, y_pred)
        r2 = r2_score(y_test, y_pred)

        print(f"Mean Squared Error: {mse}")
        print(f"R-squared: {r2}")

        dump(best_model, model_filepath)
        print(f"Trained model saved to {model_filepath}")

    except Exception as e:
        print(f"An error occurred: {e}")
        raise