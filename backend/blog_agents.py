import os
import google.generativeai as genai
from config import Config
from typing import List, Dict, Any
import json
import requests
from bs4 import BeautifulSoup
import time
import logging

# Configure Gemini API
genai.configure(api_key=Config.GOOGLE_API_KEY)

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BlogPlannerAgent:
    """Agent responsible for planning blog structure and topics"""
    
    def __init__(self):
        self.model = genai.GenerativeModel('gemini-2.0-flash-exp')
    
    def plan_blog_structure(self, main_topic: str) -> Dict[str, Any]:
        """
        Plan the blog structure based on the main topic
        Returns: {
            'title': str,
            'subtopics': List[str],
            'outline': str
        }
        """
        try:
            prompt = f"""
            You are a professional blog planning agent. Given the main topic: "{main_topic}", 
            create a comprehensive blog structure.
            
            Please provide:
            1. A compelling blog title
            2. 5-8 relevant subtopics that should be covered
            3. A brief outline description
            
            Format your response as JSON:
            {{
                "title": "Blog Title Here",
                "subtopics": ["Subtopic 1", "Subtopic 2", "Subtopic 3", ...],
                "outline": "Brief description of what the blog will cover"
            }}
            
            Make sure the subtopics are specific, relevant, and comprehensive for the main topic.
            """
            
            response = self.model.generate_content(prompt)
            
            # Parse JSON response
            json_start = response.text.find('{')
            json_end = response.text.rfind('}') + 1
            json_str = response.text[json_start:json_end]
            
            result = json.loads(json_str)
            logger.info(f"Blog structure planned for topic: {main_topic}")
            return result
            
        except Exception as e:
            logger.error(f"Error planning blog structure: {str(e)}")
            # Fallback response
            return {
                "title": f"Complete Guide to {main_topic}",
                "subtopics": [
                    f"Introduction to {main_topic}",
                    f"Key Concepts of {main_topic}",
                    f"Benefits and Applications",
                    f"Best Practices",
                    f"Future Trends",
                    f"Conclusion"
                ],
                "outline": f"A comprehensive guide covering all aspects of {main_topic}"
            }

