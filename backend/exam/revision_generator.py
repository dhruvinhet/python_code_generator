# backend/revision_generator.py

import os
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
import google.generativeai as genai
from .config import GENERATION_MODEL
from flask import jsonify
import markdown_it
from .quiz_generator import retrieve_relevant_chunks

def generate_topic_summary(topic, level, context):
    """Generates an elaborated or brush-up summary for a given topic based on level."""
    instruction = ""
    if level == "weak":
        instruction = f"Provide a detailed and elaborated explanation of the topic '{topic}' based on the context. Break down complex concepts and provide clear examples to help with understanding."
    elif level == "strong":
        instruction = f"Provide a concise summary of the topic '{topic}' based on the context. Focus on key points and a quick brush-up to reinforce knowledge."

    prompt = f"""
    You are an AI assistant creating a revision sheet.
    
    INSTRUCTION: {instruction}
    
    CONTEXT START
    {context}
    CONTEXT END
    
    Format the output using clear headings and bullet points where appropriate.
    """
    try:
        model = genai.GenerativeModel(GENERATION_MODEL)
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        print(f"Error generating topic summary: {e}")
        return "Content not available due to a generation error."

def markdown_to_plain_text(markdown_string):
    """Converts markdown to plain text."""
    if not isinstance(markdown_string, str):
        return ""
    md = markdown_it.MarkdownIt()
    html = md.render(markdown_string)
    # This regular expression removes HTML tags and replaces newlines
    plain_text = re.sub(r'<[^>]+>', '', html)
    return plain_text


def generate_revision_text(quiz_results, analysis, document_title, faiss_index, chunks):
    """
    Generates a comprehensive revision sheet based on weak and strong areas.
    """
    revision_text = f"# Revision Sheet for {document_title}\n\n"
    
    # 1. Generate content for weak areas
    if analysis and analysis.get('weak_areas'):
        revision_text += "## Weak Areas - Detailed Explanation\n\n"
        for topic in analysis['weak_areas']:
            context_chunks = retrieve_relevant_chunks(topic, faiss_index, chunks, k=3)
            context = "\n\n".join(context_chunks)
            summary = generate_topic_summary(topic, "weak", context)
            revision_text += f"### {topic}\n{summary}\n\n"

    # 2. Add the incorrect questions for quick review
    incorrect_questions = [q for q in quiz_results if not q['evaluation']['is_correct']]
    if incorrect_questions:
        revision_text += "## Incorrectly Answered Questions\n\n"
        for i, q in enumerate(incorrect_questions):
            question_text = q.get('question', '')
            user_answer_text = q.get('userAnswer', '')
            correct_answer_text = q.get('correctAnswer', '')
            explanation_text = ""
            if q.get('evaluation') and q['evaluation'].get('explanation'):
                explanation_text = q['evaluation']['explanation']

            revision_text += f"### Question {i+1}: {question_text}\n"
            revision_text += f"**Your Answer:** {user_answer_text}\n"
            revision_text += f"**Correct Answer:** {correct_answer_text}\n\n"
            if explanation_text:
                revision_text += f"**Explanation:** {explanation_text}\n\n"

    return revision_text

import re

def format_inline_markdown(text):
    """Formats bold and italic markdown within a line."""
    text = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', text)
    text = re.sub(r'\*(.*?)\*', r'<i>\1</i>', text)
    text = text.replace('<br>', '<br/>')
    return text

# In backend/revision_generator.py

# ... (all existing imports and functions) ...

def generate_revision_pdf(revision_text, output_buffer):
    """
    Generates a PDF file from the given text using ReportLab, with all markdown stripped.
    """
    doc = SimpleDocTemplate(output_buffer, pagesize=letter)
    story = []
    styles = getSampleStyleSheet()

    # Define a custom style for the body text
    styles.add(ParagraphStyle(name='NormalPlain', fontSize=10, fontName='Helvetica', leading=12, spaceAfter=6))
    styles.add(ParagraphStyle(name='H1Plain', parent=styles['Heading1'], fontSize=18, spaceAfter=12))
    styles.add(ParagraphStyle(name='H2Plain', parent=styles['Heading2'], fontSize=14, spaceAfter=10))
    styles.add(ParagraphStyle(name='H3Plain', parent=styles['Heading3'], fontSize=12, spaceAfter=8))
    
    # Split the revision text into blocks based on Markdown headings or newlines
    lines = revision_text.split('\n')

    # Iterate through each line and add it to the PDF, stripping markdown
    for line in lines:
        stripped_line = markdown_to_plain_text(line)
        if stripped_line.strip():
            # Use ReportLab's built-in styles for consistency
            if line.startswith('###'):
                story.append(Paragraph(stripped_line, styles['H3Plain'])) # Corrected style name
            elif line.startswith('##'):
                story.append(Paragraph(stripped_line, styles['H2Plain'])) # Corrected style name
            elif line.startswith('#'):
                story.append(Paragraph(stripped_line, styles['H1Plain'])) # Corrected style name
            else:
                story.append(Paragraph(stripped_line, styles['NormalPlain'])) # Corrected style name

    doc.build(story)



