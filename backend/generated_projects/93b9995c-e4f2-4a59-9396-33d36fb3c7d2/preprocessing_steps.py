# preprocessing_steps.py
from collections import OrderedDict


def get_preprocessing_options():
    """Returns a dictionary of available preprocessing steps."""
    options = OrderedDict({
        "Handle Missing Values": {},
        "Encode Categorical Features": {},
        "Scale Numerical Features": {}
    })
    return options


def get_parameters_for_step(step):
    """Returns a dictionary of parameters for a given preprocessing step."""
    if step == "Handle Missing Values":
        return {
            "column": {"type": "text", "default": "", "help": "Column to handle missing values in"},
            "strategy": {"type": "selectbox", "options": ["mean", "median", "remove", "constant"], "help": "Strategy for handling missing values"},
            "fill_value": {"type": "number", "default": 0, "help": "Value to fill missing values with (for constant strategy)"}
        }
    elif step == "Encode Categorical Features":
        return {
            "columns": {"type": "multiselect", "help": "Columns to encode"},
            "encoding_type": {"type": "selectbox", "options": ["one-hot", "label"], "help": "Encoding type"}
        }
    elif step == "Scale Numerical Features":
        return {
            "columns": {"type": "multiselect", "help": "Columns to scale"},
            "scaler_type": {"type": "selectbox", "options": ["StandardScaler", "MinMaxScaler"], "help": "Scaler type"}
        }
    else:
        return {}
