import time
import json
import google.generativeai as genai
from crewai import Agent, Task, Crew, Process
from config import Config
from .scraper import google_search, scrape_webpage
import logging
import os
# Configure logging
logger = logging.getLogger(__name__)

# Configure Gemini API
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# Generation settings will be applied when creating the model
DEFAULT_GENERATION_CONFIG = {
    "temperature": 0.7,
    "top_p": 0.8,
    "top_k": 40,
    "max_output_tokens": 8192,
}

def retry_with_backoff(func, max_retries=None, delay=None, backoff=None):
    """
    Retry decorator with exponential backoff for handling API overload errors.
    """
    if max_retries is None:
        max_retries = Config.MAX_RETRIES
    if delay is None:
        delay = Config.RETRY_DELAY
    if backoff is None:
        backoff = Config.RETRY_BACKOFF
    
    def wrapper(*args, **kwargs):
        for attempt in range(max_retries + 1):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                error_str = str(e)
                
                # Check if it's a retryable error (overload or network issues)
                is_retryable_error = any(keyword in error_str.lower() for keyword in [
                    "503", "overloaded", "unavailable", "too many requests", "rate limit", "quota",
                    "temporary failure in name resolution", "connection error", "timeout", 
                    "network", "dns", "resolve", "connection refused", "connection timeout"
                ])
                
                if is_retryable_error:
                    if attempt < max_retries:
                        wait_time = min(delay * (backoff ** attempt), Config.MAX_RETRY_DELAY)
                        logger.warning(f"API/Network error (attempt {attempt + 1}/{max_retries + 1}). "
                                     f"Retrying in {wait_time:.1f} seconds...")
                        logger.info(f"Error details: {error_str}")
                        time.sleep(wait_time)
                        continue
                    else:
                        logger.error(f"API/Network still unavailable after {max_retries} retries. "
                                   f"Total wait time: {sum(min(delay * (backoff ** i), Config.MAX_RETRY_DELAY) for i in range(max_retries)):.1f} seconds")
                        raise e
                else:
                    # For non-retryable errors, don't retry
                    logger.error(f"Non-retryable error: {error_str}")
                    raise e
        
        return None
    
    return wrapper

# Research functions for the Content Researcher Agent
def search_web_func(query: str) -> str:
    """Search the web using Google Custom Search API for a given query."""
    try:
        logger.info(f"🔍 Searching web for: {query}")
        results = google_search(query, num=8)
        logger.info(f"✅ Found {len(results)} search results for: {query}")
        return json.dumps({
            "query": query,
            "results": results,
            "total_found": len(results)
        }, indent=2)
    except Exception as e:
        logger.error(f"❌ Web search error for '{query}': {e}")
        # Return mock data if API fails - but clearly indicate it's mock data
        return json.dumps({
            "query": query,
            "error": str(e),
            "results": [],
            "note": "Search API not available, using topic-based content generation"
        })

def scrape_content_func(url: str) -> str:
    """Scrape content from a webpage URL."""
    try:
        logger.info(f"📄 Scraping content from: {url}")
        result = scrape_webpage(url)
        logger.info(f"✅ Successfully scraped content from: {url}")
        return json.dumps(result, indent=2)
    except Exception as e:
        logger.error(f"❌ Scraping error for {url}: {e}")
        return json.dumps({"error": str(e), "url": url, "content": ""})

def analyze_topic_func(topic: str) -> str:
    """Analyze a topic and generate relevant research points when web search is not available."""
    logger.info(f"🧠 Analyzing topic: {topic}")
    
    # Create topic-specific research structure
    analysis = {
        "topic": topic,
        "analysis_method": "AI-based topic analysis",
        "suggested_research_areas": [
            f"Background and history of {topic}",
            f"Key achievements and milestones related to {topic}",
            f"Current status and recent developments about {topic}",
            f"Impact and significance of {topic}",
            f"Future outlook and implications of {topic}"
        ],
        "content_focus": f"Generate content specifically about '{topic}' and not generic presentation advice"
    }
    
    logger.info(f"✅ Topic analysis completed for: {topic}")
    return json.dumps(analysis, indent=2)

