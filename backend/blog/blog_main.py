import os
import json
import re
import requests
from bs4 import BeautifulSoup
import time
from urllib.parse import quote_plus, urlparse
from flask import Flask, request, jsonify, session
from flask_cors import CORS
from dotenv import load_dotenv
import google.generativeai as genai
from youtube_transcript_api import YouTubeTranscriptApi
from pytube import YouTube
import logging

# Import the robust YouTube blog generator
from youtube_blog_generator import generate_blog_from_youtube

# ------------------------------
# Flask setup
# ------------------------------
app = Flask(__name__)
app.secret_key = os.urandom(24)
CORS(app, supports_credentials=True, origins=["http://localhost:3000"])

# ------------------------------
# Load env variables and configure AI
# ------------------------------
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    raise ValueError("GEMINI_API_KEY not found in .env")

# Remove quotes if present in API key
api_key = api_key.strip('"\'')

# Configure Gemini
genai.configure(api_key=api_key)

# ------------------------------
# Hybrid Research System: Google Custom Search API + Targeted Scraping
# ------------------------------
class AccuracyResearcher:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
        })
        
        # Google Custom Search API configuration
        self.google_api_key = "AIzaSyBulaFMZql3n6-mtJnHF55371CYtJu_9R8"
        # Primary search engine ID - Using user's custom search engine
        self.search_engine_id = "417dbc2216a1d4406"
        
        # Backup search engine IDs - using user's custom search engine as primary
        self.backup_search_engines = [
            "417dbc2216a1d4406",  # User's custom search engine
            # Create new search engines at: https://cse.google.com/cse/create/new
            # Make sure to select "Search the entire web" option
            "017576662512468239146:omuauf_lfve",  # Fallback
            # If above fail, we'll use a simplified approach with direct Google API
        ]
        
        # High-priority websites for direct scraping
        self.priority_websites = {
            'mitwpu.edu.in': {
                'search_url': 'https://mitwpu.edu.in/faculty/{}',  # We'll modify this in the search method
                'content_selectors': ['.faculty-profile', '.content-area', '.faculty-details', '.profile-content', 'article', 'main', '.content-wrapper', '.faculty-info', '.bio', '.about']
            },
            'wikipedia.org': {
                'search_url': 'https://en.wikipedia.org/wiki/{}',
                'content_selectors': ['.mw-parser-output', '.mw-content-text', 'article', 'main']
            },
            'linkedin.com': {
                'search_url': 'https://www.linkedin.com/search/results/content/?keywords={}',
                'content_selectors': ['.feed-shared-update-v2__description', '.share-update-card__update-text', 'article']
            },
            'scholar.google.com': {
                'search_url': 'https://scholar.google.com/scholar?q={}',
                'content_selectors': ['.gs_rs', '.gs_a', '.gs_fl']
            },
            'researchgate.net': {
                'search_url': 'https://www.researchgate.net/search?q={}',
                'content_selectors': ['.nova-legacy-c-card__body', '.publication-item__title', '.publication-item__summary']
            },
            'ipindiaonline.gov.in': {
                'search_url': 'https://ipindiaonline.gov.in/search?q={}',
                'content_selectors': ['.content-body', '.search-result', 'article', 'main']
            },
            'orcid.org': {
                'search_url': 'https://orcid.org/orcid-search/search?searchQuery={}',
                'content_selectors': ['.work-title', '.work-subtitle', '.research-resource-title']
            },
            'scopus.com': {
                'search_url': 'https://www.scopus.com/results/results.uri?s={}',
                'content_selectors': ['.documentTitle', '.abstract', '.sourceTitle']
            }
        }
        
        # Additional target websites for comprehensive coverage
        self.target_websites = [
            "mitwpu.edu.in", "wikipedia.org", "britannica.com", "nationalgeographic.com",
            "scientificamerican.com", "nature.com", "reuters.com", "bbc.com",
            "cnn.com", "forbes.com", "harvard.edu", "mit.edu", "stanford.edu",
            "arxiv.org", "coursera.org", "edx.org", "investopedia.com",
            "healthline.com", "mayoclinic.org", "nasa.gov", "who.int",
            "unesco.org", "worldbank.org", "techcrunch.com", "wired.com"
        ]
    
    def google_custom_search(self, query, num_results=8):
        """Perform Google Custom Search API search with fallback options"""
        search_url = "https://www.googleapis.com/customsearch/v1"
        
        # Try each search engine configuration
        for engine_id in self.backup_search_engines:
            try:
                params = {
                    'key': self.google_api_key,
                    'cx': engine_id,
                    'q': query,
                    'num': num_results
                }
                
                print(f"🔍 Searching Google for: '{query}' with engine {engine_id}")
                
                response = requests.get(search_url, params=params, timeout=15)
                print(f"📡 Response Status: {response.status_code}")
                
                if response.status_code == 200:
                    search_results = response.json()
                    items = search_results.get('items', [])
                    
                    if len(items) > 0:
                        print(f"✅ Google Custom Search returned {len(items)} results")
                        return items
                    else:
                        print(f"⚠️ No results from engine {engine_id}, trying next...")
                        # Debug info for empty results
                        if 'error' in search_results:
                            print(f"❌ API Error: {search_results['error']}")
                        continue
                        
                else:
                    print(f"❌ Search engine {engine_id} error: {response.status_code}")
                    if response.status_code == 403:
                        print("⚠️ API access forbidden - trying next search engine")
                    elif response.status_code == 400:
                        print("⚠️ Bad request - trying next search engine")
                    elif response.status_code == 429:
                        print("⚠️ Rate limit exceeded")
                    
                    # Print error details
                    try:
                        error_details = response.json()
                        print(f"📄 Error details: {error_details}")
                    except:
                        print(f"� Raw response: {response.text[:200]}")
                    
                    continue
                    
            except Exception as e:
                print(f"❌ Search engine {engine_id} failed: {e}")
                continue
        
        # If all search engines fail, try a simpler query approach
        print("🔄 All search engines failed, trying simplified search...")
        try:
            simple_query = query.split()[0] if len(query.split()) > 0 else query
            params = {
                'key': self.google_api_key,
                'cx': self.backup_search_engines[0],  # Use first engine
                'q': simple_query,
                'num': 5
            }
            
            response = requests.get(search_url, params=params, timeout=15)
            if response.status_code == 200:
                search_results = response.json()
                items = search_results.get('items', [])
                print(f"� Simplified search returned {len(items)} results")
                return items
                
        except Exception as e:
            print(f"❌ Simplified search also failed: {e}")
        
        print("❌ All Google Custom Search attempts failed - using enhanced fallback methods")
        
        # Ultimate fallback: Direct search on major sites
        print("🔄 Trying direct search on major authoritative sites...")
        return self.direct_major_site_search(query)
    
    def direct_major_site_search(self, query):
        """Direct search on major sites when Google Custom Search fails"""
        print("🌐 Direct search on major authoritative websites...")
        results = []
        
        # List of major sites to search directly
        major_sites = [
            {
                'name': 'Wikipedia',
                'search_url': 'https://en.wikipedia.org/w/api.php',
                'params': {
                    'action': 'query',
                    'list': 'search',
                    'srsearch': query,
                    'format': 'json',
                    'srlimit': 3
                }
            }
        ]
        
        for site in major_sites:
            try:
                print(f"  🔍 Searching {site['name']}...")
                response = self.session.get(site['search_url'], params=site['params'], timeout=15)
                
                if response.status_code == 200:
                    data = response.json()
                    
                    if site['name'] == 'Wikipedia':
                        search_results = data.get('query', {}).get('search', [])
                        for result in search_results:
                            page_title = result.get('title', '')
                            snippet = result.get('snippet', '').replace('<span class="searchmatch">', '').replace('</span>', '')
                            page_url = f"https://en.wikipedia.org/wiki/{page_title.replace(' ', '_')}"
                            
                            results.append({
                                'link': page_url,
                                'title': page_title,
                                'snippet': snippet
                            })
                            print(f"    ✅ Found: {page_title}")
                        
            except Exception as e:
                print(f"    ❌ Error searching {site['name']}: {e}")
                continue
        
        print(f"🔄 Direct search found {len(results)} results")
        return results
    
    def search_priority_websites(self, topic):
        """Direct search on priority websites"""
        print("🎯 Searching priority websites directly...")
        results = []
        
        for website, config in self.priority_websites.items():
            try:
                # Special handling for MIT-WPU
                if website == 'mitwpu.edu.in':
                    # Try multiple MIT-WPU URL patterns
                    mitwpu_urls = [
                        f"https://mitwpu.edu.in/faculty/{quote_plus(topic.lower().replace(' ', '-'))}",
                        f"https://mitwpu.edu.in/faculty-profile/{quote_plus(topic.lower().replace(' ', '-'))}",
                        f"https://mitwpu.edu.in/our-faculty/{quote_plus(topic.lower().replace(' ', '-'))}",
                        "https://mitwpu.edu.in/faculty",
                        "https://mitwpu.edu.in/schools/school-of-engineering-and-technology/computer-engineering-and-technology/faculty"
                    ]
                    
                    for search_url in mitwpu_urls:
                        try:
                            print(f"  🔍 Trying {search_url}...")
                            response = self.session.get(search_url, timeout=15)
                            if response.status_code == 200:
                                soup = BeautifulSoup(response.content, 'html.parser')
                                
                                # Look for faculty information containing the search topic
                                content_parts = []
                                page_text = soup.get_text().lower()
                                
                                # Check if the topic appears on the page
                                if any(keyword.lower() in page_text for keyword in topic.split()):
                                    # Extract content using configured selectors
                                    for selector in config['content_selectors']:
                                        elements = soup.select(selector)[:3]
                                        for elem in elements:
                                            text = elem.get_text().strip()
                                            if text and len(text) > 50 and any(keyword.lower() in text.lower() for keyword in topic.split()):
                                                content_parts.append(text)
                                    
                                    # If specific selectors don't work, get relevant paragraphs
                                    if not content_parts:
                                        all_paragraphs = soup.find_all('p')
                                        for p in all_paragraphs:
                                            text = p.get_text().strip()
                                            if text and len(text) > 50 and any(keyword.lower() in text.lower() for keyword in topic.split()):
                                                content_parts.append(text)
                                                if len(content_parts) >= 3:
                                                    break
                                
                                if content_parts:
                                    combined_content = ' '.join(content_parts)[:1200]
                                    results.append({
                                        'source': website,
                                        'content': combined_content,
                                        'url': search_url,
                                        'title': f"{topic} - MIT-WPU Faculty"
                                    })
                                    print(f"    ✅ Extracted content from {website}")
                                    break  # Found content, no need to try other URLs
                        except Exception as e:
                            continue  # Try next URL
                
                # Special handling for Wikipedia
                elif website == 'wikipedia.org':
                    # Try multiple Wikipedia article name formats
                    wiki_topic_formats = [
                        topic.replace(' ', '_'),  # Standard format: "Artificial intelligence" -> "Artificial_intelligence"
                        topic.title().replace(' ', '_'),  # Title case: "artificial intelligence" -> "Artificial_Intelligence"
                        topic.replace(' ', ''),  # No spaces: "artificial intelligence" -> "artificialintelligence"
                        '_'.join(word.capitalize() for word in topic.split()),  # Each word capitalized
                    ]
                    
                    for wiki_format in wiki_topic_formats:
                        try:
                            search_url = f"https://en.wikipedia.org/wiki/{quote_plus(wiki_format)}"
                            print(f"  🔍 Trying Wikipedia: {search_url}")
                            
                            response = self.session.get(search_url, timeout=15)
                            if response.status_code == 200:
                                soup = BeautifulSoup(response.content, 'html.parser')
                                
                                # Extract content from Wikipedia article
                                content_div = soup.find('div', {'class': 'mw-parser-output'})
                                if content_div:
                                    # Get the first few paragraphs (introductory content)
                                    paragraphs = content_div.find_all('p')[:5]
                                    content_parts = []
                                    
                                    for p in paragraphs:
                                        text = p.get_text().strip()
                                        if text and len(text) > 30:  # Filter out very short paragraphs
                                            # Remove citation markers like [1], [2], etc.
                                            text = re.sub(r'\[\d+\]', '', text)
                                            content_parts.append(text)
                                    
                                    if content_parts:
                                        combined_content = ' '.join(content_parts)[:1500]
                                        results.append({
                                            'source': website,
                                            'content': combined_content,
                                            'url': search_url,
                                            'title': f"{topic} - Wikipedia"
                                        })
                                        print(f"    ✅ Extracted content from Wikipedia")
                                        break  # Found content, no need to try other formats
                        except Exception as e:
                            continue  # Try next format
                else:
                    # Standard search for other websites
                    search_url = config['search_url'].format(quote_plus(topic))
                    print(f"  🔍 Searching {website}...")
                    
                    response = self.session.get(search_url, timeout=15)
                    if response.status_code == 200:
                        soup = BeautifulSoup(response.content, 'html.parser')
                        
                        # Extract content using configured selectors
                        content_parts = []
                        for selector in config['content_selectors']:
                            elements = soup.select(selector)[:3]  # Get top 3 matches
                            for elem in elements:
                                text = elem.get_text().strip()
                                if text and len(text) > 50:
                                    content_parts.append(text)
                        
                        if content_parts:
                            combined_content = ' '.join(content_parts)[:1000]
                            results.append({
                                'source': website,
                                'content': combined_content,
                                'url': search_url,
                                'title': f"{topic} - {website}"
                            })
                            print(f"    ✅ Extracted content from {website}")
                        else:
                            print(f"    ⚠️ No content found on {website}")
                    else:
                        print(f"    ❌ Failed to access {website} (status: {response.status_code})")
                        
            except Exception as e:
                print(f"    ❌ Error searching {website}: {e}")
                continue
                
        return results
    
    def scrape_specific_sites(self, topic):
        """Scrape specific high-quality websites"""
        print("🌐 Scraping additional authoritative sources...")
        results = []
        
        # Direct URLs for specific topics
        direct_searches = [
            f"site:wikipedia.org {topic}",
            f"site:britannica.com {topic}",
            f"site:nature.com {topic}",
            f"site:arxiv.org {topic}",
            f"site:harvard.edu {topic}",
            f"site:mit.edu {topic}",
            f"site:reuters.com {topic}",
            f"site:bbc.com {topic}"
        ]
        
        # Use DuckDuckGo for site-specific searches
        for search_query in direct_searches[:6]:  # Limit to avoid overwhelming
            try:
                duckduckgo_results = self.search_duckduckgo(search_query, 2)
                for result in duckduckgo_results:
                    url = result.get('link', '')
                    if url:
                        # Fix malformed URLs
                        if url.startswith('//'):
                            url = 'https:' + url
                        elif not url.startswith(('http://', 'https://')):
                            url = 'https://' + url
                        
                        # Validate URL
                        try:
                            parsed = urlparse(url)
                            if parsed.netloc:  # Valid URL with domain
                                content = self.extract_content_from_url(url)
                                if content:
                                    results.append({
                                        'source': parsed.netloc,
                                        'content': content,
                                        'url': url,
                                        'title': result.get('title', f"{topic} research")
                                    })
                                    print(f"    ✅ Scraped {parsed.netloc}")
                        except Exception as url_error:
                            print(f"❌ Invalid URL skipped: {url}")
                            continue
                            
            except Exception as e:
                continue
                
        return results
    
    def search_duckduckgo(self, query, num_results=5):
        """Search using DuckDuckGo"""
        try:
            search_url = "https://duckduckgo.com/html/"
            params = {'q': query}
            
            response = self.session.get(search_url, params=params, timeout=15)
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                results = []
                
                result_divs = soup.find_all('div', {'class': 'result'})[:num_results]
                for div in result_divs:
                    try:
                        link_elem = div.find('a', {'class': 'result__a'})
                        if link_elem:
                            url = link_elem.get('href', '')
                            title = link_elem.get_text().strip()
                            
                            snippet_elem = div.find('a', {'class': 'result__snippet'})
                            snippet = snippet_elem.get_text().strip() if snippet_elem else ""
                            
                            if url and title:
                                results.append({
                                    'link': url,
                                    'title': title,
                                    'snippet': snippet
                                })
                    except Exception:
                        continue
                        
                return results
            return []
        except Exception as e:
            print(f"❌ DuckDuckGo search failed: {e}")
            return []
    
    def extract_content_from_url(self, url):
        """Enhanced content extraction for various websites"""
        try:
            # Fix malformed URLs
            if url.startswith('//'):
                url = 'https:' + url
            elif not url.startswith(('http://', 'https://')):
                url = 'https://' + url
            
            # Validate URL before attempting to access
            parsed_url = urlparse(url)
            if not parsed_url.netloc:
                print(f"❌ Invalid URL: {url}")
                return None
                
            response = self.session.get(url, timeout=15)
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Remove unwanted elements
                for element in soup(["script", "style", "nav", "header", "footer", "aside", "ad"]):
                    element.decompose()
                
                content = ""
                domain = urlparse(url).netloc.lower()
                
                # Website-specific extraction strategies
                if 'mitwpu.edu.in' in domain:
                    # MIT-WPU specific extraction
                    faculty_content = soup.find('div', {'class': 'faculty-profile'}) or \
                                    soup.find('div', {'class': 'profile-content'}) or \
                                    soup.find('div', {'class': 'faculty-details'}) or \
                                    soup.find('section', {'class': 'content-area'})
                    
                    if faculty_content:
                        # Extract faculty-specific information
                        content_parts = []
                        
                        # Look for specific faculty information
                        for selector in ['.faculty-name', '.designation', '.qualification', '.experience', 
                                       '.research-interests', '.publications', '.achievements']:
                            element = faculty_content.find(selector.replace('.', ''), {'class': selector[1:]})
                            if element:
                                content_parts.append(element.get_text().strip())
                        
                        # If no specific selectors found, get all paragraphs
                        if not content_parts:
                            paragraphs = faculty_content.find_all('p')[:6]
                            content_parts = [p.get_text().strip() for p in paragraphs if p.get_text().strip()]
                        
                        content = ' '.join(content_parts)
                    else:
                        # Fallback to general content extraction
                        main_content = soup.find('main') or soup.find('article') or soup.find('div', {'class': 'content-wrapper'})
                        if main_content:
                            paragraphs = main_content.find_all('p')[:6]
                            content = ' '.join([p.get_text().strip() for p in paragraphs])
                        
                elif 'wikipedia.org' in domain:
                    content_div = soup.find('div', {'class': 'mw-parser-output'})
                    if content_div:
                        paragraphs = content_div.find_all('p')[:4]
                        content = ' '.join([p.get_text().strip() for p in paragraphs])
                        
                elif 'linkedin.com' in domain:
                    post_content = soup.find('div', {'class': 'feed-shared-update-v2__description'})
                    if not post_content:
                        post_content = soup.find('article') or soup.find('main')
                    if post_content:
                        content = post_content.get_text().strip()[:800]
                        
                elif 'scholar.google.com' in domain:
                    abstracts = soup.find_all('div', {'class': 'gs_rs'})[:3]
                    content = ' '.join([abs.get_text().strip() for abs in abstracts])
                    
                elif 'researchgate.net' in domain:
                    publication_body = soup.find('div', {'class': 'nova-legacy-c-card__body'})
                    if publication_body:
                        content = publication_body.get_text().strip()[:800]
                        
                elif 'nature.com' in domain or 'arxiv.org' in domain:
                    abstract = soup.find('div', {'class': 'c-article-section__content'}) or soup.find('blockquote', {'class': 'abstract'})
                    if abstract:
                        content = abstract.get_text().strip()[:800]
                    else:
                        paragraphs = soup.find_all('p')[:4]
                        content = ' '.join([p.get_text().strip() for p in paragraphs])
                        
                elif any(news_site in domain for news_site in ['reuters.com', 'bbc.com', 'cnn.com']):
                    article_body = soup.find('div', {'class': ['story-body', 'article-body', 'story-content']})
                    if not article_body:
                        article_body = soup.find('article') or soup.find('main')
                    if article_body:
                        paragraphs = article_body.find_all('p')[:4]
                        content = ' '.join([p.get_text().strip() for p in paragraphs])
                        
                else:
                    # Generic extraction
                    main_content = soup.find('main') or soup.find('article') or soup.find('div', {'class': ['content', 'main-content']})
                    if main_content:
                        paragraphs = main_content.find_all('p')[:4]
                        content = ' '.join([p.get_text().strip() for p in paragraphs])
                    else:
                        paragraphs = soup.find_all('p')[:4]
                        content = ' '.join([p.get_text().strip() for p in paragraphs])
                
                if content and len(content) > 100:
                    return content[:1000]
                    
        except Exception as e:
            print(f"❌ Failed to extract from {url}: {e}")
            
        return None
    
    def research_topic(self, topic):
        """Google Custom Search API Only - Simple and Fast"""
        print(f"\n� GOOGLE CUSTOM SEARCH for '{topic}'")
        print("=" * 60)
        
        all_research_data = []
        
        # Google Custom Search API - Multiple queries for comprehensive results
        print("📡 Google Custom Search API")
        
        # Try multiple search queries to get comprehensive results
        search_queries = [
            f"{topic} research facts statistics",
            f"{topic} overview information",
            f"{topic} latest developments",
            f"{topic} expert analysis",
            f"what is {topic}"
        ]
        
        for query in search_queries:
            print(f"🔍 Searching: '{query}'")
            google_results = self.google_custom_search(query, num_results=5)
            
            for result in google_results:
                try:
                    url = result.get('link', '')
                    title = result.get('title', '')
                    snippet = result.get('snippet', '')
                    
                    # Extract detailed content from the URL
                    extracted_content = self.extract_content_from_url(url)
                    content = extracted_content if extracted_content else snippet
                    
                    if content and len(content) > 80:
                        # Check if we already have this domain to avoid duplicates
                        domain = urlparse(url).netloc
                        if not any(item['source'] == domain for item in all_research_data):
                            all_research_data.append({
                                'source': domain,
                                'content': content,
                                'url': url,
                                'title': title,
                                'method': 'Google Custom Search'
                            })
                            print(f"  ✅ Added: {domain}")
                        
                except Exception as e:
                    continue
            
            # Stop if we have enough results
            if len(all_research_data) >= 10:
                break
        
        print(f"\n📊 RESEARCH SUMMARY:")
        print(f"  • Total sources found: {len(all_research_data)}")
        for result in all_research_data:
            print(f"    - {result['source']} ({result['method']})")
        
        if all_research_data:
            combined_content = "\n\n".join([
                f"From {data['source']}: {data['content']}"
                for data in all_research_data
            ])
            return {
                "content": combined_content,
                "internal_sources": [data['url'] for data in all_research_data],
                "research_summary": {
                    "total_sources": len(all_research_data),
                    "google_results": len([r for r in all_research_data if r['method'] == 'Google Custom Search'])
                }
            }
        else:
            return {
                "content": f"Comprehensive research about {topic} from multiple authoritative sources.",
                "internal_sources": [],
                "research_summary": {"total_sources": 0, "note": "No results found"}
            }

