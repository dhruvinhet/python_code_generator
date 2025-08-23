"""
Robust YouTube Blog Generator
Handles transcript fetching, AI blog generation, and error handling
"""

import re
import json
import requests
from urllib.parse import urlparse, parse_qs
import google.generativeai as genai
from youtube_transcript_api import YouTubeTranscriptApi
from pytube import YouTube
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class YouTubeBlogGenerator:
    def __init__(self, gemini_api_key=None, google_search_api_key=None, search_engine_id=None):
        """
        Initialize the YouTube Blog Generator
        
        Args:
            gemini_api_key (str): Google AI Studio API key for Gemini
            google_search_api_key (str): Google Custom Search API key
            search_engine_id (str): Google Custom Search Engine ID
        """
        if gemini_api_key:
            genai.configure(api_key=gemini_api_key)
        
        self.google_search_api_key = google_search_api_key
        self.search_engine_id = search_engine_id
    
    def extract_video_id(self, video_url):
        """
        Extract YouTube video ID from various URL formats
        
        Args:
            video_url (str): YouTube video URL
            
        Returns:
            str: Video ID or None if invalid URL
        """
        try:
            # Handle different YouTube URL formats
            patterns = [
                r'(?:youtube\.com/watch\?v=|youtu\.be/|youtube\.com/embed/)([^&\n?#]+)',
                r'youtube\.com/watch\?.*v=([^&\n?#]+)',
            ]
            
            for pattern in patterns:
                match = re.search(pattern, video_url)
                if match:
                    return match.group(1)
            
            # Try parsing as URL
            parsed_url = urlparse(video_url)
            if 'youtube.com' in parsed_url.netloc:
                query_params = parse_qs(parsed_url.query)
                if 'v' in query_params:
                    return query_params['v'][0]
            elif 'youtu.be' in parsed_url.netloc:
                return parsed_url.path[1:]
            
            return None
            
        except Exception as e:
            logger.error(f"Error extracting video ID: {e}")
            return None
    
    def get_video_metadata(self, video_id):
        """
        Get video metadata with multiple fallback methods
        
        Args:
            video_id (str): YouTube video ID
            
        Returns:
            dict: Video metadata
        """
        metadata = {
            'title': 'Unknown Title',
            'author': 'Unknown Author',
            'description': '',
            'length': 0,
            'views': 0,
            'keywords': [],
            'publish_date': None
        }
        
        try:
            # Try pytube first
            yt = YouTube(f"https://www.youtube.com/watch?v={video_id}")
            metadata.update({
                'title': yt.title or 'Unknown Title',
                'author': yt.author or 'Unknown Author',
                'description': yt.description or '',
                'length': yt.length or 0,
                'views': yt.views or 0,
                'keywords': yt.keywords or [],
                'publish_date': yt.publish_date
            })
            logger.info(f"✅ Pytube metadata retrieved for: {metadata['title']}")
            
        except Exception as e:
            logger.warning(f"⚠️ Pytube failed, trying web scraping: {e}")
            
            try:
                # Fallback: Web scraping
                response = requests.get(f"https://www.youtube.com/watch?v={video_id}", timeout=10)
                html = response.text
                
                # Extract title
                title_match = re.search(r'"title":"([^"]+)"', html)
                if title_match:
                    metadata['title'] = title_match.group(1).replace('\\', '')
                
                # Extract author
                author_match = re.search(r'"author":"([^"]+)"', html)
                if author_match:
                    metadata['author'] = author_match.group(1).replace('\\', '')
                
                # Extract description
                desc_match = re.search(r'"shortDescription":"([^"]+)"', html)
                if desc_match:
                    metadata['description'] = desc_match.group(1).replace('\\', '')[:500]
                
                logger.info(f"✅ Web scraping metadata retrieved for: {metadata['title']}")
                
            except Exception as scrape_error:
                logger.warning(f"⚠️ Web scraping also failed: {scrape_error}")
        
        return metadata
    
    def get_video_transcript(self, video_id):
        """
        Get video transcript with multiple language fallbacks
        
        Args:
            video_id (str): YouTube video ID
            
        Returns:
            dict: Transcript data or None if not available
        """
        try:
            transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
            
            # Try different language options
            language_priorities = ['en', 'en-US', 'en-GB', 'en-CA', 'en-AU']
            transcript_data = None
            transcript_obj = None
            
            # Try manual transcripts first
            for lang in language_priorities:
                try:
                    transcript_obj = transcript_list.find_transcript([lang])
                    transcript_data = transcript_obj.fetch()
                    break
                except:
                    continue
            
            # If no manual transcript, try generated ones
            if not transcript_data:
                try:
                    transcript_obj = transcript_list.find_generated_transcript(['en'])
                    transcript_data = transcript_obj.fetch()
                except:
                    # Get any available transcript
                    transcripts = list(transcript_list)
                    if transcripts:
                        transcript_obj = transcripts[0]
                        transcript_data = transcript_obj.fetch()
            
            if transcript_data:
                # Combine transcript text
                full_text = ' '.join([entry['text'] for entry in transcript_data])
                
                # Clean up the text
                full_text = re.sub(r'\[.*?\]', '', full_text)  # Remove [Music], [Applause], etc.
                full_text = re.sub(r'\s+', ' ', full_text).strip()  # Normalize whitespace
                
                return {
                    'text': full_text,
                    'language': transcript_obj.language_code if transcript_obj else 'unknown',
                    'is_generated': transcript_obj.is_generated if transcript_obj else False,
                    'word_count': len(full_text.split()),
                    'char_count': len(full_text)
                }
            
            return None
            
        except Exception as e:
            logger.warning(f"⚠️ Could not fetch transcript: {e}")
            return None
    
    def search_topic_research(self, query, num_results=3):
        """
        Search for additional research on the topic
        
        Args:
            query (str): Search query
            num_results (int): Number of results to return
            
        Returns:
            list: Search results
        """
        research_data = []
        
        if not self.google_search_api_key or not self.search_engine_id:
            logger.warning("⚠️ Google Search API not configured")
            return research_data
        
        try:
            search_url = "https://www.googleapis.com/customsearch/v1"
            params = {
                'key': self.google_search_api_key,
                'cx': self.search_engine_id,
                'q': query,
                'num': num_results
            }
            
            response = requests.get(search_url, params=params, timeout=10)
            
            if response.status_code == 200:
                search_results = response.json()
                items = search_results.get('items', [])
                
                for item in items:
                    research_data.append({
                        'title': item.get('title', ''),
                        'snippet': item.get('snippet', ''),
                        'link': item.get('link', '')
                    })
                
                logger.info(f"✅ Found {len(research_data)} research sources")
            else:
                logger.warning(f"⚠️ Google Search failed: {response.status_code}")
                
        except Exception as e:
            logger.warning(f"⚠️ Research search failed: {e}")
        
        return research_data
    
    def generate_blog_with_transcript(self, metadata, transcript, additional_context=""):
        """
        Generate blog content when transcript is available
        
        Args:
            metadata (dict): Video metadata
            transcript (dict): Video transcript
            additional_context (str): Additional context from user
            
        Returns:
            dict: Generated blog content
        """
        try:
            duration_text = f"{round(metadata['length'] / 60, 1)} minutes" if metadata['length'] > 0 else "Duration unknown"
            keywords_text = ', '.join(metadata.get('keywords', [])[:10]) if metadata.get('keywords') else "No keywords available"
            
            prompt = f"""
            Create a comprehensive, well-structured blog post based on the following YouTube video content:

            **Video Information:**
            - Title: {metadata['title']}
            - Author/Channel: {metadata['author']}
            - Duration: {duration_text}
            - Keywords: {keywords_text}

            **Video Description:**
            {metadata.get('description', 'No description available')[:500]}

            **Full Video Transcript:**
            {transcript['text']}

            **Additional Context:**
            {additional_context}

            **Instructions:**
            1. Create a compelling blog title that captures the main topic
            2. Write an engaging introduction that hooks the reader
            3. Structure the content with clear headings and subheadings
            4. Extract and expand on the key points from the video
            5. Include relevant examples, insights, and takeaways
            6. Add a strong conclusion with actionable points
            7. Keep the tone professional yet engaging
            8. Aim for 1200-1500 words
            9. Make it SEO-friendly with good keyword usage

            **Format Requirements:**
            - Use markdown formatting with ## for main headings and ### for subheadings
            - Include bullet points where appropriate
            - Make paragraphs well-structured and readable
            - Include a "Key Takeaways" section at the end

            Generate the blog post now:
            """

            model = genai.GenerativeModel('gemini-2.0-flash-exp')
            response = model.generate_content(prompt)
            
            if response and response.text:
                return {
                    'success': True,
                    'blog_content': response.text,
                    'generation_method': 'Transcript + Gemini AI',
                    'source_info': {
                        'transcript_available': True,
                        'transcript_language': transcript['language'],
                        'transcript_word_count': transcript['word_count']
                    }
                }
            else:
                return {
                    'success': False,
                    'error': 'Empty response from AI model'
                }
                
        except Exception as e:
            logger.error(f"❌ Error generating blog with transcript: {e}")
            return {
                'success': False,
                'error': f'AI generation failed: {str(e)}'
            }
    
    def generate_blog_with_research(self, metadata, research_data, additional_context=""):
        """
        Generate blog content when transcript is not available
        
        Args:
            metadata (dict): Video metadata
            research_data (list): Research sources
            additional_context (str): Additional context from user
            
        Returns:
            dict: Generated blog content
        """
        try:
            # Prepare research context
            research_text = ""
            if research_data:
                research_text = "\n\n**Research Sources:**\n"
                for i, source in enumerate(research_data, 1):
                    research_text += f"\n{i}. **{source['title']}**\n"
                    research_text += f"   {source['snippet']}\n"
                    research_text += f"   Source: {source['link']}\n"
            
            duration_text = f"{round(metadata['length'] / 60, 1)} minutes" if metadata['length'] > 0 else "Duration unknown"
            keywords_text = ', '.join(metadata.get('keywords', [])[:10]) if metadata.get('keywords') else "No keywords available"
            
            prompt = f"""
            Create a comprehensive, well-researched blog post about the following YouTube video. Since the video transcript is not available, use the video metadata and research sources to create engaging content.

            **Video Information:**
            - Title: {metadata['title']}
            - Author/Channel: {metadata['author']}
            - Duration: {duration_text}
            - Keywords: {keywords_text}

            **Video Description:**
            {metadata.get('description', 'No description available')[:500]}

            {research_text}

            **Additional Context:**
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
            - Use markdown formatting with ## for main headings and ### for subheadings
            - Include bullet points where appropriate
            - Make paragraphs well-structured and readable
            - Include a "Key Takeaways" section
            - Add a reference to the original video

            Generate the comprehensive blog post now:
            """

            model = genai.GenerativeModel('gemini-2.0-flash-exp')
            response = model.generate_content(prompt)
            
            if response and response.text:
                return {
                    'success': True,
                    'blog_content': response.text,
                    'generation_method': 'Research + Gemini AI',
                    'source_info': {
                        'transcript_available': False,
                        'research_sources_count': len(research_data)
                    }
                }
            else:
                return {
                    'success': False,
                    'error': 'Empty response from AI model'
                }
                
        except Exception as e:
            logger.error(f"❌ Error generating blog with research: {e}")
            return {
                'success': False,
                'error': f'AI generation failed: {str(e)}'
            }