class PPTAgents:
    """
    Defines all the AI agents for PPT generation using CrewAI framework.
    Each agent has a specific role in the presentation creation pipeline.
    """
    
    def __init__(self, use_fallback_model=False):
        try:
            self.model = Config.FALLBACK_MODEL if use_fallback_model else Config.CREWAI_MODEL
            self.use_fallback = use_fallback_model
            if use_fallback_model:
                logger.info(f"Using fallback model: {self.model}")
            
            # Create model instance with generation settings
            self.model_instance = genai.GenerativeModel(
                self.model,
                generation_config=DEFAULT_GENERATION_CONFIG
            )
            logger.info(f"Successfully initialized model: {self.model}")
        except Exception as e:
            logger.error(f"Error initializing agent model: {e}")
            raise
            
    def presentation_generator_agent(self):
        """
        Presentation Generator Agent: Creates the final presentation output from the content and design specifications.
        """
        return Agent(
            role='Presentation Generator',
            goal='Transform the design specifications into a polished, interactive presentation',
            backstory="""You are an expert presentation developer with years of experience in creating 
            stunning digital presentations. You understand modern web technologies, visual design principles,
            and how to create engaging, interactive presentations. Your skills include implementing smooth
            transitions, responsive layouts, and ensuring the final presentation is both visually appealing
            and functionally robust. You excel at converting complex design specifications into polished,
            professional presentations that effectively communicate the intended message.""",
            verbose=True,
            allow_delegation=False,
            llm=getattr(self, 'model_instance', self.model)  # Fallback to self.model if model_instance isn't available
        )
    
    def content_researcher_agent(self):
        """
        Content Researcher Agent: Searches and analyzes web content to create presentation structure.
        """
        return Agent(
            role='Content Researcher',
            goal=f'Research and gather specific information about the given topic, not generic presentation advice',
            backstory="""You are an expert content researcher who specializes in gathering specific 
            information about requested topics. You MUST focus on the exact topic provided by the user 
            and gather real, factual information about that specific subject. You have access to web 
            search capabilities to find current, relevant information. Your job is to research the 
            SPECIFIC TOPIC requested, not to provide generic presentation advice or unrelated content. 
            You ALWAYS start by analyzing the exact topic requested and gathering relevant facts and 
            information about that specific subject.""",
            verbose=True,
            allow_delegation=False,
            llm=getattr(self, 'model_instance', self.model)
        )

    def planner_agent(self):
        """
        Planner Agent: Creates presentation structure based on researched content.
        """
        return Agent(
            role='Presentation Planner',
            goal='Analyze researched content and create an engaging presentation structure',
            backstory="""You are a professional presentation strategist who excels at organizing 
            information into clear, compelling narratives. You analyze provided research content 
            to identify key themes and create a logical presentation structure. You know how to 
            break down complex topics into digestible slides and ensure the presentation flows 
            naturally while maintaining audience engagement.""",
            verbose=True,
            allow_delegation=False,
            llm=getattr(self, 'model_instance', self.model)
        )
    
    def content_creator_agent(self):
        """
        Content Creator Agent: Generates actual textual content for each slide based on the blueprint.
        """
        return Agent(
            role='Content Creator',
            goal='Generate engaging and relevant plain-text content for each slide based on the presentation plan',
            backstory="""You are a skilled content writer and researcher who specializes in creating 
            presentation content. You have the ability to transform abstract concepts into clear, 
            engaging text that resonates with audiences. You understand how to write compelling 
            headlines, informative bullet points, and descriptive text that supports the overall 
            presentation narrative. Your content is always well-researched, accurate, and tailored 
            to the intended audience. 
            
            IMPORTANT: You NEVER use markdown formatting like **, *, __, _, ~~, or ` in your content. 
            You write in plain text only, using clear language and proper sentence structure. 
            For emphasis, you use capital letters or rephrase sentences. You keep bullet points 
            concise and under 15 words each.""",
            verbose=True,
            allow_delegation=False,
            llm=self.model
        )
    
    def designer_agent(self):
        """
        Designer Agent: Defines visual presentation, layout, and styling for each slide.
        """
        return Agent(
            role='Presentation Designer',
            goal='Create visually appealing and professional slide designs that enhance content delivery',
            backstory="""You are a professional presentation designer with extensive experience in 
            visual communication and graphic design. You understand color theory, typography, 
            layout principles, and how to create slides that are both beautiful and functional. 
            You know how to balance text and visuals, choose appropriate color schemes, and 
            create layouts that guide the viewer's attention effectively. Your designs always 
            maintain consistency and professionalism while being visually engaging.""",
            verbose=True,
            allow_delegation=False,
            llm=self.model
        )

