import pandas as pd
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def clean_data(df, report_filepath = 'cleaning_report.txt'):
    """Cleans the DataFrame.

    Args:
        df (pandas.DataFrame): The DataFrame to clean.
        report_filepath (str, optional): Path for the cleaning report. Defaults to 'cleaning_report.txt'.

    Returns:
        pandas.DataFrame: The cleaned DataFrame.
    """
    try:
        logging.info("Cleaning data...")
        original_shape = df.shape
        #Example cleaning steps.  Expand as needed for your specific data.
        df.dropna(subset=['email_body'], inplace=True) #Remove rows with missing email bodies
        #Add more cleaning steps here (e.g., handling duplicates, removing special characters, etc.)
        df.drop_duplicates(inplace=True) #remove duplicates
        cleaned_shape = df.shape
        
        with open(report_filepath, 'w') as f:
            f.write(f"Original shape: {original_shape}\n")
            f.write(f"Shape after cleaning: {cleaned_shape}\n")
            #Add detailed report of cleaning steps and actions here.
            f.write(f"Rows with missing email bodies dropped: {original_shape[0] - cleaned_shape[0]}\n")
            f.write(f"Duplicate rows dropped: {original_shape[0] - cleaned_shape[0]}\n")
        logging.info(f"Data cleaning complete. Report saved to: {report_filepath}")
        return df
    except Exception as e:
        logging.error(f"An error occurred during data cleaning: {e}")
        return None