# data_processing.py
import pandas as pd
import logging

logging.basicConfig(level=logging.ERROR)

# Function to normalize the scraped data
def normalize_data(data: list) -> list:
    """Normalizes the scraped data by cleaning and standardizing the format.

    Args:
        data (list): A list of dictionaries, where each dictionary represents an event.

    Returns:
        list: A list of dictionaries with normalized data.
    """
    normalized_data = []
    for event in data:
        try:
            # Clean and standardize data fields
            date_str = event['date'].strip() if isinstance(event.get('date'), str) else ''
            time_str = event['time'].strip() if isinstance(event.get('time'), str) else ''
            event_name_str = event['event'].strip() if isinstance(event.get('event'), str) else ''
            website_str = event['website'].strip() if isinstance(event.get('website'), str) else ''

            try:
                date = pd.to_datetime(date_str, errors='coerce')
                date_formatted = date.strftime('%Y-%m-%d') if not pd.isna(date) else None
            except ValueError:
                date_formatted = None
                logging.warning(f"Invalid date format found: {date_str}")

            normalized_event = {
                'website': website_str,
                'date': date_formatted,
                'time': time_str,
                'event': event_name_str
            }

            if normalized_event['date'] is None:
                logging.warning(f"Invalid date found, skipping: {event.get('date')}")
            else:
                normalized_data.append(normalized_event)

        except KeyError as ke:
            logging.error(f"Missing key in event data: {ke} - Event data: {event}")
        except Exception as e:
            logging.error(f"Error normalizing data: {e} - Event data: {event}")

    return normalized_data


# Function to merge calendar data from multiple sources into a single DataFrame
def merge_calendars(calendar_data: list) -> pd.DataFrame:
    """Merges calendar data from multiple sources into a single pandas DataFrame.

    Args:
        calendar_data (list): A list of lists, where each inner list represents calendar data from one source.

    Returns:
        pd.DataFrame: A DataFrame containing the merged and sorted calendar data.
    """
    try:
        # Flatten the list of lists into a single list of dictionaries
        all_events = []
        for data in calendar_data:
            if isinstance(data, list):
                all_events.extend(data)
            else:
                logging.warning(f"Unexpected data type in calendar_data: {type(data)}")

        if not all_events:
            return pd.DataFrame()  # Return an empty DataFrame if no data is available

        # Create a pandas DataFrame from the combined data
        df = pd.DataFrame(all_events)

        # Sort the DataFrame by date and time
        df['date'] = pd.to_datetime(df['date'], errors='coerce')
        df = df.sort_values(by=['date', 'time'])
        df['date'] = df['date'].dt.strftime('%Y-%m-%d')  # Format date back to string for display

        # Reset the index
        df = df.reset_index(drop=True)

        return df

    except Exception as e:
        logging.error(f"Error merging calendars: {e}")
        return pd.DataFrame()