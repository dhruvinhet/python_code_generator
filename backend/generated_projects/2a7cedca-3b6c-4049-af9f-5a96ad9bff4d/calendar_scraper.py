# calendar_scraper.py
import requests
from bs4 import BeautifulSoup
import pandas as pd
import logging

logging.basicConfig(level=logging.ERROR)

# Function to scrape calendar data from a given URL
def scrape_website_calendar(url):
    """Scrapes HTML content from a given URL.

    Args:
        url (str): The URL to scrape.

    Returns:
        str: The HTML content of the page, or None if an error occurs.
    """
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)
        return response.content
    except requests.exceptions.RequestException as e:
        logging.error(f"Error scraping {url}: {e}")
        return None


# Function to extract event details from the scraped HTML content
def extract_events(html_content, website_name):
    """Extracts event details (date, time, event name) from scraped HTML content.

    Args:
        html_content (str): The HTML content to parse.
        website_name (str): The name of the website being scraped (for identification).

    Returns:
        list: A list of dictionaries, where each dictionary represents an event.
              Returns an empty list if no events are found or if an error occurs.
    """
    try:
        soup = BeautifulSoup(html_content, 'html.parser')

        # This is a placeholder and needs to be adapted based on the website's HTML structure.
        # Example: Find all tables and extract data from them.
        tables = soup.find_all('table')

        events = []
        for table in tables:
            for row in table.find_all('tr'):
                cells = row.find_all('td')
                if len(cells) >= 3:  # Assuming at least 3 columns: date, time, event
                    try:
                        date = cells[0].text.strip()
                        time = cells[1].text.strip()
                        event_name = cells[2].text.strip()

                        events.append({
                            'website': website_name,
                            'date': date,
                            'time': time,
                            'event': event_name
                        })
                    except IndexError as ie:
                        logging.warning(f"IndexError extracting data from row: {ie}")
                    except Exception as ex:
                        logging.error(f"Error processing cells: {ex}")

        return events

    except Exception as e:
        logging.error(f"Error extracting events from {website_name}: {e}")
        return []