# ------------------------------
# YouTube Video Processor with Genkit Integration
# ------------------------------
class YouTubeVideoProcessor:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        })
    
    def extract_video_id(self, url):
        """Extract video ID from various YouTube URL formats"""
        patterns = [
            r'(?:youtube\.com\/watch\?v=|youtu\.be\/|youtube\.com\/embed\/|youtube\.com\/v\/|m\.youtube\.com\/watch\?v=)([^&\n?#]+)',
            r'youtube\.com\/watch\?.*v=([^&\n?#]+)',
            r'youtu\.be\/([^&\n?#]+)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        return None
    
    def get_video_metadata(self, video_id):
        """Get video metadata using multiple fallback methods"""
        # Method 1: Try pytube first
        try:
            video_url = f"https://www.youtube.com/watch?v={video_id}"
            yt = YouTube(video_url)
            
            return {
                'title': yt.title,
                'description': yt.description,
                'author': yt.author,
                'length': yt.length,
                'views': yt.views,
                'publish_date': str(yt.publish_date) if yt.publish_date else None,
                'keywords': yt.keywords if yt.keywords else []
            }
        except Exception as e:
            print(f"⚠️ Pytube failed: {e}")
            
        # Method 2: Try web scraping as fallback
        try:
            video_url = f"https://www.youtube.com/watch?v={video_id}"
            response = self.session.get(video_url)
            
            if response.status_code == 200:
                html_content = response.text
                
                # Extract title
                title_match = re.search(r'"title":"([^"]+)"', html_content)
                title = title_match.group(1) if title_match else f"YouTube Video {video_id}"
                
                # Extract author/channel name
                author_match = re.search(r'"author":"([^"]+)"', html_content)
                author = author_match.group(1) if author_match else "Unknown Channel"
                
                # Extract length in seconds
                length_match = re.search(r'"lengthSeconds":"(\d+)"', html_content)
                length = int(length_match.group(1)) if length_match else 0
                
                # Extract view count
                view_match = re.search(r'"viewCount":"(\d+)"', html_content)
                views = int(view_match.group(1)) if view_match else 0
                
                # Extract description
                desc_match = re.search(r'"shortDescription":"([^"]*)"', html_content)
                description = desc_match.group(1)[:500] if desc_match else ""
                
                return {
                    'title': title.encode().decode('unicode_escape'),
                    'description': description.encode().decode('unicode_escape'),
                    'author': author.encode().decode('unicode_escape'),
                    'length': length,
                    'views': views,
                    'publish_date': None,
                    'keywords': []
                }
        except Exception as e:
            print(f"⚠️ Web scraping fallback failed: {e}")
            
        # Method 3: Basic fallback with just video ID
        print("⚠️ Using basic fallback metadata")
        return {
            'title': f"YouTube Video {video_id}",
            'description': "Video description not available",
            'author': "Unknown Channel",
            'length': 0,
            'views': 0,
            'publish_date': None,
            'keywords': []
        }
    
    def get_video_transcript(self, video_id):
        """Get video transcript using YouTube Transcript API"""
        try:
            # Try to get transcript in English first
            transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
            
            # Try to get English transcript
            try:
                transcript = transcript_list.find_transcript(['en', 'en-US', 'en-GB'])
                transcript_data = transcript.fetch()
            except:
                # If English not available, get the first available transcript
                try:
                    transcript = transcript_list.find_generated_transcript(['en'])
                    transcript_data = transcript.fetch()
                except:
                    # Get any available transcript
                    transcript = list(transcript_list)[0]
                    transcript_data = transcript.fetch()
            
            # Combine transcript text
            full_text = ' '.join([entry['text'] for entry in transcript_data])
            
            # Clean up the text
            full_text = re.sub(r'\[.*?\]', '', full_text)  # Remove [Music], [Applause], etc.
            full_text = re.sub(r'\s+', ' ', full_text).strip()  # Normalize whitespace
            
            return {
                'text': full_text,
                'language': transcript.language_code,
                'is_generated': transcript.is_generated,
                'entries': transcript_data[:10]  # First 10 entries for reference
            }
            
        except Exception as e:
            print(f"❌ Error getting video transcript: {e}")
            return None
    
    def generate_content_without_transcript(self, video_id, video_url, metadata, additional_context=""):
        """Generate blog content when transcript is not available using Genkit research"""
        print("🔍 Generating content without transcript using Genkit research...")
        
        try:
            # Extract key information from metadata
            title = metadata.get('title', 'Unknown Title')
            author = metadata.get('author', 'Unknown Author')
            description = metadata.get('description', '')
            keywords = metadata.get('keywords', [])
            
            # Create search queries based on video metadata
            search_queries = []
            
            # Primary search query from title
            search_queries.append(title)
            
            # Add author-specific search if available
            if author and author != 'Unknown Author':
                search_queries.append(f"{author} {title}")
            
            # Add keyword-based searches
            if keywords:
                top_keywords = keywords[:3]  # Use top 3 keywords
                search_queries.append(' '.join(top_keywords))
            
            # Extract topic from description if available
            if description:
                # Use first 100 characters of description for context
                description_snippet = description[:100].strip()
                if description_snippet:
                    search_queries.append(description_snippet)
            
            print(f"🔍 Generated {len(search_queries)} search queries for research")
            
            # Research the topic using Google Custom Search
            research_content = []
            for i, query in enumerate(search_queries[:2]):  # Limit to 2 searches to avoid rate limits
                print(f"📚 Researching query {i+1}: {query}")
                try:
                    search_results = self.search_google(query, num_results=3)
                    if search_results:
                        for result in search_results:
                            research_content.append({
                                'title': result.get('title', ''),
                                'snippet': result.get('snippet', ''),
                                'link': result.get('link', '')
                            })
                        print(f"✅ Found {len(search_results)} research sources for query: {query}")
                    else:
                        print(f"⚠️ No results found for query: {query}")
                except Exception as e:
                    print(f"❌ Error searching for query '{query}': {e}")
                    continue
            
            # Generate blog content using Genkit with research data
            blog_content = self.generate_blog_with_research(video_id, video_url, metadata, research_content, additional_context)
            
            if blog_content:
                return {
                    'success': True,
                    'video_id': video_id,
                    'video_url': video_url,
                    'metadata': metadata,
                    'transcript': None,  # No transcript available
                    'research_data': research_content,
                    'blog_content': blog_content,
                    'content_summary': {
                        'title': metadata['title'],
                        'author': metadata['author'],
                        'duration_minutes': round(metadata['length'] / 60, 1) if metadata['length'] > 0 else 'Unknown',
                        'has_transcript': False,
                        'research_sources': len(research_content),
                        'generation_method': 'Metadata + Research + Genkit'
                    }
                }
            else:
                return {
                    'error': 'Failed to generate blog content using research method',
                    'success': False,
                    'metadata': metadata
                }
                
        except Exception as e:
            print(f"❌ Error in generate_content_without_transcript: {e}")
            return {
                'error': f'Error generating content without transcript: {str(e)}',
                'success': False,
                'metadata': metadata
            }
    
    def generate_blog_with_research(self, video_id, video_url, metadata, research_content, additional_context=""):
        """Generate blog using video metadata and research data with Genkit"""
        try:
            # Prepare research context
            research_text = ""
            if research_content:
                research_text = "\n\n**Research Sources:**\n"
                for i, source in enumerate(research_content, 1):
                    research_text += f"\n{i}. **{source['title']}**\n"
                    research_text += f"   {source['snippet']}\n"
                    research_text += f"   Source: {source['link']}\n"
            
            # Prepare metadata context
            duration_text = f"{round(metadata['length'] / 60, 1)} minutes" if metadata['length'] > 0 else "Duration unknown"
            keywords_text = ', '.join(metadata.get('keywords', [])[:10]) if metadata.get('keywords') else "No keywords available"
            description_text = metadata.get('description', '')[:500] if metadata.get('description') else "No description available"
            
            prompt = f"""
            Create a comprehensive, well-researched blog post about the following YouTube video. Since the video transcript is not available, use the video metadata and research sources to create engaging content.

            **Video Information:**
            - Title: {metadata['title']}
            - Author/Channel: {metadata['author']}
            - Duration: {duration_text}
            - Keywords: {keywords_text}
            - Video URL: {video_url}

            **Video Description:**
            {description_text}

            {research_text}

            **Additional Context (if provided):**
            {additional_context}

            **Content Generation Instructions:**
            1. Create a compelling blog title based on the video title and research
            2. Write an engaging introduction that explains what the video likely covers
            3. Use the research sources to provide comprehensive coverage of the topic
            4. Structure content with clear headings and subheadings
            5. Include insights and analysis based on the research
            6. Provide practical takeaways and actionable advice
            7. Write a strong conclusion that summarizes key points
            8. Keep the tone professional yet engaging
            9. Aim for 1200-1800 words
            10. Make it SEO-friendly with good keyword usage

            **Important Notes:**
            - Acknowledge that this content is based on research about the video topic
            - Don't claim to have watched the video or quote specific video content
            - Focus on providing value around the video's topic using the research
            - Include references to the video as a recommended resource

            **Format Requirements:**
            - Use clear headings (##) and subheadings (###)
            - Include bullet points where appropriate
            - Make paragraphs well-structured and readable
            - Include a "Key Takeaways" section
            - Add a reference to the original video

            Generate the comprehensive blog post now:
            """

            # Generate blog using Gemini
            model = genai.GenerativeModel('gemini-2.0-flash-exp')
            response = model.generate_content(prompt)
            
            if response and response.text:
                print("✅ Successfully generated blog content using research method")
                return response.text
            else:
                print("❌ Failed to generate blog content - empty response from Gemini")
                return None
                
        except Exception as e:
            print(f"❌ Error generating blog with research: {e}")
            return None
    
    def process_youtube_video(self, video_url, additional_context=""):
        """Main method to process YouTube video and extract all information"""
        print(f"🎥 Processing YouTube video: {video_url}")
        
        # Extract video ID
        video_id = self.extract_video_id(video_url)
        if not video_id:
            return {
                'error': 'Invalid YouTube URL',
                'success': False
            }
        
        print(f"📺 Video ID: {video_id}")
        
        # Get video metadata - now always returns something
        metadata = self.get_video_metadata(video_id)
        
        print(f"📝 Video Title: {metadata['title']}")
        print(f"👤 Author: {metadata['author']}")
        print(f"⏱️ Duration: {metadata['length']} seconds")
        
        # Try to get video transcript
        transcript = self.get_video_transcript(video_id)
        if not transcript:
            print("⚠️ No transcript available - will generate content based on metadata and research")
            # Use Genkit to research and generate content based on video metadata
            return self.generate_content_without_transcript(video_id, video_url, metadata, additional_context)
        
        print(f"📄 Transcript length: {len(transcript['text'])} characters")
        print(f"🌐 Transcript language: {transcript['language']}")
        
        return {
            'success': True,
            'video_id': video_id,
            'video_url': video_url,
            'metadata': metadata,
            'transcript': transcript,
            'content_summary': {
                'title': metadata['title'],
                'author': metadata['author'],
                'duration_minutes': round(metadata['length'] / 60, 1) if metadata['length'] > 0 else 'Unknown',
                'transcript_words': len(transcript['text'].split()),
                'has_transcript': True,
                'language': transcript['language']
            }
        }
    
    def generate_blog_from_video(self, video_data, additional_context=""):
        """Generate blog content from video data using Gemini"""
        if not video_data.get('success'):
            return None
        
        metadata = video_data['metadata']
        transcript = video_data['transcript']
        
        # Prepare the prompt for Gemini
        duration_text = f"{round(metadata['length'] / 60, 1)} minutes" if metadata['length'] > 0 else "Duration unknown"
        views_text = f"{metadata.get('views', 'N/A')}" if metadata.get('views') else "Views not available"
        keywords_text = ', '.join(metadata.get('keywords', [])[:10]) if metadata.get('keywords') else "No keywords available"
        description_text = metadata.get('description', '')[:500] if metadata.get('description') else "No description available"
        
        prompt = f"""
        Create a comprehensive, well-structured blog post based on the following YouTube video content:

        **Video Information:**
        - Title: {metadata['title']}
        - Author/Channel: {metadata['author']}
        - Duration: {duration_text}
        - Views: {views_text}
        - Keywords: {keywords_text}

        **Video Description:**
        {description_text}

        **Full Video Transcript:**
        {transcript['text']}

        **Additional Context (if provided):**
        {additional_context}

        **Instructions:**
        1. Create a compelling blog title that captures the main topic
        2. Write an engaging introduction that hooks the reader
        3. Structure the content with clear headings and subheadings
        4. Extract and expand on the key points from the video
        5. Include relevant examples, insights, and takeaways
        6. Add a strong conclusion with actionable points
        7. Keep the tone professional yet engaging
        8. Aim for 1000-1500 words
        9. Make it SEO-friendly with good keyword usage

        **Format the blog as follows:**
        - Use clear headings and subheadings
        - Include bullet points where appropriate
        - Make paragraphs well-structured and readable
        - Include a summary section at the end

        Generate the blog post now:
        """

        try:
            # Generate blog using Gemini
            model = genai.GenerativeModel('gemini-2.0-flash-exp')
            response = model.generate_content(prompt)
            
            if response and response.text:
                return {
                    'success': True,
                    'blog_content': response.text,
                    'source_video': {
                        'title': metadata['title'],
                        'author': metadata['author'],
                        'url': video_data['video_url'],
                        'duration': round(metadata['length'] / 60, 1)
                    },
                    'generation_info': {
                        'method': 'YouTube Video + Gemini 2.0 Flash',
                        'transcript_length': len(transcript['text']),
                        'has_captions': True
                    }
                }
            else:
                return {
                    'success': False,
                    'error': 'Failed to generate blog content'
                }
                
        except Exception as e:
            print(f"❌ Error generating blog from video: {e}")
            return {
                'success': False,
                'error': f'Blog generation failed: {str(e)}'
            }

# ------------------------------
# CrewAI-like Classes (Custom Implementation)
# ------------------------------
class Agent:
    def __init__(self, role, goal, backstory, verbose=True, allow_delegation=False, llm=None):
        self.role = role
        self.goal = goal
        self.backstory = backstory
        self.verbose = verbose
        self.allow_delegation = allow_delegation
        self.model = genai.GenerativeModel('gemini-2.5-flash')
    
    def execute(self, task_description, context="", research_data=None):
        research_context = ""
        if research_data and isinstance(research_data, dict):
            research_context = "\n\nVERIFIED RESEARCH DATA:\n"
            if research_data.get('content'):
                research_context += f"{research_data['content']}\n"
        
        prompt = f"""
You are a {self.role}.
Your goal: {self.goal}
Your backstory: {self.backstory}

Task: {task_description}

Context: {context}
{research_context}

IMPORTANT: Use the verified research data above to ensure accuracy. Include specific facts, statistics, and information from the sources. Make the content authoritative and well-researched.

Execute this task professionally and return a high-quality result.
"""
        try:
            response = self.model.generate_content(prompt)
            return response.text.strip()
        except Exception as e:
            return f"Error: {str(e)}"

class Task:
    def __init__(self, description, expected_output, agent):
        self.description = description
        self.expected_output = expected_output
        self.agent = agent
    
    def execute(self, inputs=None, research_data=None):
        context = ""
        if inputs:
            context = "\n".join([f"{k}: {v}" for k, v in inputs.items()])
        
        task_desc = self.description.format(**inputs) if inputs else self.description
        return self.agent.execute(task_desc, context, research_data)

class Process:
    sequential = "sequential"

class Crew:
    def __init__(self, agents, tasks, process=Process.sequential, memory=False):
        self.agents = agents
        self.tasks = tasks
        self.process = process
        self.memory = memory
    
    def kickoff(self, inputs=None, research_data=None):
        results = []
        context = ""
        
        for i, task in enumerate(self.tasks):
            if inputs:
                # Add previous results to inputs for context
                task_inputs = inputs.copy()
                task_inputs['previous_results'] = context
            else:
                task_inputs = {'previous_results': context}
            
            result = task.execute(task_inputs, research_data)
            results.append(result)
            
            # Build context for next task
            if i < len(self.tasks) - 1:  # Don't add to context for last task
                context += f"\n\nPrevious Task Result: {result}"
        
        # Create a result object that mimics CrewAI output
        class CrewResult:
            def __init__(self, content):
                self.raw = content
                self.content = content
            
            def __str__(self):
                return self.content
        
        return CrewResult(results[-1] if results else "No results")

# Mock LLM class for interface compatibility
class MockLLM:
    def __init__(self):
        self.model = genai.GenerativeModel('gemini-2.5-flash')
    
    def invoke(self, prompt):
        class Response:
            def __init__(self, content):
                self.content = content
        
        try:
            response = self.model.generate_content(prompt)
            return Response(response.text.strip())
        except Exception as e:
            return Response(f"Error: {str(e)}")

# Create LLM instance
llm = MockLLM()

# ------------------------------
# Blog Generator Class (Exact same structure as main.py)
# ------------------------------
class InterviewBlogGenerator:
    def __init__(self):
        # Initialize research system for accuracy
        self.researcher_tool = AccuracyResearcher()
        
        self.interviewer = Agent(
            role="Content Overview Specialist",
            goal="Provide clear overviews of planned blog content and incorporate user feedback.",
            backstory="""You are an expert content strategist who explains what will be covered in a blog post and gracefully incorporates user suggestions.""",
            verbose=True,
            allow_delegation=False,
            llm="gemini/gemini-2.0-flash"
        )
        self.researcher = Agent(
            role="Senior Research Analyst & Information Specialist",
            goal="Conduct comprehensive research and create detailed, fact-based blog outlines with current information and expert insights.",
            backstory="""You are an expert researcher with access to vast knowledge databases. You specialize in gathering comprehensive, accurate, and up-to-date information on any topic. You excel at finding specific details, statistics, examples, case studies, and expert opinions. You structure information in a way that's both informative and engaging for readers.""",
            verbose=True,
            allow_delegation=False,
            llm="gemini/gemini-2.0-flash"
        )
        self.writer = Agent(
            role="Expert Blog Writer & Storyteller",
            goal="Create engaging, well-structured blog posts that tell compelling stories while providing valuable information and insights to readers.",
            backstory="""You are a skilled digital content creator and storyteller who specializes in writing engaging blog posts that capture readers' attention from the first sentence. You excel at transforming dry facts and research into compelling narratives that are both informative and entertaining. 

Your writing style characteristics:
- You start with hooks that grab attention (questions, surprising facts, relatable scenarios)
- You structure content logically with smooth transitions between sections
- You use storytelling techniques to make information memorable
- You write in a conversational, accessible tone while maintaining professionalism
- You focus on creating narrative flow rather than academic lists
- You include human elements, personal touches, and relatable examples
- You make complex topics understandable and interesting for general audiences

You avoid academic writing style and instead create content that feels like reading an interesting magazine feature or talking to an expert friend who can explain things clearly and engagingly.""",
            verbose=True,
            allow_delegation=False,
            llm="gemini/gemini-2.0-flash"
        )
        self.stylist = Agent(
            role="Content Stylist and SEO Editor",
            goal="Format blogs with perfect Markdown, optimize for SEO, and ensure professional presentation.",
            backstory="You are an SEO and formatting expert who makes content look professional and search-engine friendly. You always return perfect JSON format.",
            verbose=True,
            allow_delegation=False,
            llm="gemini/gemini-2.0-flash"
        )
        self.research_task = Task(
            description="""Research the topic "{topic}" comprehensively using your knowledge base. Focus on:

DETAILED RESEARCH REQUIREMENTS:
For writing an engaging blog about "{topic}", gather information that will help create a compelling narrative:

**ESSENTIAL INFORMATION NEEDED:**
- Personal/Background Details: Early life, education, formative experiences
- Career Journey: Key milestones, progression, major turning points
- Achievements & Recognition: Awards, publications, notable accomplishments
- Current Role & Impact: Present position, responsibilities, influence
- Expertise Areas: Specializations, research interests, unique skills
- Future Vision: Goals, aspirations, industry outlook

**RESEARCH FOCUS AREAS:**
- Find specific dates, numbers, and factual details
- Look for interesting stories, anecdotes, or lesser-known facts
- Gather information about current projects or initiatives
- Research their impact on students, industry, or community
- Find quotes or statements that reveal personality/philosophy
- Identify what makes them unique or noteworthy in their field

CONTEXT ANALYSIS:
{context}

**STRUCTURE RESEARCH OUTPUT AS:**
- Background & Early Foundation
- Professional Journey & Key Milestones  
- Areas of Expertise & Specializations
- Current Role & Contributions
- Vision & Future Outlook
- Notable Achievements & Recognition
- Specific examples and case studies

Structure this as a detailed research brief with bullet points, facts, and comprehensive information that will enable writing an expert-level blog post.""",
            expected_output="A comprehensive research brief with detailed facts, statistics, examples, and expert insights",
            agent=self.researcher
        )
        self.write_task = Task(
            description="""Using the comprehensive research about "{topic}":
{context}
{previous_results}

Write an engaging, well-structured 1200-1500 word blog post about "{topic}" that follows this EXACT structure:

**TITLE**: Create a compelling, click-worthy title that captures attention

**INTRODUCTION** (150-200 words):
- Start with an engaging hook (question, surprising fact, or compelling statement)
- Briefly introduce who/what "{topic}" is about
- Preview what readers will learn in the blog
- Create curiosity and encourage reading

**MAIN CONTENT SECTIONS** (4-5 sections, 200-250 words each):

1. **Background & Early Life/Foundation** (if person) OR **Overview & Background** (if topic):
   - Personal background, education, early career
   - Key formative experiences and influences
   - Foundation that led to current success/recognition

2. **Professional Journey & Achievements**:
   - Career progression with specific milestones
   - Major accomplishments and recognitions
   - Key positions, roles, and responsibilities
   - Notable projects or contributions

3. **Expertise & Specializations**:
   - Areas of expertise and core competencies
   - Research interests or professional focus areas
   - Unique skills or knowledge that sets them apart
   - Publications, patents, or notable work

4. **Current Role & Impact**:
   - Present position and responsibilities
   - Current projects and initiatives
   - Impact on industry/field/students/community
   - Leadership roles and influence

5. **Vision & Future Outlook**:
   - Future goals and aspirations
   - Industry trends they're working on
   - Legacy and long-term vision
   - Advice or insights for others

**CONCLUSION** (100-150 words):
- Summarize key takeaways about "{topic}"
- Highlight their most significant contributions
- End with an inspiring or thought-provoking statement

WRITING STYLE REQUIREMENTS:
- Write in an engaging, conversational tone (not academic)
- Use storytelling elements to make it interesting
- Include specific facts, dates, numbers, and details from research
- Make it relatable and inspiring for general readers
- Use transitional phrases to connect sections smoothly
- Avoid dry, list-like academic writing

SPECIFIC DETAILS TO INCLUDE:
- Exact names, positions, institutions, dates
- Specific achievements, publications, or projects
- Real numbers, statistics, or measurable impacts
- Quotes or notable statements (if available)
- Interesting anecdotes or lesser-known facts

Make this read like a feature article that would engage and inspire readers, not like a resume or academic paper.""",
            expected_output="An engaging, well-structured blog post with narrative flow and specific details",
            agent=self.writer
        )
        self.style_task = Task(
            description="""Take the blog post and format it perfectly for web display:

{previous_results}

Your task is to transform the blog content into a professionally formatted, engaging piece that's optimized for online reading.

FORMATTING REQUIREMENTS:
1. **Title**: Create a compelling, SEO-friendly title that captures the essence of the person/topic
2. **Structure**: Use clear Markdown hierarchy:
   - # for main title
   - ## for major sections (Background, Career, Expertise, etc.)
   - ### for subsections if needed
3. **Readability**: 
   - Keep paragraphs short (2-4 sentences)
   - Use line breaks generously for visual breathing room
   - Create scannable content with clear section breaks
4. **Emphasis**:
   - Use **bold** for key names, achievements, positions, and important terms
   - Use *italic* sparingly for emphasis or quotes
   - Highlight specific numbers, dates, and statistics in **bold**
5. **Lists**: Use bullet points (-) for achievements, skills, or key points
6. **Flow**: Ensure smooth transitions between sections

CONTENT ENHANCEMENT:
- Make sure the introduction is engaging and sets up the entire piece
- Ensure each section flows naturally into the next
- Add transitional phrases between paragraphs where needed
- Maintain an inspiring, professional tone throughout

CRITICAL FORMATTING RULES:
- NO code blocks or technical formatting (```)
- NO JSON formatting in the content
- Clean, readable Markdown only
- Proper spacing and paragraph breaks
- Professional presentation suitable for publication

Return as valid JSON:
{{
  "blogContent": "Clean, well-formatted markdown blog with proper headings and NO code blocks",
  "summary": "2-3 sentence summary of the blog",  
  "keywords": ["keyword1", "keyword2", "keyword3", "keyword4", "keyword5", "keyword6", "keyword7", "keyword8"]
}}

CRITICAL: Ensure the blogContent is clean markdown suitable for web display with NO technical formatting.""",
            expected_output="Valid JSON with clean, readable blogContent and keywords",
            agent=self.stylist
        )
        self.blog_crew = Crew(
            agents=[self.researcher, self.writer, self.stylist],
            tasks=[self.research_task, self.write_task, self.style_task],
            process=Process.sequential,
            memory=False
        )

    def clean_blog_formatting(self, content):
        """Clean up blog content formatting for better UI display"""
        if not content:
            return content
            
        # Remove code blocks and JSON formatting
        content = re.sub(r'```json\s*\n?', '', content)
        content = re.sub(r'```\s*\n?', '', content)
        content = re.sub(r'`([^`]+)`', r'\1', content)  # Remove inline code formatting
        
        # Clean up excessive markdown
        content = re.sub(r'#{4,}', '###', content)  # Max 3 levels of headings
        content = re.sub(r'\*{3,}', '**', content)  # Remove triple+ asterisks
        
        # Ensure proper spacing
        content = re.sub(r'\n{3,}', '\n\n', content)  # Max 2 line breaks
        content = re.sub(r'[ \t]+\n', '\n', content)  # Remove trailing spaces
        
        # Clean up any remaining JSON-like formatting
        content = re.sub(r'{\s*"[^"]*":\s*"', '', content)
        content = re.sub(r'"\s*}', '', content)
        
        return content.strip()

    def interview_step(self, topic, user_answer=None):
        if "conversation" not in session:
            session["conversation"] = []
            session["topic"] = topic
            
            # Enhanced overview with research-based preview
            overview_prompt = f"""You are an expert content strategist creating a comprehensive blog overview for: "{topic}"

Create a detailed content overview that shows what you'll research and cover. Format it professionally with clear sections:

**📋 BLOG OVERVIEW: {topic}**

**🔍 Research Areas I'll Cover:**
• Historical background and key developments
• Current trends and latest developments  
• Important statistics and data points
• Expert insights and case studies
• Practical applications and real-world examples
• Future outlook and emerging trends

**📖 Content Structure:**
• **Introduction**: Hook readers with compelling facts about {topic}
• **Background**: Historical context and foundation knowledge
• **Current State**: Latest developments and current status
• **Key Insights**: Expert analysis and important findings  
• **Practical Applications**: Real-world uses and implementations
• **Future Trends**: What's coming next in {topic}
• **Conclusion**: Key takeaways and actionable insights

**💡 What Makes This Blog Special:**
• Research-backed information from authoritative sources
• Specific examples and case studies
• Expert-level insights and analysis
• Actionable information readers can use
• Professional formatting with proper structure

**🎯 Customization Options:**
If you want me to focus on specific aspects like:
- Target audience (beginners, professionals, students)
- Specific subtopics or angles
- Industry focus or applications
- Technical depth level
- Length preferences

Just let me know your preferences, or I'll create a comprehensive, well-researched blog covering all key aspects of {topic}!

Ready to proceed with research and writing?"""
            
            try:
                response = self.interviewer.execute(overview_prompt, "")
                formatted_overview = response if response and len(response) > 100 else overview_prompt
                session["conversation"].append({"role": "agent", "content": formatted_overview})
                session.modified = True
                return formatted_overview
            except Exception as e:
                return overview_prompt

        if user_answer:
            session["conversation"].append({"role": "user", "content": user_answer})
            session.modified = True
            
            # Enhanced response that acknowledges customization
            customization_response = f"""Perfect! I've noted your specific requirements for the {topic} blog:

**Your Customization Requests:**
"{user_answer}"

**How I'll Incorporate This:**
• I'll adjust the research focus based on your preferences
• The content depth and style will match your specified audience
• Any specific subtopics you mentioned will get extra attention
• The tone and technical level will be tailored accordingly

**Enhanced Research Process:**
• I'll research authoritative sources (Wikipedia, Britannica, academic sources)
• Extract verified facts, statistics, and expert insights
• Structure content according to your preferences
• Ensure accuracy with fact-checking from multiple sources

Ready to generate your customized, research-backed blog post! The system will now:
1. 🔍 Research from trusted sources
2. 📊 Extract factual data and statistics  
3. ✍️ Create your customized blog
4. 🎯 Format for maximum impact

Click "Generate Blog" to start the research and writing process!"""
            
            return customization_response

        # Fallback
        return "Ready to create your detailed, research-based blog! Click generate to start."

    def generate_blog(self):
        topic = session.get("topic")
        conversation = session.get("conversation", [])
        
        # Extract user preferences from conversation
        user_preferences = ""
        for msg in conversation:
            if msg["role"] == "user":
                user_preferences += f" {msg['content']}"

        try:
            # Step 1: Research the topic for accuracy
            print(f"🔍 Starting comprehensive research for: {topic}")
            research_data = self.researcher_tool.research_topic(topic)
            
            if not research_data:
                research_data = {"sources": [], "content": f"General information about {topic}"}
            
            # Step 2: Create enhanced context with research data
            enhanced_context = f"""Create an exceptional, research-backed blog post about: {topic}

RESEARCH DATA AVAILABLE:
{research_data.get('content', '')}

USER CUSTOMIZATION:
{user_preferences if user_preferences else 'Create comprehensive coverage of the topic'}

BLOG REQUIREMENTS:
- Use the research data to provide accurate, specific information
- Include facts, statistics, and verified details from authoritative sources
- Structure as a professional, engaging blog post (1000+ words)
- Add specific examples, case studies, and real-world applications
- Use expert-level insights while remaining accessible
- Include proper headings and subheadings for readability
- Ensure all claims are accurate and supportable
- Add actionable advice and practical takeaways

TARGET AUDIENCE: Educated readers seeking comprehensive, accurate information
TONE: Professional yet engaging, authoritative but accessible
LENGTH: 1000-1500 words with proper structure"""

            # Execute blog generation with research context
            print("✍️ Generating research-backed blog content...")
            result = self.blog_crew.kickoff(inputs={
                "topic": topic,
                "context": enhanced_context
            }, research_data=research_data)
            
            raw_output = result.raw if hasattr(result, "raw") else str(result)
            
            # More aggressive JSON cleaning
            clean_json = re.sub(r"```json\n|\n```|```", "", raw_output).strip()
            
            # Remove any text before the first { and after the last }
            start_idx = clean_json.find('{')
            end_idx = clean_json.rfind('}')
            
            if start_idx != -1 and end_idx != -1:
                clean_json = clean_json[start_idx:end_idx+1]
            
            try:
                data = json.loads(clean_json)
                # Ensure all required fields exist
                if not isinstance(data.get('blogContent'), str):
                    raise ValueError("Invalid blogContent")
                if not isinstance(data.get('summary'), str):
                    data['summary'] = f"A comprehensive, research-backed guide about {topic}"
                if not isinstance(data.get('keywords'), list):
                    data['keywords'] = [topic.lower(), "guide", "research", "facts", "expert analysis"]
                
                # Clean up the blog content formatting
                data['blogContent'] = self.clean_blog_formatting(data['blogContent'])
                
                # DO NOT add source attribution to visible content
                # Sources are kept internal for research accuracy only
                    
            except (json.JSONDecodeError, ValueError):
                # If JSON parsing fails, create a manual response without research sources
                cleaned_content = self.clean_blog_formatting(f"# {topic}\n\n{raw_output}")
                data = {
                    "blogContent": cleaned_content,
                    "summary": f"A comprehensive, research-backed guide about {topic}",
                    "keywords": [topic.lower(), "guide", "research", "facts", "expert analysis"]
                }
                
        except Exception as e:
            print(f"❌ Error in research-backed generation: {str(e)}")
            # Fallback to basic generation
            try:
                basic_context = f"Create a detailed, informative blog post about {topic}. User preferences: {user_preferences}"
                result = self.blog_crew.kickoff(inputs={
                    "topic": topic,
                    "context": basic_context
                })
                raw_output = result.raw if hasattr(result, "raw") else str(result)
                data = {
                    "blogContent": f"# {topic}\n\n{raw_output}",
                    "summary": f"A comprehensive guide about {topic}",
                    "keywords": [topic.lower(), "guide", "tips", "tutorial", "blog"]
                }
            except:
                data = {
                    "blogContent": f"# Error Generating Blog\n\nSorry, there was an error generating your blog about {topic}. Please try again.",
                    "summary": "Error generating blog",
                    "keywords": ["error"]
                }

        session.clear()
        print("✅ Blog generation completed!")
        return data

# Create an instance of the generator
blog_generator = InterviewBlogGenerator()

# --- API Routes (Exact same as main.py) ---
@app.route("/interview", methods=["POST"])
def interview():
    data = request.get_json()
    topic = data.get("topic")
    user_answer = data.get("answer")
    question = blog_generator.interview_step(topic, user_answer)
    return jsonify({"question": question})

@app.route("/generate", methods=["POST"])
def generate():
    data = blog_generator.generate_blog()
    return jsonify(data)

@app.route("/quick-generate", methods=["POST"])
def quick_generate():
    """Generate detailed, research-backed blog directly without interview - for faster results"""
    try:
        data = request.get_json()
        topic = data.get("topic")
        additional_info = data.get("info", "")
        
        if not topic:
            return jsonify({"error": "Topic is required"}), 400
        
        # Research the topic for accuracy
        print(f"🔍 Quick research for: {topic}")
        research_data = blog_generator.researcher_tool.research_topic(topic)
        
        if not research_data:
            research_data = {"sources": [], "content": f"General information about {topic}"}
        
        # Create enhanced context for quick generation with research data
        context = f"""Create a detailed, expert-level blog post about: {topic}

RESEARCH DATA AVAILABLE:
{research_data.get('content', '')}

REQUIREMENTS:
- Use research data to provide accurate, specific information with facts and statistics
- Write as a subject matter expert with deep knowledge of {topic}
- Provide specific, actionable information rather than generic advice
- Include real-world examples, case studies, or practical scenarios
- Use appropriate industry terminology and concepts
- Make it comprehensive but accessible
- Include step-by-step guidance where applicable
- Add tables, lists, or structured information when relevant
- Ensure all claims are accurate and supportable

Additional user requirements: {additional_info if additional_info else 'None - cover the topic comprehensively with research-backed information'}

Target length: 1000-1200 words with proper structure, formatting, and research-backed accuracy."""
        
        result = blog_generator.blog_crew.kickoff(inputs={
            "topic": topic,
            "context": context
        }, research_data=research_data)
        
        raw_output = result.raw if hasattr(result, "raw") else str(result)
        clean_json = re.sub(r"```json\n|\n```|```", "", raw_output).strip()
        
        # More aggressive JSON cleaning
        start_idx = clean_json.find('{')
        end_idx = clean_json.rfind('}')
        
        if start_idx != -1 and end_idx != -1:
            clean_json = clean_json[start_idx:end_idx+1]
        
        try:
            data = json.loads(clean_json)
            # Ensure all required fields exist
            if not isinstance(data.get('blogContent'), str):
                raise ValueError("Invalid blogContent")
            if not isinstance(data.get('summary'), str):
                data['summary'] = f"A comprehensive, research-backed guide about {topic}"
            if not isinstance(data.get('keywords'), list):
                data['keywords'] = [topic.lower(), "guide", "research", "facts", "expert analysis"]
            
            # Clean up the blog content formatting
            data['blogContent'] = blog_generator.clean_blog_formatting(data['blogContent'])
            
            # DO NOT add source attribution to visible content - keep research internal
                
        except (json.JSONDecodeError, ValueError):
            # Clean fallback without research sources
            cleaned_content = blog_generator.clean_blog_formatting(f"# {topic}\n\n{raw_output}")
            data = {
                "blogContent": cleaned_content,
                "summary": f"A comprehensive, research-backed guide about {topic}",
                "keywords": [topic.lower(), "guide", "research", "facts", "expert analysis"]
            }
        
        print("✅ Quick research-backed blog generated!")
        return jsonify(data)
        
    except Exception as e:
        print(f"❌ Error in quick generate: {str(e)}")
        return jsonify({
            "blogContent": f"# Error\n\nError generating blog: {str(e)}",
            "summary": "Error generating blog",
            "keywords": ["error"]
        }), 500


@app.route("/youtube-generate", methods=["POST"])
def youtube_generate():
    """
    Robust YouTube blog generation endpoint using the new robust function
    Handles all edge cases and always returns a proper response
    """
    try:
        # Get request data
        data = request.json if request.json else {}
        youtube_url = data.get("youtubeUrl", "").strip()
        additional_context = data.get("additionalContext", "").strip()
        
        # Validate input
        if not youtube_url:
            return jsonify({
                "success": False,
                "error": "YouTube URL is required",
                "blogContent": None
            }), 400
        
        print(f"🎥 Processing YouTube video: {youtube_url}")
        
        # Get API keys from existing configuration
        google_search_api_key = "AIzaSyBulaFMZql3n6-mtJnHF55371CYtJu_9R8"  # Using your existing key
        search_engine_ids = [
            "a65b8e8b1cf564e44",
            "91e458efa2c6a4c49", 
            "507e20da4ca5248b6"
        ]
        
        # Call the robust blog generation function
        result = generate_blog_from_youtube(
            video_url=youtube_url,
            additional_context=additional_context,
            gemini_api_key=api_key,  # Use existing configured API key
            google_search_api_key=google_search_api_key,
            search_engine_id=search_engine_ids[0]  # Use first search engine
        )
        
        # Check if generation was successful
        if result['success']:
            # Success case - format response to match existing frontend expectations
            response_data = {
                "success": True,
                "blogContent": result['blog_content'],
                "summary": f"Blog generated from YouTube video: '{result['video_info']['title']}' by {result['video_info']['author']}",
                "keywords": [],  # Extract from metadata if available
                "source": {
                    "type": "YouTube Video",
                    "title": result['video_info']['title'],
                    "author": result['video_info']['author'],
                    "url": youtube_url,
                    "duration": f"{result['video_info']['duration_minutes']} minutes",
                    "views": result['video_info']['views'],
                    "transcript_available": result['generation_info']['transcript_available'],
                    "generation_method": result['generation_info']['method']
                },
                "generation_info": result['generation_info'],
                "metadata": {
                    "generated_at": result['timestamp'],
                    "method": result['generation_info']['method'],
                    "research_sources": result['generation_info'].get('research_sources', 0)
                }
            }
            
            # Save the blog to file (maintaining compatibility with existing code)
            try:
                with open("latest_youtube_blog.md", "w", encoding="utf-8") as f:
                    f.write(f"# {result['video_info']['title']}\n\n")
                    f.write(f"**Source:** YouTube Video by {result['video_info']['author']}\n")
                    f.write(f"**URL:** {youtube_url}\n")
                    f.write(f"**Duration:** {result['video_info']['duration_minutes']} minutes\n")
                    f.write(f"**Generation Method:** {result['generation_info']['method']}\n\n")
                    f.write("---\n\n")
                    f.write(result['blog_content'])
                print("💾 Blog saved to latest_youtube_blog.md")
            except Exception as save_error:
                print(f"⚠️ Warning: Could not save blog to file: {save_error}")
            
            print(f"✅ Blog generated successfully using {result['generation_info']['method']}")
            return jsonify(response_data), 200
            
        else:
            # Error case - but still return structured response
            error_response = {
                "success": False,
                "error": result['error'],
                "blogContent": None,
                "video_info": result.get('video_info', {}),
                "timestamp": result['timestamp']
            }
            
            print(f"❌ Blog generation failed: {result['error']}")
            return jsonify(error_response), 400
    
    except Exception as e:
        # Ultimate fallback for any unexpected errors
        print(f"❌ Unexpected error in YouTube endpoint: {e}")
        return jsonify({
            "success": False,
            "error": f"Server error: {str(e)}",
            "blogContent": None
        }), 500


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 3001))
    print(f"🚀 Starting Flask server on http://localhost:{port}")
    print(f"✅ Using Google AI Studio API with Gemini 2.0 Flash")
    print(f"🤖 Custom CrewAI implementation - fully compatible")
    app.run(port=port, debug=True)