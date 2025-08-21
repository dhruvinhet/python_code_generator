import pandas as pd
import matplotlib.pyplot as plt

def validate_data(df):
    """Validates the data to ensure data quality."""
    if df is None:
        return None

    report = {}
    
    # Check for missing values
    missing_values = df.isnull().sum()
    if missing_values.any():
        report['missing_values'] = missing_values

    # Check for duplicate rows
    duplicate_rows = df[df.duplicated()]
    if not duplicate_rows.empty:
        report['duplicate_rows'] = duplicate_rows

    #Check for data type inconsistencies (example -  assuming a column 'age' should be numeric)
    if 'age' in df.columns:
        if not pd.api.types.is_numeric_dtype(df['age']):
            report['data_type_inconsistencies'] = "Column 'age' is not numeric."

    # Check for outliers (example - using IQR for 'age' column)

    if 'age' in df.columns and pd.api.types.is_numeric_dtype(df['age']):
        Q1 = df['age'].quantile(0.25)
        Q3 = df['age'].quantile(0.75)
        IQR = Q3 - Q1
        lower_bound = Q1 - 1.5 * IQR
        upper_bound = Q3 + 1.5 * IQR
        outliers = df[(df['age'] < lower_bound) | (df['age'] > upper_bound)]
        if not outliers.empty:
            report['outliers'] = {"column": 'age', "outliers": outliers}


    return report