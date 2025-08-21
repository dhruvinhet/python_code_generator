import pandas as pd
import numpy as np

def clean_data(df):
    """Cleans the dataset by handling missing values and outliers."""
    if df is None:
        return None

    # Handle missing values (replace with mean for numerical columns, mode for categorical)
    for col in df.columns:
        if df[col].isnull().any():
            if pd.api.types.is_numeric_dtype(df[col]):
                df[col].fillna(df[col].mean(), inplace=True)
            elif pd.api.types.is_categorical_dtype(df[col]):
                df[col].fillna(df[col].mode()[0], inplace=True)
            else:
                print(f"Warning: Column '{col}' has missing values and is not numeric or categorical.  Skipping.")


    # Handle Outliers (using IQR -  needs to be applied column by column)

    for col in df.columns:
        if pd.api.types.is_numeric_dtype(df[col]):
            Q1 = df[col].quantile(0.25)
            Q3 = df[col].quantile(0.75)
            IQR = Q3 - Q1
            Lower_bound = Q1 - 1.5 * IQR
            Upper_bound = Q3 + 1.5 * IQR
            df = df[(df[col] >= Lower_bound) & (df[col] <= Upper_bound)]


    return df