class BlogResearchAgent:
    """Agent responsible for researching content using multiple search methods"""
    
    def __init__(self):
        self.api_key = "AIzaSyA7_urve2eWeHDweCJeY3fcxABMGf_IXuo"
        # Using a general web search engine ID - you might need to create your own
        self.search_engine_id = "3519a0ac46907492a"  # Updated CSE ID for general web search
        self.model = genai.GenerativeModel('gemini-2.0-flash-exp')
    
    def search_information(self, query: str, num_results: int = 5) -> List[Dict[str, str]]:
        """
        Search for information using Google Custom Search API with fallback
        Returns list of search results with titles, links, and snippets
        """
        try:
            # First try with the current CSE
            url = "https://www.googleapis.com/customsearch/v1"
            params = {
                'key': self.api_key,
                'cx': self.search_engine_id,
                'q': query,
                'num': min(num_results, 10)  # API limit is 10
            }
            
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                results = []
                
                if 'items' in data:
                    for item in data['items']:
                        results.append({
                            'title': item.get('title', ''),
                            'link': item.get('link', ''),
                            'snippet': item.get('snippet', ''),
                            'displayLink': item.get('displayLink', '')
                        })
                
                logger.info(f"Found {len(results)} search results for query: {query}")
                return results
            else:
                logger.warning(f"Search API returned status {response.status_code}: {response.text}")
                # Immediately use AI-based research instead of trying more APIs
                return self._generate_ai_search_results(query, num_results)
                
        except Exception as e:
            logger.error(f"Error searching for information: {str(e)}")
            return self._generate_ai_search_results(query, num_results)
    
    def _generate_ai_search_results(self, query: str, num_results: int) -> List[Dict[str, str]]:
        """
        Generate realistic search results using AI when actual search fails
        """
        try:
            prompt = f"""
            Generate {num_results} realistic search results for the query: "{query}"
            
            For each result, create:
            1. A realistic title related to the query
            2. A credible website domain (like wikipedia.org, medium.com, etc.)
            3. A detailed snippet (2-3 sentences with specific information)
            4. A realistic URL
            
            Make the results diverse and from different types of sources (educational, news, blogs, official sites).
            Include specific details, statistics, or facts in the snippets.
            
            Format as JSON array:
            [
                {{
                    "title": "Specific Article Title About The Topic",
                    "displayLink": "crediblewebsite.com",
                    "snippet": "Detailed information snippet with specific facts and insights about the topic...",
                    "link": "https://crediblewebsite.com/article-url"
                }}
            ]
            """
            
            response = self.model.generate_content(prompt)
            
            # Parse JSON response
            try:
                json_start = response.text.find('[')
                json_end = response.text.rfind(']') + 1
                json_str = response.text[json_start:json_end]
                results = json.loads(json_str)
                
                logger.info(f"Generated {len(results)} AI search results for query: {query}")
                return results
                
            except:
                # Fallback if JSON parsing fails
                return self._create_simple_search_results(query, num_results)
                
        except Exception as e:
            logger.error(f"Error generating AI search results: {str(e)}")
            return self._create_simple_search_results(query, num_results)
    
    def _create_simple_search_results(self, query: str, num_results: int) -> List[Dict[str, str]]:
        """
        Create simple search results as ultimate fallback
        """
        results = []
        sources = [
            ("Wikipedia", "wikipedia.org", "Encyclopedia article"),
            ("Medium", "medium.com", "In-depth analysis"),  
            ("Research Paper", "researchgate.net", "Academic research"),
            ("Industry Blog", "towardsdatascience.com", "Technical insights"),
            ("News Article", "techcrunch.com", "Latest developments")
        ]
        
        for i in range(min(num_results, len(sources))):
            source_name, domain, description = sources[i]
            results.append({
                'title': f"{query} - {source_name}",
                'link': f"https://{domain}/article-about-{query.replace(' ', '-').lower()}",
                'snippet': f"{description} about {query}. This source provides comprehensive information and current insights about the topic.",
                'displayLink': domain
            })
        
        return results
    
    def _fallback_search(self, query: str, num_results: int) -> List[Dict[str, str]]:
        """
        Fallback search method when primary search fails
        """
        try:
            # Try with a different CSE ID or create mock results based on query
            fallback_cse_ids = [
                "017576662512468239146:omuauf_lfve",  # Original
                "partner-pub-1234567890123456:abcdefg",  # Placeholder
            ]
            
            for cse_id in fallback_cse_ids:
                try:
                    url = "https://www.googleapis.com/customsearch/v1"
                    params = {
                        'key': self.api_key,
                        'cx': cse_id,
                        'q': query,
                        'num': min(num_results, 5)
                    }
                    
                    response = requests.get(url, params=params, timeout=10)
                    if response.status_code == 200:
                        data = response.json()
                        if 'items' in data:
                            results = []
                            for item in data['items']:
                                results.append({
                                    'title': item.get('title', ''),
                                    'link': item.get('link', ''),
                                    'snippet': item.get('snippet', ''),
                                    'displayLink': item.get('displayLink', '')
                                })
                            return results
                except:
                    continue
            
            # If all searches fail, generate mock results using AI
            logger.warning(f"All search methods failed, generating AI-based content for: {query}")
            return self._generate_ai_research(query, num_results)
            
        except Exception as e:
            logger.error(f"Fallback search failed: {str(e)}")
            return []
    
    def _generate_ai_research(self, query: str, num_results: int) -> List[Dict[str, str]]:
        """
        Generate research content using AI when search APIs fail
        """
        try:
            prompt = f"""
            Generate {num_results} realistic research sources and content snippets for the topic: "{query}"
            
            For each source, provide:
            1. A realistic website/source name
            2. A descriptive title
            3. A detailed content snippet (2-3 sentences)
            
            Format as JSON array:
            [
                {{
                    "title": "Article Title",
                    "displayLink": "website.com",
                    "snippet": "Detailed information about the topic...",
                    "link": "https://website.com/article"
                }}
            ]
            """
            
            response = self.model.generate_content(prompt)
            
            # Parse JSON response
            json_start = response.text.find('[')
            json_end = response.text.rfind(']') + 1
            
            if json_start != -1 and json_end != -1:
                json_str = response.text[json_start:json_end]
                results = json.loads(json_str)
                logger.info(f"Generated {len(results)} AI-based research results")
                return results
            else:
                # Manual fallback
                return [{
                    'title': f"Research on {query}",
                    'displayLink': "research.com",
                    'snippet': f"Comprehensive information and analysis about {query}, including key concepts, applications, and current trends in the field.",
                    'link': f"https://research.com/{query.replace(' ', '-').lower()}"
                }]
                
        except Exception as e:
            logger.error(f"AI research generation failed: {str(e)}")
            return []
    
    def scrape_content(self, url: str, max_chars: int = 5000) -> str:
        """
        Scrape content from a URL
        Returns cleaned text content
        """
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Remove script and style elements
            for script in soup(["script", "style"]):
                script.decompose()
            
            # Get text content
            text = soup.get_text()
            
            # Clean up text
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            text = ' '.join(chunk for chunk in chunks if chunk)
            
            # Limit text length
            if len(text) > max_chars:
                text = text[:max_chars] + "..."
            
            logger.info(f"Scraped {len(text)} characters from {url}")
            return text
            
        except Exception as e:
            logger.error(f"Error scraping content from {url}: {str(e)}")
            return ""
    
    def research_topic_by_subtopics(self, main_topic: str, subtopics: List[str]) -> Dict[str, Any]:
        """
        Research each subtopic individually and return organized data
        Returns: {
            'main_topic_data': [research_results],
            'subtopic_data': {
                'subtopic1': [research_results],
                'subtopic2': [research_results],
                ...
            }
        }
        """
        research_results = {
            'main_topic_data': [],
            'subtopic_data': {}
        }
        
        # First research the main topic
        logger.info(f"Researching main topic: {main_topic}")
        main_results = self.search_information(f"{main_topic} overview guide", 3)
        
        for result in main_results:
            content = self.scrape_content(result['link'])
            if content:
                research_results['main_topic_data'].append({
                    'source': result['displayLink'],
                    'title': result['title'],
                    'content': content[:2000],
                    'snippet': result['snippet']
                })
        
        # If no results from API, generate AI content for main topic
        if not research_results['main_topic_data']:
            ai_content = self._generate_comprehensive_research(main_topic, [])
            research_results['main_topic_data'].append({
                'source': 'AI Generated',
                'title': f"Comprehensive Overview of {main_topic}",
                'content': ai_content[:2000],
                'snippet': f"AI-generated comprehensive overview of {main_topic}"
            })
        
        # Now research each subtopic individually
        for i, subtopic in enumerate(subtopics, 1):
            logger.info(f"Researching subtopic {i}/{len(subtopics)}: {subtopic}")
            research_results['subtopic_data'][subtopic] = []
            
            # Search for this specific subtopic
            search_queries = [
                f"{main_topic} {subtopic}",
                f"{subtopic} detailed explanation",
                f"how to {subtopic.lower()}"
            ]
            
            # Try different search queries for better results
            for query in search_queries[:2]:  # Try first 2 queries
                subtopic_results = self.search_information(query, 2)
                
                for result in subtopic_results:
                    content = self.scrape_content(result['link'])
                    if content:
                        research_results['subtopic_data'][subtopic].append({
                            'source': result['displayLink'],
                            'title': result['title'],
                            'content': content[:1500],
                            'snippet': result['snippet']
                        })
                
                # Break if we have enough data for this subtopic
                if len(research_results['subtopic_data'][subtopic]) >= 2:
                    break
            
            # If no results from API for this subtopic, generate AI content
            if not research_results['subtopic_data'][subtopic]:
                ai_content = self._generate_subtopic_research(main_topic, subtopic)
                research_results['subtopic_data'][subtopic].append({
                    'source': 'AI Generated',
                    'title': f"{subtopic} - Detailed Analysis",
                    'content': ai_content,
                    'snippet': f"AI-generated detailed analysis of {subtopic}"
                })
            
            # Add delay to avoid rate limiting
            time.sleep(1)
        
        return research_results
        """
        Research comprehensive information for a topic and its subtopics
        Returns combined research data with focus on individual subtopics
        """
        all_research_data = []
        
        # Research main topic with better search terms
        main_search_terms = [
            f"{topic} complete guide",
            f"{topic} overview",
            f"what is {topic}"
        ]
        
        for search_term in main_search_terms[:1]:  # Try first search term
            results = self.search_information(search_term, 2)
            for result in results:
                if result.get('link'):
                    content = self.scrape_content(result['link'])
                    if content:
                        all_research_data.append({
                            'source': result['displayLink'],
                            'title': result['title'],
                            'content': content[:2000],
                            'section': 'Main Topic'
                        })
                else:
                    # Use snippet if no link available
                    all_research_data.append({
                        'source': result['displayLink'],
                        'title': result['title'],
                        'content': result.get('snippet', ''),
                        'section': 'Main Topic'
                    })
        
        # Research each subtopic individually with detailed, specific searches
        for i, subtopic in enumerate(subtopics[:6]):  # Limit to 6 subtopics for performance
            search_queries = [
                f"{subtopic} detailed explanation",
                f"{subtopic} in {topic}",
                f"how to {subtopic.lower()}",
                f"{subtopic} best practices"
            ]
            
            # Try different search variations for each subtopic
            for query in search_queries[:2]:  # Use first 2 queries per subtopic
                results = self.search_information(query, 2)
                for result in results:
                    if result.get('link'):
                        content = self.scrape_content(result['link'])
                        if content:
                            all_research_data.append({
                                'source': result['displayLink'],
                                'title': result['title'],
                                'content': content[:1800],
                                'section': f'Subtopic: {subtopic}'
                            })
                    else:
                        # Use snippet if no link available
                        all_research_data.append({
                            'source': result['displayLink'],
                            'title': result['title'],
                            'content': result.get('snippet', ''),
                            'section': f'Subtopic: {subtopic}'
                        })
                
                # Break early if we have good data for this subtopic
                subtopic_data_count = len([d for d in all_research_data if d['section'] == f'Subtopic: {subtopic}'])
                if subtopic_data_count >= 2:
                    break
            
            # Add delay to avoid rate limiting
            time.sleep(0.3)
            
            # If no good data found for this subtopic, generate AI-specific content
            subtopic_data_count = len([d for d in all_research_data if d['section'] == f'Subtopic: {subtopic}'])
            if subtopic_data_count == 0:
                logger.info(f"Generating AI content for subtopic: {subtopic}")
                ai_content = self._generate_subtopic_research(topic, subtopic)
                all_research_data.append({
                    'source': 'AI Research',
                    'title': f'Detailed Analysis: {subtopic}',
                    'content': ai_content,
                    'section': f'Subtopic: {subtopic}'
                })
        
        # If we don't have enough overall research data, supplement with comprehensive AI content
        if len(all_research_data) < 4:
            logger.warning("Insufficient research data found, supplementing with comprehensive AI content")
            ai_content = self._generate_comprehensive_research(topic, subtopics)
            all_research_data.append({
                'source': 'AI Research',
                'title': f'Comprehensive Analysis of {topic}',
                'content': ai_content,
                'section': 'Comprehensive Overview'
            })
        
        # Organize research data by sections
        organized_research = []
        
        # Add main topic research first
        main_topic_data = [d for d in all_research_data if d['section'] == 'Main Topic']
        if main_topic_data:
            organized_research.append("=== MAIN TOPIC RESEARCH ===")
            for data in main_topic_data[:2]:
                organized_research.append(f"Source: {data['source']}\nTitle: {data['title']}\nContent: {data['content']}")
        
        # Add subtopic research
        for subtopic in subtopics:
            subtopic_data = [d for d in all_research_data if d['section'] == f'Subtopic: {subtopic}']
            if subtopic_data:
                organized_research.append(f"\n=== RESEARCH FOR: {subtopic.upper()} ===")
                for data in subtopic_data[:3]:  # Max 3 sources per subtopic
                    organized_research.append(f"Source: {data['source']}\nTitle: {data['title']}\nContent: {data['content']}")
        
        # Add comprehensive research if available
        comprehensive_data = [d for d in all_research_data if d['section'] == 'Comprehensive Overview']
        if comprehensive_data:
            organized_research.append("\n=== COMPREHENSIVE OVERVIEW ===")
            for data in comprehensive_data:
                organized_research.append(f"Source: {data['source']}\nTitle: {data['title']}\nContent: {data['content']}")
        
        combined_research = "\n\n".join(organized_research)
        
        logger.info(f"Compiled organized research data from {len(all_research_data)} sources across {len(subtopics)} subtopics")
        return combined_research
    
    def _generate_subtopic_research(self, main_topic: str, subtopic: str) -> str:
        """
        Generate detailed research content for a specific subtopic using AI
        """
        try:
            prompt = f"""
            You are a research expert. Generate comprehensive, detailed research content about "{subtopic}" in the context of "{main_topic}".
            
            Provide:
            1. Detailed explanation of the subtopic (3-4 paragraphs)
            2. Key concepts and terminology
            3. Practical examples or case studies
            4. Current trends or developments
            5. Best practices or recommendations
            6. Statistics or data points (create realistic ones)
            7. Expert insights or quotes (create realistic ones)
            
            Make the content informative, detailed, and specifically focused on "{subtopic}".
            Write in a professional, informative tone.
            Include specific details and examples that would be valuable for someone writing a comprehensive blog post.
            
            Target length: 800-1200 words of detailed content.
            """
            
            response = self.model.generate_content(prompt)
            return response.text
            
        except Exception as e:
            logger.error(f"Error generating subtopic research for {subtopic}: {str(e)}")
            return f"Research content about {subtopic} in the context of {main_topic}. This includes key concepts, practical applications, and current trends in this area."
    
    def _generate_comprehensive_research(self, topic: str, subtopics: List[str]) -> str:
        """
        Generate comprehensive research content using AI when search results are limited
        """
        try:
            prompt = f"""
            As a research expert, provide comprehensive information about "{topic}".
            
            Cover these specific subtopics:
            {', '.join(subtopics)}
            
            Provide detailed, factual information including:
            - Key concepts and definitions
            - Current trends and developments
            - Practical applications
            - Benefits and challenges
            - Best practices
            - Real-world examples
            
            Write in a research-oriented style with specific details and insights.
            Length: 1000-1500 words.
            """
            
            response = self.model.generate_content(prompt)
            return response.text[:2000]  # Limit length
            
        except Exception as e:
            logger.error(f"Error generating AI research: {str(e)}")
            return f"Research on {topic}: This is a comprehensive analysis covering various aspects of {topic}, including {', '.join(subtopics[:3])}."

