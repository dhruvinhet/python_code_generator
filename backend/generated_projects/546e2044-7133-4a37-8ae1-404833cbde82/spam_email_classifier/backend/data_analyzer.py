import pandas as pd
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def analyze_data(df):
    """Performs basic data analysis.

    Args:
        df (pandas.DataFrame): The input DataFrame.

    Returns:
        dict: A dictionary containing data analysis results (shape, data types, missing values).
    """
    try:
        logging.info("Analyzing data...")
        analysis_results = {
            "shape": df.shape,
            "data_types": df.dtypes.to_dict(),
            "missing_values": df.isnull().sum().to_dict(),
            "unique_values": {}
        }
        for col in df.columns:
            analysis_results['unique_values'][col] = df[col].nunique()
        logging.info("Data analysis complete.")
        return analysis_results
    except Exception as e:
        logging.error(f"An error occurred during data analysis: {e}")
        return None