class PPTTasks:
    """
    Defines all the tasks that agents will perform in the PPT generation pipeline.
    """
    
    def research_task(self, agent, topic, num_slides):
        """
        Task for the Content Researcher Agent to gather and analyze web content.
        """
        # Ensure num_slides is an integer
        num_slides = int(num_slides) if isinstance(num_slides, str) else num_slides
        
        return Task(
            description=f'''
            CRITICAL MISSION: Research and gather specific information about "{topic}" ONLY.
            
            You are researching: "{topic}"
            Target slides: {num_slides}
            
            MANDATORY REQUIREMENTS:
            1. Focus EXCLUSIVELY on "{topic}" - this is your research subject
            2. Do NOT research "presentation skills", "how to present", or "presentation tips"
            3. Research factual information, background, and key details about "{topic}"
            4. Gather current information and recent developments about "{topic}"
            5. Find key facts, achievements, and significance of "{topic}"
            
            RESEARCH AREAS FOR "{topic}":
            - Background and history of {topic}
            - Key facts and information about {topic}
            - Recent developments and current status of {topic}
            - Achievements and milestones related to {topic}
            - Impact and significance of {topic}
            - Notable quotes or statements about {topic}
            
            OUTPUT STRUCTURE (JSON format):
            {{
                "researched_topic": "{topic}",
                "research_focus": "Specific information about {topic}",
                "research_method": "Topic analysis and fact gathering",
                "main_themes": [
                    {{
                        "theme": "Background of {topic}",
                        "importance": 9,
                        "content": "Historical background and origin of {topic}",
                        "key_points": ["Specific facts about {topic}"]
                    }},
                    {{
                        "theme": "Key achievements of {topic}",
                        "importance": 8,
                        "content": "Major accomplishments and milestones of {topic}",
                        "key_points": ["Notable achievements of {topic}"]
                    }},
                    {{
                        "theme": "Current status of {topic}",
                        "importance": 8,
                        "content": "Recent developments and current situation of {topic}",
                        "key_points": ["Current facts about {topic}"]
                    }},
                    {{
                        "theme": "Impact of {topic}",
                        "importance": 7,
                        "content": "Significance and influence of {topic}",
                        "key_points": ["Impact areas of {topic}"]
                    }}
                ],
                "key_facts": [
                    {{
                        "fact": "Specific factual information about {topic}",
                        "context": "Context about this aspect of {topic}",
                        "relevance": "Why this fact is important for understanding {topic}"
                    }}
                ],
                "suggested_slide_topics": [
                    "Introduction to {topic}",
                    "Background and History of {topic}",
                    "Key Achievements of {topic}",
                    "Current Status of {topic}",
                    "Impact and Legacy of {topic}"
                ]
            }}
            
            CRITICAL: Your research must be about "{topic}" specifically. Do not generate content about presentations, public speaking, or communication skills.
            ''',
            agent=agent,
            expected_output=f"Comprehensive factual research specifically about '{topic}'"
        )

    def planning_task(self, agent, research_result, num_slides):
        """
        Task for the Planner Agent to create presentation structure from research.
        """
        # Ensure num_slides is an integer
        num_slides = int(num_slides) if isinstance(num_slides, str) else num_slides
        
        return Task(
            description=f"""
            Create a {num_slides}-slide presentation structure based ONLY on the research data provided.
            
            Research Data: {research_result}
            
            CRITICAL RULES:
            1. Use ONLY the topic and information from the research data
            2. Do NOT add generic presentation advice
            3. Create slides specifically about the researched topic
            4. Base slide titles and content on the research themes and facts
            5. Each slide must relate to the specific topic researched
            
            CONTENT LENGTH PLANNING:
            6. Plan slide titles to be ≤ 10 words maximum
            7. For bullet_points content type: plan for 5-6 bullet points maximum
            8. For paragraph content type: plan for 40-50 words maximum
            9. Ensure content fits slide dimensions and readability
            
            Slide Distribution Strategy:
            - Slide 1: Introduction to the specific topic
            - Slides 2 to {num_slides - 1}: Main themes/aspects from research (This should be {num_slides - 2} slides)
            - Slide {num_slides}: Conclusion/summary of the topic
            
            Output Format (JSON ONLY):
            {{
                "presentation_title": "Title based on researched topic",
                "presentation_description": "Description of the specific topic",
                "target_topic": "The exact topic researched",
                "total_slides": {num_slides},
                "slides": [
                    {{
                        "slide_number": 1,
                        "title": "Title based on research theme",
                        "subtitle": "Subtitle related to the topic",
                        "content_type": "title_only|bullet_points|paragraph|two_column",
                        "description": "What this slide covers about the topic",
                        "research_theme": "Which research theme this slide covers",
                        "key_points": ["Points from research data"],
                        "sources": ["Sources from research"]
                    }}
                ]
            }}
            """,
            agent=agent,
            expected_output="Presentation structure based ONLY on the researched topic"
        )
    
    def content_creation_task(self, agent, planning_result, research_data):
        """
        Task for the Content Creator Agent to generate content for each slide based on research and planning.
        """
        return Task(
            description=f"""
            Generate specific content for each slide using ONLY the research data and planning structure provided.
            
            Planning Structure: {planning_result}
            Research Data: {research_data}
            
            STRICT CONTENT RULES:
            1. Use ONLY information from the research data provided
            2. Do NOT create generic presentation advice or tips
            3. Focus on the specific topic that was researched
            4. Each slide must contain factual information about the topic
            5. Use research themes, facts, and sources provided
            6. Content must be plain text - NO markdown formatting
            
            CONTENT LENGTH CONSTRAINTS:
            7. Slide titles: Maximum 10 words per title
            8. Bullet points: Maximum 5-6 bullet points per slide
            9. Paragraphs: Maximum 40-50 words per paragraph
            10. Keep content concise to ensure proper slide formatting and readability
            
            For each slide, create content that:
            - Relates directly to the researched topic
            - Uses facts and themes from the research data
            - Includes specific information, not generic advice
            - Cites sources when using specific facts
            - STRICTLY FOLLOWS LENGTH LIMITS (count words carefully!)
            - Prioritizes clarity and conciseness for slide readability
            
            Content Types:
            - bullet_points: Use research facts as bullet points (MAX 5-6 points, each ≤ 10 words)
            - paragraph: Write paragraphs using research information (MAX 40-50 words per paragraph)
            - title_only: Create impactful titles about the topic (MAX 10 words)
            - two_column: Compare aspects from research data (each column ≤ 50 words)
            
            Output Format (JSON):
            {{
                "presentation_title": "Title from planning (≤ 10 words)",
                "topic_focus": "The specific topic researched",
                "slides": [
                    {{
                        "slide_number": 1,
                        "title": "Slide title from planning (≤ 10 words)",
                        "subtitle": "Subtitle if needed (≤ 8 words)",
                        "content_type": "From planning structure",
                        "main_content": "Content based on research data (follow length constraints by type)",
                        "sources": ["Sources from research data"],
                        "research_basis": "Which research theme this content is based on"
                    }}
                ]
            }}
            
            CONTENT LENGTH EXAMPLES:
            - Title: "AI Impact on Modern Healthcare" (5 words ✓)
            - Bullet Point: "• Reduces diagnosis time by 40%" (6 words ✓)
            - Paragraph: "Machine learning algorithms analyze medical data faster than traditional methods, improving patient outcomes significantly across multiple healthcare sectors." (19 words ✓)
            
            ALWAYS count words and stay within limits!
            """,
            agent=agent,
            expected_output="Slide content based strictly on research data about the specific topic"
        )
    
    def design_task(self, agent, content_result, research_data):
        """
        Task for the Designer Agent to define visual styling and layout using research insights.
        """
        return Task(
            description=f"""
            Define the visual design and layout for a research-backed presentation.
            
            Content Structure: {content_result}
            Research Data: {research_data}
            
            For each slide:
            1. Choose layout based on content type and research data
            2. Determine appropriate visual elements based on content:
               - Bar charts for statistics, percentages, growth data
               - Process diagrams for workflows, methodologies, step-by-step processes
               - Timeline visualizations for historical data, roadmaps, evolution
               - Comparison grids for feature comparisons, before/after, pros/cons
               - Icons for key concepts and categories
               - Card layouts for highlighting important information
            3. Create a cohesive visual theme that:
               - Reflects the topic's domain
               - Supports data visualization
               - Enhances content readability
            4. Define data presentation formats:
               - Use charts for numerical data (percentages, statistics, growth)
               - Use process flows for sequential information
               - Use timelines for chronological data
               - Use comparison grids for competitive analysis
               - Use icons to represent concepts visually
            
            CRITICAL: Based on content analysis, you MUST specify which visual elements to use:
            - If content has numbers/statistics → specify "bar_chart" or "comparison_grid"
            - If content describes processes → specify "process_diagram" 
            - If content has dates/history → specify "timeline"
            - If content compares items → specify "comparison_grid"
            - Always use relevant icons for key concepts
            
            Add design specifications:
            - "layout_type": Based on content and research
            - "visual_elements": {{"type": "chart|image|icon|diagram", "purpose": "data|concept|process"}}
            - "color_scheme": Primary and accent colors
            - "typography": Font choices and text hierarchy
            - "data_visualization": Chart types and formats
            - "source_styling": Citation and attribution design
            
            Design Guidelines:
            1. Academic and Professional:
               - Clean, data-focused layouts
               - Clear visual hierarchy
               - Prominent source attributions
            2. Research Emphasis:
               - Visualize data effectively
               - Clear citation formatting
            3. Visual Balance:
               - Content-to-whitespace ratio
               - Text-to-visual balance
               - Consistent alignment
            """,
            agent=agent,
            expected_output="Complete JSON with content and comprehensive design specifications"
        )

    def presentation_generation_task(self, agent, design_result):
        """
        Task for the Presentation Generator Agent to create the final presentation.
        """
        return Task(
            description=f'''
            Create individual HTML files for each slide with enhanced visual design and interactive elements.

            Design Specifications: {design_result}

            CRITICAL REQUIREMENTS:

            0. VISUAL ELEMENT IMPLEMENTATION:
               - Analyze the design specifications for visual element requirements
               - If design specifies "bar_chart" → implement actual bar chart with data
               - If design specifies "process_diagram" → create step-by-step visual flow
               - If design specifies "timeline" → build chronological timeline
               - If design specifies "comparison_grid" → create comparison layout
               - Always use relevant icons for key concepts

            1. CONTENT LENGTH VALIDATION:
               - Verify titles are ≤ 10 words
               - Ensure bullet points are ≤ 6 items per slide
               - Confirm paragraphs are ≤ 50 words
               - Content must fit properly in slide layout

            1. Enhanced Visual Structure:
               - Create stunning, modern slide layouts with visual elements
               - Use the 16:9 aspect ratio (1920x1080px) effectively
               - Include visual design elements where appropriate
               - Each slide must be a self-contained HTML file
               - No JavaScript or external resources

            2. Advanced Content Layout:
               - All content must be within .slide-content div
               - Title in .slide-title with visual emphasis
               - Main content in .slide-body with proper spacing
               - Add visual elements like cards and icons where appropriate
               - Use these content classes based on type:
                 * bullet-points for lists (with visual bullets)
                 * paragraph for text (with visual cards when appropriate)
                 * two-column for side-by-side content
                 * numbered-list for steps (with visual numbers)
                 * quote for quotations (with visual styling)
                 * center for title slides (centered content)

            3. Visual Enhancement Guidelines:
               - Use .card divs for important information blocks
               - Use .visual-element spans for key concepts
               - Add .center class for title slides
               - Include visual separators and spacing

            4. Enhanced HTML Template Structure:
               Use this exact template with embedded CSS for each slide:
               
               ```html
               <!DOCTYPE html>
               <html>
               <head>
                   <meta charset="UTF-8">
                   <title>Slide [NUMBER]</title>
                   <style>
                       * {{
                           box-sizing: border-box;
                           margin: 0;
                           padding: 0;
                       }}
                       
                       body {{
                           font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                           width: 1920px;
                           height: 1080px;
                           margin: 0;
                           padding: 0;
                           background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                           color: #333;
                           overflow: hidden;
                       }}
                       
                       .slide {{
                           width: 100%;
                           height: 100%;
                           display: flex;
                           align-items: center;
                           justify-content: center;
                           padding: 60px;
                           position: relative;
                       }}
                       
                       .slide-content {{
                           background: rgba(255, 255, 255, 0.95);
                           border-radius: 20px;
                           padding: 60px;
                           box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
                           max-width: 1400px;
                           width: 100%;
                           position: relative;
                       }}
                       
                       .slide-title {{
                           font-size: 3.5rem;
                           font-weight: bold;
                           color: #2c3e50;
                           margin-bottom: 30px;
                           text-align: center;
                           line-height: 1.2;
                       }}
                       
                       .slide-body {{
                           font-size: 1.8rem;
                           line-height: 1.6;
                           color: #34495e;
                       }}
                       
                       .center {{
                           text-align: center;
                           display: flex;
                           flex-direction: column;
                           justify-content: center;
                           align-items: center;
                           height: 100%;
                       }}
                       
                       .card {{
                           background: #f8f9fa;
                           border-radius: 15px;
                           padding: 30px;
                           margin: 20px 0;
                           border-left: 5px solid #3498db;
                           box-shadow: 0 5px 15px rgba(0, 0, 0, 0.08);
                       }}
                       
                       .visual-element {{
                           display: inline-block;
                           color: #667eea;
                           font-weight: bold;
                           font-size: 1.6rem;
                           margin: 0 3px;
                       }}
                       
                       .bullet-points {{
                           list-style: none;
                           padding: 0;
                       }}
                       
                       .bullet-points li {{
                           margin: 20px 0;
                           padding-left: 40px;
                           position: relative;
                           font-size: 1.6rem;
                       }}
                       
                       .bullet-points li::before {{
                           content: "●";
                           color: #3498db;
                           font-size: 2rem;
                           position: absolute;
                           left: 0;
                           top: -2px;
                       }}
                       
                       .two-column {{
                           display: grid;
                           grid-template-columns: 1fr 1fr;
                           gap: 40px;
                           align-items: start;
                       }}
                       
                       h2 {{
                           font-size: 2.5rem;
                           color: #667eea;
                           margin-bottom: 20px;
                           text-align: center;
                       }}
                       
                       h3 {{
                           font-size: 2rem;
                           color: #764ba2;
                           margin-bottom: 15px;
                       }}
                       
                       p {{
                           margin-bottom: 15px;
                           text-align: justify;
                       }}
                       
                       .quote {{
                           font-style: italic;
                           font-size: 2rem;
                           color: #555;
                           text-align: center;
                           position: relative;
                           padding: 20px;
                       }}
                       
                       .quote::before {{
                           content: """;
                           font-size: 4rem;
                           color: #3498db;
                           position: absolute;
                           top: -10px;
                           left: -10px;
                       }}
                       
                       .source-citation {{
                           text-align: right;
                           font-size: 1.2rem;
                           color: #7f8c8d;
                           margin-top: 15px;
                           font-style: normal;
                       }}
                       
                       /* Chart and Visual Elements Styling */
                       .chart-container {{
                           margin: 30px 0;
                           text-align: center;
                       }}
                       
                       .chart-visual {{
                           margin: 20px 0;
                           padding: 20px;
                           background: #f8f9fa;
                           border-radius: 10px;
                       }}
                       
                       .bar-chart {{
                           display: flex;
                           justify-content: space-around;
                           align-items: end;
                           height: 200px;
                           padding: 20px;
                       }}
                       
                       .bar {{
                           background: linear-gradient(45deg, #667eea, #764ba2);
                           width: 80px;
                           border-radius: 5px 5px 0 0;
                           display: flex;
                           align-items: end;
                           justify-content: center;
                           color: white;
                           font-weight: bold;
                           padding: 10px 5px;
                           font-size: 1rem;
                       }}
                       
                       .process-diagram {{
                           margin: 30px 0;
                           text-align: center;
                       }}
                       
                       .process-flow {{
                           display: flex;
                           justify-content: center;
                           align-items: center;
                           margin: 20px 0;
                           flex-wrap: wrap;
                       }}
                       
                       .process-step {{
                           background: #f8f9fa;
                           border-radius: 15px;
                           padding: 20px;
                           margin: 10px;
                           text-align: center;
                           min-width: 150px;
                           border: 2px solid #3498db;
                       }}
                       
                       .step-icon {{
                           font-size: 2.5rem;
                           margin-bottom: 10px;
                       }}
                       
                       .arrow {{
                           font-size: 2rem;
                           color: #3498db;
                           margin: 0 10px;
                       }}
                       
                       .comparison-grid {{
                           display: grid;
                           grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                           gap: 20px;
                           margin: 30px 0;
                       }}
                       
                       .comparison-item {{
                           background: #f8f9fa;
                           border-radius: 15px;
                           padding: 30px;
                           text-align: center;
                           border: 2px solid #e9ecef;
                           transition: transform 0.2s;
                       }}
                       
                       .comparison-item:hover {{
                           transform: translateY(-5px);
                       }}
                       
                       .icon-large {{
                           font-size: 3rem;
                           margin-bottom: 15px;
                       }}
                       
                       .timeline {{
                           margin: 30px 0;
                           position: relative;
                           padding-left: 30px;
                       }}
                       
                       .timeline::before {{
                           content: '';
                           position: absolute;
                           left: 15px;
                           top: 0;
                           bottom: 0;
                           width: 3px;
                           background: #3498db;
                       }}
                       
                       .timeline-item {{
                           position: relative;
                           margin-bottom: 30px;
                           background: #f8f9fa;
                           border-radius: 10px;
                           padding: 20px;
                           margin-left: 20px;
                       }}
                       
                       .timeline-item::before {{
                           content: '';
                           position: absolute;
                           left: -30px;
                           top: 20px;
                           width: 12px;
                           height: 12px;
                           background: #3498db;
                           border-radius: 50%;
                       }}
                       
                       .timeline-date {{
                           font-weight: bold;
                           color: #667eea;
                           font-size: 1.2rem;
                           margin-bottom: 10px;
                       }}
                       
                       .card-icon {{
                           font-size: 2.5rem;
                           text-align: center;
                           margin-bottom: 15px;
                       }}
                   </style>
               </head>
               <body>
                   <div class="slide">
                       <div class="slide-content">
                           <h1 class="slide-title">[TITLE]</h1>
                           <div class="slide-body">
                               [VISUALLY ENHANCED CONTENT BASED ON TYPE]
                           </div>
                       </div>
                   </div>
               </body>
               </html>
               ```

            5. Enhanced Content Type Examples with Visual Elements:
               
               For statistical data with charts:
               ```html
               <div class="chart-container">
                   <h3>Market Growth Statistics</h3>
                   <div class="chart-visual">
                       <div class="bar-chart">
                           <div class="bar" style="height: 60%"><span>2020: 60%</span></div>
                           <div class="bar" style="height: 75%"><span>2021: 75%</span></div>
                           <div class="bar" style="height: 90%"><span>2022: 90%</span></div>
                       </div>
                   </div>
               </div>
               ```

               For process flows with diagrams:
               ```html
               <div class="process-diagram">
                   <h3>AI Development Process</h3>
                   <div class="process-flow">
                       <div class="process-step">
                           <div class="step-icon">📊</div>
                           <span>Data Collection</span>
                       </div>
                       <div class="arrow">→</div>
                       <div class="process-step">
                           <div class="step-icon">🤖</div>
                           <span>Model Training</span>
                       </div>
                       <div class="arrow">→</div>
                       <div class="process-step">
                           <div class="step-icon">🎯</div>
                           <span>Deployment</span>
                       </div>
                   </div>
               </div>
               ```

               For comparative data with visual icons:
               ```html
               <div class="comparison-grid">
                   <div class="comparison-item">
                       <div class="icon-large">🚀</div>
                       <h4>Performance</h4>
                       <p>300% improvement</p>
                   </div>
                   <div class="comparison-item">
                       <div class="icon-large">💰</div>
                       <h4>Cost Reduction</h4>
                       <p>40% savings</p>
                   </div>
                   <div class="comparison-item">
                       <div class="icon-large">⚡</div>
                       <h4>Speed</h4>
                       <p>5x faster</p>
                   </div>
               </div>
               ```

               For timeline data:
               ```html
               <div class="timeline">
                   <div class="timeline-item">
                       <div class="timeline-date">2020</div>
                       <div class="timeline-content">
                           <h4>🎯 First Implementation</h4>
                           <p>Initial AI prototype launched</p>
                       </div>
                   </div>
                   <div class="timeline-item">
                       <div class="timeline-date">2023</div>
                       <div class="timeline-content">
                           <h4>📈 Major Breakthrough</h4>
                           <p>Advanced model deployment</p>
                       </div>
                   </div>
               </div>
               ```

               For bullet points with minimal highlighting:
               ```html
               <ul class="bullet-points">
                   <li>🔍 <span class="visual-element">Key Point</span> Additional explanation</li>
                   <li>⚡ Important term with context</li>
               </ul>
               ```
               
               For clean bullet points without highlighting:
               ```html
               <ul class="bullet-points">
                   <li>🔍 Research and Development Progress</li>
                   <li>⚡ Implementation Strategy</li>
                   <li>📊 Performance Metrics</li>
               </ul>
               ```

               For cards with important information:
               ```html
               <div class="card">
                   <div class="card-icon">💡</div>
                   <h3>Important Concept</h3>
                   <p>Detailed explanation with emphasized terms</p>
               </div>
               ```

               For two columns with visual balance:
               ```html
               <div class="two-column">
                   <div class="column">
                       <div class="card">
                           <h3>Left Topic</h3>
                           <p>Content here</p>
                       </div>
                   </div>
                   <div class="column">
                       <div class="card">
                           <h3>Right Topic</h3>
                           <p>Content here</p>
                       </div>
                   </div>
               </div>
               ```

               For centered title slides:
               ```html
               <div class="center">
                   <h1 class="slide-title">Main Title</h1>
                   <h2>Subtitle</h2>
                   <p>Brief description with key points</p>
               </div>
               ```

               For quotes with visual styling:
               ```html
               <div class="card">
                   <div class="quote">
                       <p>"Quote text here"</p>
                       <div class="source-citation">- Source Name</div>
                   </div>
               </div>
               ```

            6. Design Rules:
               - Use visual elements strategically, not on every slide
               - Maintain readability and balance
               - Use cards for important information blocks
               - Keep consistent visual hierarchy
               - The CSS is already provided in the template above - USE IT EXACTLY
               - Clean, semantic HTML structure

            7. Content Guidelines:
               - Never exceed slide boundaries
               - Keep titles to 1-2 lines maximum
               - For bullet points, limit to 5-6 items
               - Use visual elements to break up text
               - Add source citations for factual content

            8. VISUAL ELEMENT USAGE REQUIREMENTS:
               - For ANY numerical data (percentages, statistics, growth): Use bar charts
               - For ANY process or methodology content: Use process diagrams  
               - For ANY historical or chronological content: Use timelines
               - For ANY comparison content: Use comparison grids
               - For ALL key concepts: Use relevant icons INSTEAD of visual-element spans
               - Prefer clean icons (🚀📊💡⚡🎯📈🔍💰🤖) over highlighted text
               - Use visual-element spans SPARINGLY, only for truly critical terms
               - Example: "🚀 Performance improvement" instead of "<span class='visual-element'>Performance</span> improvement"

            9. CRITICAL: You MUST use the HTML template structure above INCLUDING the <style> section.
               Each slide should be a complete HTML file with embedded CSS styling.

            Format your response as a series of HTML code blocks, one for each slide:

            ```html
            <!-- Slide 1 -->
            [HTML for slide 1]
            ```

            ```html
            <!-- Slide 2 -->
            [HTML for slide 2]
            ```

            And so on for each slide.
            ''',
            agent=agent,
            expected_output="A single HTML file containing the complete presentation."
        )
    
    @staticmethod
    def validate_content_length(content_data):
        """
        Validate that content adheres to length constraints.
        
        Args:
            content_data (dict): Content data with slides
            
        Returns:
            tuple: (is_valid, validation_errors)
        """
        errors = []
        
        # Check presentation title
        if 'presentation_title' in content_data:
            title_words = len(content_data['presentation_title'].split())
            if title_words > 10:
                errors.append(f"Presentation title too long: {title_words} words (max 10)")
        
        # Check each slide
        if 'slides' in content_data:
            for slide in content_data['slides']:
                slide_num = slide.get('slide_number', 'Unknown')
                
                # Check slide title
                if 'title' in slide:
                    title_words = len(slide['title'].split())
                    if title_words > 10:
                        errors.append(f"Slide {slide_num} title too long: {title_words} words (max 10)")
                
                # Check content based on type
                if 'main_content' in slide and 'content_type' in slide:
                    content = slide['main_content']
                    content_type = slide['content_type']
                    
                    if content_type == 'bullet_points':
                        # Count bullet points (assuming each line is a bullet)
                        bullet_count = len([line for line in content.split('\n') if line.strip()])
                        if bullet_count > 6:
                            errors.append(f"Slide {slide_num} has too many bullet points: {bullet_count} (max 6)")
                    
                    elif content_type == 'paragraph':
                        # Count words in paragraph
                        word_count = len(content.split())
                        if word_count > 50:
                            errors.append(f"Slide {slide_num} paragraph too long: {word_count} words (max 50)")
        
        return len(errors) == 0, errors