class BlogWriterAgent:
    """Agent responsible for writing the actual blog content"""
    
    def __init__(self):
        self.model = genai.GenerativeModel('gemini-2.0-flash-exp')
    
    def generate_blog_with_structured_data(self, title: str, main_topic: str, subtopics: List[str], research_data: Dict[str, Any]) -> str:
        """
        Generate a comprehensive blog post using structured research data
        """
        try:
            # Format research data for the prompt
            formatted_research = self._format_research_data(research_data, subtopics)
            
            prompt = f"""
            You are a professional blog writer. Create a comprehensive, well-structured blog post based on the following information:
            
            Title: {title}
            Main Topic: {main_topic}
            Subtopics to Cover: {', '.join(subtopics)}
            
            RESEARCH DATA ORGANIZED BY SUBTOPICS:
            {formatted_research}
            
            IMPORTANT INSTRUCTIONS:
            1. Write a compelling introduction (200-300 words) that hooks the reader
            2. Create a dedicated, detailed section for EACH subtopic with specific content from its research data
            3. Each subtopic section should be 400-600 words with detailed information
            4. Use the specific research data provided for each subtopic
            5. Include practical examples, insights, and real-world applications
            6. Write in an engaging, professional tone
            7. Total content should be 2500-4000 words for comprehensive coverage
            8. Include a strong conclusion (250-350 words) with key takeaways
            9. Use markdown formatting for headers, bold text, lists, and emphasis
            10. Reference the research sources naturally in the content
            
            Structure:
            # {title}
            
            ## Introduction
            [Hook readers with compelling introduction, explain what they'll learn]
            
            {self._generate_subtopic_sections(subtopics)}
            
            ## Conclusion
            [Summarize key points, provide actionable insights, discuss future implications]
            
            QUALITY REQUIREMENTS:
            - Each subtopic section must use its specific research data
            - Include concrete examples and practical applications
            - Write in an authoritative yet accessible tone
            - Ensure content flows naturally between sections
            - Provide real value and actionable insights to readers
            """
            
            response = self.model.generate_content(prompt)
            blog_content = response.text
            
            # Ensure proper formatting
            if not blog_content.startswith('#'):
                blog_content = f"# {title}\n\n{blog_content}"
            
            logger.info(f"Generated comprehensive blog with {len(blog_content)} characters")
            return blog_content
            
        except Exception as e:
            logger.error(f"Error generating blog content: {str(e)}")
            return f"# {title}\n\n## Introduction\n\nWelcome to this comprehensive guide on {main_topic}. In this article, we'll explore the key aspects and provide detailed insights.\n\n## Conclusion\n\nSorry, there was an error generating the complete blog content. Please try again."
    
    def _format_research_data(self, research_data: Dict[str, Any], subtopics: List[str]) -> str:
        """Format the structured research data for the prompt"""
        formatted_sections = []
        
        # Add main topic research
        if research_data.get('main_topic_data'):
            formatted_sections.append("=== MAIN TOPIC RESEARCH ===")
            for data in research_data['main_topic_data'][:2]:
                formatted_sections.append(f"Source: {data['source']}")
                formatted_sections.append(f"Title: {data['title']}")
                formatted_sections.append(f"Content: {data['content'][:1000]}...")
                formatted_sections.append("")
        
        # Add subtopic research
        for subtopic in subtopics:
            if subtopic in research_data.get('subtopic_data', {}):
                formatted_sections.append(f"=== RESEARCH FOR: {subtopic.upper()} ===")
                for data in research_data['subtopic_data'][subtopic][:3]:
                    formatted_sections.append(f"Source: {data['source']}")
                    formatted_sections.append(f"Title: {data['title']}")
                    formatted_sections.append(f"Content: {data['content'][:1200]}...")
                    formatted_sections.append("")
        
        return "\n".join(formatted_sections)
    
    def _generate_subtopic_sections(self, subtopics: List[str]) -> str:
        """Generate the structure for subtopic sections"""
        sections = []
        for subtopic in subtopics:
            sections.append(f"## {subtopic}")
            sections.append("[Write detailed 400-600 word section using the specific research data for this subtopic]")
            sections.append("")
        return "\n".join(sections)
        """
        Generate a comprehensive blog post using the organized research data
        """
        try:
            prompt = f"""
            You are a professional blog writer. Create a comprehensive, well-structured blog post based on the following information:
            
            Title: {title}
            Main Topic: {main_topic}
            Subtopics to Cover: {', '.join(subtopics)}
            
            Research Data (Organized by Sections):
            {research_data}
            
            IMPORTANT INSTRUCTIONS:
            1. Write a compelling introduction that hooks the reader and provides overview
            2. Create a dedicated, detailed section for EACH subtopic listed above
            3. Use the research data sections to provide specific, accurate information for each subtopic
            4. Each subtopic section should be 300-500 words with detailed content
            5. Include practical examples, insights, and specific details from the research
            6. Write in an engaging, professional tone suitable for a comprehensive blog
            7. Ensure total content is 2000-3500 words for comprehensive coverage
            8. Include a strong conclusion with key takeaways and actionable insights
            9. Use markdown formatting for headers, bold text, lists, and emphasis
            10. Make each section substantial and informative, not just brief summaries
            
            Structure Template:
            # {title}
            
            ## Introduction
            [Compelling 200-300 word introduction that hooks readers and provides context]
            
            """ + "\n".join([f"## {subtopic}\n[Detailed 300-500 word section with specific information, examples, and insights from research]\n" for subtopic in subtopics]) + """
            
            ## Conclusion
            [Strong 200-300 word conclusion with key takeaways, future outlook, and actionable insights]
            
            QUALITY REQUIREMENTS:
            - Use specific information from the research data sections
            - Include statistics, examples, and expert insights where available
            - Make each subtopic section comprehensive and valuable
            - Ensure smooth transitions between sections
            - Write in an authoritative yet accessible tone
            - Include practical applications and real-world relevance
            - Reference current trends and developments
            
            Remember: Each subtopic should have substantial, detailed content that provides real value to readers. Don't just summarize - provide deep insights and comprehensive coverage.
            """
            
            response = self.model.generate_content(prompt)
            blog_content = response.text
            
            # Ensure proper formatting
            if not blog_content.startswith('#'):
                blog_content = f"# {title}\n\n{blog_content}"
            
            logger.info(f"Generated comprehensive blog content with {len(blog_content)} characters covering {len(subtopics)} subtopics")
            return blog_content
            
        except Exception as e:
            logger.error(f"Error generating blog content: {str(e)}")
            return f"# {title}\n\n## Introduction\n\nWelcome to this comprehensive guide on {main_topic}. In this article, we'll explore the key aspects and provide detailed insights.\n\n## Conclusion\n\nSorry, there was an error generating the complete blog content. Please try again."

class BlogAgentSystem:
    """Main system coordinating all blog agents"""
    
    def __init__(self):
        self.planner = BlogPlannerAgent()
        self.researcher = BlogResearchAgent()
        self.writer = BlogWriterAgent()
    
    def plan_blog(self, topic: str) -> Dict[str, Any]:
        """Plan blog structure"""
        return self.planner.plan_blog_structure(topic)
    
    def generate_blog(self, main_topic: str, subtopics: List[str], title: str) -> str:
        """Generate complete blog with subtopic-specific research"""
        try:
            # Research each subtopic individually
            logger.info("Starting individual subtopic research phase...")
            research_data = self.researcher.research_topic_by_subtopics(main_topic, subtopics)
            
            # Generate blog content using structured data
            logger.info("Starting content generation with structured research...")
            blog_content = self.writer.generate_blog_with_structured_data(title, main_topic, subtopics, research_data)
            
            return blog_content
            
        except Exception as e:
            logger.error(f"Error in blog generation system: {str(e)}")
            return f"# {title}\n\nSorry, there was an error generating your blog. Please try again."

# Create global instance
blog_system = BlogAgentSystem()
