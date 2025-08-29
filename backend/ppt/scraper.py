import os
import requests
from dotenv import load_dotenv
from bs4 import BeautifulSoup
import time
import sys

load_dotenv()

def google_search(query, num=4):
    """
    Perform a Google Custom Search query using API key and CSE ID from env vars.
    
    :param query: Search query string
    :param num: Number of results (max 10 per request)
    :return: List of results (title, link, snippet)
    """
    api_key = os.getenv("CUSTOM_SEARCH_API")
    cse_id = os.getenv("CSE_ID")

    if not api_key or not cse_id:
        raise ValueError("ENV ERROR")

    url = "https://www.googleapis.com/customsearch/v1"
    params = {
        "q": query,
        "key": api_key,
        "cx": cse_id,
        "num": num,
    }
    response = requests.get(url, params=params)
    results = []
    if response.status_code == 200:
        data = response.json()
        for item in data.get("items", []):
            results.append({
                "title": item["title"],
                "link": item["link"],
                "snippet": item["snippet"],
            })
    else:
        print("Error:", response.status_code, response.text)
    return results

def scrape_webpage(url, timeout=10):
    """
    Scrape content from a webpage.
    
    :param url: URL to scrape
    :param timeout: Request timeout in seconds
    :return: Dictionary with scraped content
    """
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    try:
        print(f"🔍 Scraping: {url}")
        response = requests.get(url, headers=headers, timeout=timeout)
        response.raise_for_status()
        
        # Parse HTML content
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.decompose()
        
        # Extract basic information
        title = soup.find('title')
        title_text = title.get_text().strip() if title else "No title found"
        
        # Extract main content (try common content selectors)
        content_selectors = [
            'main', 'article', '.content', '#content', 
            '.post-content', '.entry-content', 'div.content'
        ]
        
        content_text = ""
        for selector in content_selectors:
            content_elem = soup.select_one(selector)
            if content_elem:
                content_text = content_elem.get_text(strip=True, separator=' ')
                break
        
        # If no specific content area found, get body text
        if not content_text:
            body = soup.find('body')
            if body:
                content_text = body.get_text(strip=True, separator=' ')
        
        # Limit content length for display
        if len(content_text) > 1000:
            content_text = content_text[:1000] + "..."
        
        # Extract meta description
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        meta_description = meta_desc.get('content', '') if meta_desc else ""
        
        return {
            'url': url,
            'title': title_text,
            'meta_description': meta_description,
            'content': content_text,
            'status': 'success'
        }
        
    except requests.exceptions.Timeout:
        return {'url': url, 'status': 'timeout', 'error': 'Request timed out'}
    except requests.exceptions.ConnectionError:
        return {'url': url, 'status': 'connection_error', 'error': 'Connection failed'}
    except requests.exceptions.HTTPError as e:
        return {'url': url, 'status': 'http_error', 'error': f'HTTP {e.response.status_code}'}
    except Exception as e:
        return {'url': url, 'status': 'error', 'error': str(e)}

def display_scraped_content(scraped_data):
    """
    Display scraped content in a formatted way.
    
    :param scraped_data: Dictionary with scraped content
    """
    print("=" * 80)
    
    if scraped_data['status'] == 'success':
        print(f" TITLE: {scraped_data['title']}")
        print(f" URL: {scraped_data['url']}")
        
        if scraped_data['meta_description']:
            print(f" META DESCRIPTION: {scraped_data['meta_description']}")
        
        print("\n CONTENT:")
        print("-" * 60)
        print(scraped_data['content'])
        
    else:
        print(f" FAILED TO SCRAPE: {scraped_data['url']}")
        print(f" STATUS: {scraped_data['status']}")
        print(f"️  ERROR: {scraped_data.get('error', 'Unknown error')}")
    
    print("=" * 80)
    print()

def main():
    """
    Main function to search and scrape results.
    """
    # Get search query from user
    if len(sys.argv) > 1:
        query = ' '.join(sys.argv[1:])
    else:
        query = input("Enter search query: ").strip()
        if not query:
            query = "python ppt generation"  # default query
    
    print(f"🔍 Searching for: '{query}'")
    print("=" * 80)
    
    try:
        # Perform search
        search_results = google_search(query, num=4)
        
        if not search_results:
            print("No search results found.")
            return
        
        print(f"Found {len(search_results)} results. Starting to scrape...\n")
        
        # Scrape each result
        for i, result in enumerate(search_results, start=1):
            print(f"\n SEARCH RESULT #{i}")
            print(f" Original Link: {result['link']}")
            print(f" Original Title: {result['title']}")
            print(f" Snippet: {result['snippet']}")
            print()
            
            # Scrape the webpage
            scraped_data = scrape_webpage(result['link'])
            display_scraped_content(scraped_data)
            
            # Add delay between requests to be respectful
            if i < len(search_results):
                time.sleep(2)
    
    except ValueError as e:
        print(f" Configuration Error: {e}")
        print("Make sure your .env file contains CUSTOM_SEARCH_API and CSE_ID")
    except Exception as e:
        print(f" Unexpected Error: {e}")

if __name__ == "__main__":
    main()