class PPTCrew:
    """
    Orchestrates the AI agents in the presentation creation process.
    """
    
    def __init__(self, use_fallback_model=False):
        self.agents = PPTAgents(use_fallback_model)
        self.tasks = PPTTasks()  # Initialize tasks instance

    @retry_with_backoff
    def create_presentation(self, topic, style_preferences=None):
        """
        Create a research-driven presentation using multiple AI agents.
        """
        logger.info(f"🚀 PPTCrew starting presentation creation for topic: '{topic}'")
        
        # Initialize agents
        researcher = self.agents.content_researcher_agent()
        planner = self.agents.planner_agent()
        content_creator = self.agents.content_creator_agent()
        designer = self.agents.designer_agent()
        generator = self.agents.presentation_generator_agent()

        # Ensure num_slides is an integer
        num_slides = style_preferences.get('num_slides', 5)
        num_slides = int(num_slides) if isinstance(num_slides, str) else num_slides
        logger.info(f"📊 Creating {num_slides} slides about: '{topic}'")

        # Research Phase: Gather and analyze web content
        logger.info(f"🔍 PHASE 1: Starting research for topic: '{topic}'")
        research_task = self.tasks.research_task(
            researcher, topic, num_slides
        )

        crew = Crew(
            agents=[researcher],
            tasks=[research_task],
            process=Process.sequential,
            verbose=True
        )

        logger.info(f"🔍 Executing research phase for: '{topic}'")
        research_result = crew.kickoff()
        logger.info(f"✅ Research phase completed for: '{topic}'")

        # Planning Phase: Create structure based on research
        logger.info(f"📋 PHASE 2: Starting planning based on research about: '{topic}'")
        planning_task = self.tasks.planning_task(
            planner, research_result, num_slides
        )
        planning_task.context = [research_task]

        crew = Crew(
            agents=[planner],
            tasks=[planning_task],
            process=Process.sequential,
            verbose=True
        )

        logger.info(f"📋 Executing planning phase for: '{topic}'")
        planning_result = crew.kickoff()
        logger.info(f"✅ Planning phase completed for: '{topic}'")

        # Content Creation Phase
        logger.info(f"✍️ PHASE 3: Creating content for: '{topic}'")
        content_task = self.tasks.content_creation_task(
            content_creator, planning_result, research_result
        )
        content_task.context = [planning_task, research_task]

        crew = Crew(
            agents=[content_creator],
            tasks=[content_task],
            process=Process.sequential,
            verbose=True
        )

        logger.info(f"✍️ Executing content creation for: '{topic}'")
        content_result = crew.kickoff()
        logger.info(f"✅ Content creation completed for: '{topic}'")

        # Design Phase
        logger.info(f"🎨 PHASE 4: Designing presentation for: '{topic}'")
        design_task = self.tasks.design_task(
            designer, content_result, research_result
        )
        design_task.context = [content_task, research_task]

        crew = Crew(
            agents=[designer],
            tasks=[design_task],
            process=Process.sequential,
            verbose=True
        )

        logger.info(f"🎨 Executing design phase for: '{topic}'")
        design_result = crew.kickoff()
        logger.info(f"✅ Design phase completed for: '{topic}'")

        # Generation Phase
        logger.info(f"🏗️ PHASE 5: Generating final presentation for: '{topic}'")
        generation_task = self.tasks.presentation_generation_task(
            generator, design_result
        )
        generation_task.context = [design_task]

        crew = Crew(
            agents=[generator],
            tasks=[generation_task],
            process=Process.sequential,
            verbose=True
        )

        logger.info(f"🏗️ Executing final generation for: '{topic}'")
        final_result = crew.kickoff()
        logger.info(f"🎉 Presentation generation COMPLETED for: '{topic}'")
        return final_result