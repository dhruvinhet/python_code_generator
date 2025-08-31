import os
import json
import re
import requests
from bs4 import BeautifulSoup
from urllib.parse import quote_plus, urlparse
from flask import Flask, request, jsonify, session
from flask_cors import CORS
from dotenv import load_dotenv
import google.generativeai as genai

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
    def __init__(self, detailed=True):
        # Initialize research system for accuracy
        self.researcher_tool = AccuracyResearcher()
        self.detailed = detailed
        
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
            description=self._get_writer_prompt(),
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

    def _get_writer_prompt(self):
        """Get the appropriate writer prompt based on detailed flag"""
        if self.detailed:
            return """Using the comprehensive research about "{topic}":
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

Make this read like a feature article that would engage and inspire readers, not like a resume or academic paper."""
        else:
            return """Using ONLY the research data provided about "{topic}":
{context}
{previous_results}

Write a concise, factual 600-800 word blog post about "{topic}" that sticks STRICTLY to the available research data. DO NOT add any information, speculation, or "extra masala" that is not explicitly supported by the research sources.

**TITLE**: Create a clear, descriptive title

**INTRODUCTION** (80-100 words):
- Briefly introduce the topic based on research data
- State what the blog will cover from the available information

**MAIN CONTENT** (3-4 sections, 100-150 words each):
Focus ONLY on verified information from research sources:

1. **Key Facts & Background**:
   - Report only factual information found in research
   - Include specific dates, names, and verifiable details
   - Avoid any speculation or assumptions

2. **Important Details & Achievements**:
   - List concrete achievements and milestones from research
   - Include measurable impacts and statistics if available
   - Stick to documented information only

3. **Current Status & Impact**:
   - Report current situation based on research data
   - Include any documented impacts or contributions
   - Avoid future predictions or speculations

**CONCLUSION** (50-80 words):
- Summarize only the verified information covered
- End with key takeaways from the research data

CRITICAL REQUIREMENTS:
- Use ONLY information from the provided research data
- DO NOT add creative content, speculation, or "extra masala"
- If research data is limited, keep the blog correspondingly brief
- Include specific facts, dates, and verifiable details
- Maintain factual, journalistic tone
- Length: 600-800 words maximum
- Focus on accuracy over engagement

This should read like a factual summary, not a creative feature article."""

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

            # Step 3: Recreate write_task with correct prompt based on detailed flag
            self.write_task = Task(
                description=self._get_writer_prompt(),
                expected_output="An engaging, well-structured blog post with narrative flow and specific details",
                agent=self.writer
            )
            
            # Recreate the crew with updated task
            self.blog_crew = Crew(
                agents=[self.researcher, self.writer, self.stylist],
                tasks=[self.research_task, self.write_task, self.style_task],
                process=Process.sequential,
                memory=False
            )

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


@app.route("/quick-generate", methods=["POST"])
def quick_generate():
    """Generate detailed, research-backed blog directly without interview - for faster results"""
    try:
        data = request.get_json()
        topic = data.get("topic")
        additional_info = data.get("info", "")
        detailed = data.get("detailed", True)  # Default to True for backward compatibility
        
        if not topic:
            return jsonify({"error": "Topic is required"}), 400
        
        # Create generator instance with detailed flag
        generator = InterviewBlogGenerator(detailed=detailed)
        
        # Research the topic for accuracy
        print(f"🔍 Quick research for: {topic}")
        research_data = generator.researcher_tool.research_topic(topic)
        
        if not research_data:
            research_data = {"sources": [], "content": f"General information about {topic}"}
        
        # Create enhanced context for quick generation with research data
        if detailed:
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
        else:
            context = f"""Create a concise, factual blog post about: {topic}

RESEARCH DATA AVAILABLE:
{research_data.get('content', '')}

REQUIREMENTS:
- Use ONLY the research data provided - DO NOT add any information not in the research
- Stick strictly to facts, dates, and verifiable information from the sources
- Write in a journalistic, factual tone without creative embellishment
- Keep it concise and focused on the available data
- Include specific facts, statistics, and details from research sources
- Avoid speculation, predictions, or "extra masala"
- If research data is limited, keep the blog correspondingly brief

Additional user requirements: {additional_info if additional_info else 'None - stick to research data only'}

Target length: 600-800 words maximum, focused on facts from research data."""
        
        result = generator.blog_crew.kickoff(inputs={
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
            data['blogContent'] = generator.clean_blog_formatting(data['blogContent'])
            
            # DO NOT add source attribution to visible content - keep research internal
                
        except (json.JSONDecodeError, ValueError):
            # Clean fallback without research sources
            cleaned_content = generator.clean_blog_formatting(f"# {topic}\n\n{raw_output}")
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
        detailed = data.get("detailed", True)  # Default to True for backward compatibility
        
        # Validate input
        if not youtube_url:
            return jsonify({
                "success": False,
                "error": "YouTube URL is required",
                "blogContent": None
            }), 400
        
        print(f"🎥 Processing YouTube video: {youtube_url} (Detailed: {detailed})")
        
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
            search_engine_id=search_engine_ids[0],  # Use first search engine
            detailed=detailed
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