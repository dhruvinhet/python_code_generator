# backend/story_generator.py

import google.generativeai as genai
from .config import GENERATION_MODEL

def generate_story_explanation(context, document_title):
    """
    Prompts Gemini to generate a detailed, easy-to-understand explanation of a document's concepts.
    """
    prompt = f"""
    You are an expert educator and a creative storyteller. Your task is to explain the key concepts
    from the following document in detail. The explanation should be in easy, practical language,
    with a clear, real-world example for each concept to help a student understand it.
    
    The explanation should be presented in a friendly, conversational tone and use clear headings
    and Markdown formatting.

    Document Title: {document_title}
    
    Document Content:
    \"\"\"
    {context}
    \"\"\"
    
    Start with an introduction to the main idea, then for each key concept found in the document,
    provide a clear explanation and a practical, real-world example.
    
    Example format:
    
    ## Introduction
    [Introductory text about the document's purpose.]
    
    ## Concept 1: [Name of the concept]
    
    ### Explanation
    [A detailed explanation of the concept.]
    
    ### Practical Example
    [A real-world example demonstrating the concept in action.]
    
    ## Concept 2: [Name of the second concept]
    
    ### Explanation
    [A detailed explanation of the second concept.]
    
    ### Practical Example
    [A real-world example demonstrating the second concept in action.]
    
    ...and so on for all major concepts.
    """
    
    try:
        model = genai.GenerativeModel(GENERATION_MODEL)
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        print(f"Error generating story explanation with Gemini: {e}")
        return "An error occurred while generating the explanation."
