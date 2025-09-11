# backend/learning_generator.py
import google.generativeai as genai
from .config import GENERATION_MODEL
from .evaluator import evaluate_theoretical_answer

def generate_initial_explanation(context, document_title, topic):
    """
    Prompts Gemini to generate a detailed initial explanation of a user-specified topic.
    """
    prompt = f"""
    Provide a concise explanation of the topic "{topic}" from the document titled "{document_title}".
    Only provide the explanation. Do not include any conversational text, introductions, or questions.

    Document Content:
    "
    {context}
    "
    """
    
    try:
        model = genai.GenerativeModel(GENERATION_MODEL)
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        print(f"Error generating initial explanation with Gemini: {e}")
        return "Explanation unavailable due to an error."

def generate_next_question(context, document_title, topic, user_message, is_correct, correct_answer):
    """
    Generates a follow-up question based on the user's previous answer.
    """
    if is_correct:
        prompt = f"""
        The student correctly answered the last question about "{topic}".
        Based on the document titled "{document_title}" and the provided context,
        ask a new, slightly more advanced question or a question about a related concept.
        The student's previous correct answer was: "{user_message}".

        Document Content:
        {context}

        End with a direct question.
        """
    else:
        prompt = f"""
        The user's answer was incorrect. The correct answer is "{correct_answer}".
        Based on the document titled "{document_title}" and the provided context, ask a new, slightly more advanced question about "{topic}" that helps reinforce the concept.

        The user's incorrect answer was: "{user_message}"

        Document Content:
        {context}

        Ask only the next question. Do not provide any explanation or conversational text.
        End with a direct question.
        """
    try:
        model = genai.GenerativeModel(GENERATION_MODEL)
        response = model.generate_content(prompt)
        text = response.text.strip()
        return text
    except Exception as e:
        print(f"Error generating next question with Gemini: {e}")
        return "Question unavailable due to an error. Please try again."

def generate_correct_answer(context, document_title, topic, question):
    """
    Generates a concise correct answer for a given question.
    """
    prompt = f"""
    Given the following document content from "{document_title}", and a question about the topic "{topic}",
    provide a concise and direct correct answer to the question.

    Document Content:
    {context}

    Question: {question}

    Correct Answer:
    """
    
    try:
        model = genai.GenerativeModel(GENERATION_MODEL)
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        print(f"Error generating correct answer with Gemini: {e}")
        return "Answer unavailable due to an error."

def generate_first_question(context, document_title, topic):
    """
    Generates the very first question for a new learning session.
    """
    prompt = f"""
    Based on the document titled "{document_title}" and the provided context,
    generate an introductory question about the topic "{topic}".
    The question should be clear and directly related to the initial explanation.

    Document Content:
    {context}

    End with a direct question.
    """

    try:
        model = genai.GenerativeModel(GENERATION_MODEL)
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        print(f"Error generating first question with Gemini: {e}")
        return "Question unavailable due to an error."

def evaluate_user_answer(correct_answer, user_answer):
    """
    Reuses the existing theoretical answer evaluation logic.
    """
    return evaluate_theoretical_answer(correct_answer, user_answer)

def generate_explanation_for_correct_answer(context, document_title, topic, correct_answer):
    """
    Generates an explanation for why the correct answer is correct.
    """
    prompt = f"""
    Based on the document titled "{document_title}" and the provided context,
    explain why the following answer is correct for the topic "{topic}".

    Correct Answer: "{correct_answer}"

    Document Content:
    {context}

    Provide a concise explanation.
    """
    try:
        model = genai.GenerativeModel(GENERATION_MODEL)
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        print(f"Error generating explanation for correct answer with Gemini: {e}")
        return "Explanation unavailable due to an error."