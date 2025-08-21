import streamlit as st
import requests

# --- Replace with your API key and Custom Search Engine ID ---
API_KEY = "AIzaSyCa_9wI1sT3-d2BejbxwmvEI31bq5oP59A"
CX = "3519a0ac46907492a"

# Streamlit UI
st.set_page_config(page_title="Google Custom Search", page_icon="🔍", layout="wide")
st.title("🔍 Google Custom Search with Streamlit")

query = st.text_input("Enter your search query:", "")

if st.button("Search"):
    if query.strip():
        # API endpoint
        url = f"https://www.googleapis.com/customsearch/v1"
        params = {
            "key": API_KEY,
            "cx": CX,
            "q": query
        }

        # Call API
        response = requests.get(url, params=params)

        if response.status_code == 200:
            results = response.json().get("items", [])
            if results:
                st.subheader(f"Search Results for: **{query}**")
                for idx, item in enumerate(results, start=1):
                    title = item.get("title")
                    link = item.get("link")
                    snippet = item.get("snippet")

                    with st.container():
                        st.markdown(f"### {idx}. [{title}]({link})")
                        st.write(snippet)
                        st.write("---")
            else:
                st.warning("No results found.")
        else:
            st.error(f"Error {response.status_code}: {response.text}")
    else:
        st.warning("Please enter a query.")