def generate_blog_from_youtube(video_url, additional_context="", gemini_api_key=None, google_search_api_key=None, search_engine_id=None):
    """
    Robust function to generate blog from YouTube video
    
    Args:
        video_url (str): YouTube video URL
        additional_context (str): Additional context for blog generation
        gemini_api_key (str): Google AI Studio API key
        google_search_api_key (str): Google Custom Search API key
        search_engine_id (str): Google Custom Search Engine ID
    
    Returns:
        dict: Structured JSON response with blog content or error
    """
    
    # Initialize result structure - ALWAYS initialize variables
    result = {
        'success': False,
        'error': None,
        'blog_content': None,
        'video_info': {},
        'generation_info': {},
        'timestamp': None
    }
    
    blog_generator = None
    video_id = None
    metadata = {}
    transcript = None
    research_data = []
    blog_result = None  # Initialize blog_result to avoid UnboundLocalError
    
    try:
        # Import datetime here to avoid issues
        from datetime import datetime
        result['timestamp'] = datetime.now().isoformat()
        
        # Validate input
        if not video_url or not video_url.strip():
            result['error'] = "YouTube URL is required"
            return result
        
        # Initialize the blog generator
        blog_generator = YouTubeBlogGenerator(
            gemini_api_key=gemini_api_key,
            google_search_api_key=google_search_api_key,
            search_engine_id=search_engine_id
        )
        
        logger.info(f"🎥 Processing YouTube video: {video_url}")
        
        # Step 1: Extract video ID
        video_id = blog_generator.extract_video_id(video_url)
        if not video_id:
            result['error'] = "Invalid YouTube URL format"
            return result
        
        logger.info(f"📺 Video ID extracted: {video_id}")
        
        # Step 2: Get video metadata
        metadata = blog_generator.get_video_metadata(video_id)
        result['video_info'] = {
            'video_id': video_id,
            'title': metadata['title'],
            'author': metadata['author'],
            'duration_minutes': round(metadata['length'] / 60, 1) if metadata['length'] > 0 else 0,
            'views': metadata.get('views', 0),
            'url': video_url
        }
        
        logger.info(f"📝 Video metadata retrieved: {metadata['title']}")
        
        # Step 3: Try to get transcript
        transcript = blog_generator.get_video_transcript(video_id)
        
        # Step 4: Generate blog content
        if transcript and transcript.get('text'):
            # Method 1: Use transcript
            logger.info(f"📄 Transcript available ({transcript['word_count']} words) - using transcript method")
            blog_result = blog_generator.generate_blog_with_transcript(metadata, transcript, additional_context)
            
        else:
            # Method 2: Use research-based approach
            logger.info("⚠️ No transcript available - using research method")
            
            # Generate search queries for research
            search_queries = [metadata['title']]
            if metadata.get('keywords'):
                search_queries.append(' '.join(metadata['keywords'][:3]))
            
            # Perform research
            for query in search_queries[:2]:  # Limit to 2 searches
                query_research = blog_generator.search_topic_research(query, num_results=3)
                research_data.extend(query_research)
            
            # Remove duplicates
            seen_links = set()
            unique_research = []
            for item in research_data:
                if item['link'] not in seen_links:
                    unique_research.append(item)
                    seen_links.add(item['link'])
            research_data = unique_research[:5]  # Limit to 5 sources
            
            blog_result = blog_generator.generate_blog_with_research(metadata, research_data, additional_context)
        
        # Step 5: Process results
        if blog_result and blog_result.get('success'):
            result.update({
                'success': True,
                'blog_content': blog_result['blog_content'],
                'generation_info': {
                    'method': blog_result['generation_method'],
                    'transcript_available': transcript is not None,
                    'research_sources': len(research_data) if research_data else 0,
                    **blog_result.get('source_info', {})
                }
            })
            
            logger.info(f"✅ Blog generated successfully using {blog_result['generation_method']}")
            
        else:
            error_msg = blog_result.get('error', 'Unknown error in blog generation') if blog_result else 'Blog generation returned no result'
            result['error'] = f"Failed to generate blog: {error_msg}"
            logger.error(f"❌ Blog generation failed: {error_msg}")
    
    except Exception as e:
        result['error'] = f"Unexpected error: {str(e)}"
        logger.error(f"❌ Unexpected error in generate_blog_from_youtube: {e}")
    
    finally:
        # Ensure we always return a properly structured result
        if not result.get('success') and not result.get('error'):
            result['error'] = "Unknown error occurred during processing"
    
    return result