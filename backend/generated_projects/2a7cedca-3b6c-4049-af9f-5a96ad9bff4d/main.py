# main.py
import streamlit as st
import pandas as pd
import calendar_scraper
import data_processing
import config


# Streamlit application entry point
def main():
    st.title("Sports Championship Calendar Aggregator")
    st.write("Aggregating sports championship calendars from various sources...")

    all_calendar_data = []
    # Scrape data from each website defined in config.py
    for website in config.WEBSITE_CONFIGURATIONS:
        url = website.get('url')
        website_name = website.get('name')
        if not url or not website_name:
            st.error(f"Invalid website configuration: {website}")
            continue
        try:
            st.write(f"Scraping data from {website_name} ({url})...")
            html_content = calendar_scraper.scrape_website_calendar(url)
            if html_content:
                events = calendar_scraper.extract_events(html_content, website_name)
                if events:
                    all_calendar_data.append(events)
                else:
                    st.warning(f"No events extracted from {website_name}.")
            else:
                st.error(f"Failed to scrape data from {website_name}.")
        except Exception as e:
            st.error(f"An error occurred while scraping {website_name}: {e}")

    # Process and merge the scraped data
    if all_calendar_data:
        try:
            st.write("Processing and merging calendar data...")
            normalized_data = [data_processing.normalize_data(data) for data in all_calendar_data]
            merged_calendar = data_processing.merge_calendars(normalized_data)

            if merged_calendar is not None and not merged_calendar.empty:
                st.write("Displaying aggregated calendar:")
                st.dataframe(merged_calendar)
            else:
                st.warning("No data to display after processing.")
        except Exception as e:
            st.error(f"An error occurred during data processing: {e}")
    else:
        st.info("No data scraped from any websites.")


# Run the Streamlit application
if __name__ == "__main__":
    main()