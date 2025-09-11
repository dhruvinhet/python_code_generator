# backend/evaluator.py

import google.generativeai as genai
from .config import GENERATION_MODEL
import json

def evaluate_theoretical_answer(correct_answer, user_answer):
    """
    Evaluates a user's theoretical answer against the correct answer using Gemini.

    Returns a dictionary with classification ('correct', 'incorrect', 'irrelevant'),
    a similarity score, and detailed feedback.
    """
    prompt = f"""
    Analyze the user's answer in relation to the correct answer and classify it.

    Correct Answer: "{correct_answer}"
    User Answer: "{user_answer}"

    1.  **Classification**: Categorize the user's answer into one of three categories:
        *   **Correct**: If the user's answer is semantically similar or identical to the correct answer.
        *   **Incorrect**: If the user's answer is on-topic but factually wrong.
        *   **Irrelevant**: If the user's answer is off-topic or does not attempt to answer the question.

    2.  **Similarity Score**: Provide a numerical score from 0.0 (completely different) to 1.0 (identical meaning).

    3.  **Feedback**: Give a concise explanation for your classification. If the answer is incorrect, explain why.

    Format your response strictly as follows:
    Classification: [Correct/Incorrect/Irrelevant]
    Similarity Score: [score from 0.0 to 1.0]
    Feedback: [Brief explanation]
    """

    try:
        model = genai.GenerativeModel(GENERATION_MODEL)
        response = model.generate_content(prompt)
        evaluation_text = response.text.strip()

        classification = "irrelevant"
        score = 0.0
        feedback = "Could not evaluate answer."

        for line in evaluation_text.split('\n'):
            if line.startswith("Classification:"):
                classification = line[len("Classification:"):].strip().lower()
            elif line.startswith("Similarity Score:"):
                try:
                    score = float(line[len("Similarity Score:"):].strip())
                except ValueError:
                    pass
            elif line.startswith("Feedback:"):
                feedback = line[len("Feedback:"):].strip()

        is_correct = classification == "correct"

        return {
            "is_correct": is_correct,
            "classification": classification,
            "similarity_score": score,
            "feedback": feedback
        }
    except Exception as e:
        print(f"Error evaluating answer: {e}")
        return {
            "is_correct": False,
            "classification": "error",
            "similarity_score": 0.0,
            "feedback": "An error occurred during evaluation."
        }


def get_question_topic(question):
    """
    Uses Gemini to extract a concise topic from a given question.
    """
    prompt = f"""
    Given the following quiz question, extract the single, most relevant key concept or topic from it.
    Return only the topic name, without any extra text or formatting.
    
    Question: {question}
    Topic: 
    """
    try:
        model = genai.GenerativeModel(GENERATION_MODEL)
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        print(f"Error extracting topic: {e}")
        return "Unknown Topic"

def analyze_quiz_performance(quiz_results):
    """
    Analyzes quiz results to identify weak and strong areas based on topics.
    """
    total_questions = len(quiz_results)
    correct_answers = [q for q in quiz_results if q['evaluation']['is_correct']]
    incorrect_answers = [q for q in quiz_results if not q['evaluation']['is_correct']]
    
    analysis = {
        "overall_summary": f"You answered {len(correct_answers)} out of {total_questions} questions correctly.",
        "weak_areas": [],
        "strong_areas": []
    }
    
    # Extract topics for incorrect answers
    if len(incorrect_answers) > 0:
        analysis["weak_areas"] = [get_question_topic(q['question']) for q in incorrect_answers]
        # Remove duplicates
        analysis["weak_areas"] = list(dict.fromkeys(analysis["weak_areas"]))

    # Extract topics for correct answers
    if len(correct_answers) > 0:
        analysis["strong_areas"] = [get_question_topic(q['question']) for q in correct_answers]
        # Remove duplicates
        analysis["strong_areas"] = list(dict.fromkeys(analysis["strong_areas"]))

    if not analysis["weak_areas"]:
        analysis["weak_areas"] = ["None, you performed very well!"]

    if not analysis["strong_areas"]:
        analysis["strong_areas"] = ["You may need to focus on core concepts."]

    return analysis


def generate_explanation(question, correct_answer_text, context):
    """Generates a detailed explanation for why an answer is correct."""
    is_context_present = bool(context and len(context.strip()) > 50) # Check if context is meaningful
    
    if is_context_present:
        prompt = f"""
        You are an AI assistant tasked with explaining the correct answer to a multiple-choice question based on a provided context.
        
        Question: {question}
        Correct Answer: {correct_answer_text}
        
        CONTEXT START
        {context}
        CONTEXT END
        
        Provide a concise explanation (1-2 sentences) of why the correct answer is right, strictly using information from the context. If the information is not present, you must state that it is not available in the context and provide a general explanation.
        """
    else:
        prompt = f"""
        You are an AI assistant tasked with explaining the correct answer to a multiple-choice question. The document provided does not contain the answer.
        
        Question: {question}
        Correct Answer: {correct_answer_text}
        
        Provide a concise explanation (1-2 sentences) of why the correct answer is right, based on your general knowledge.
        """
    
    try:
        model = genai.GenerativeModel(GENERATION_MODEL)
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        print(f"Error generating explanation: {e}")
        return "Explanation not available due to a generation error."
    
# In backend/evaluator.py

import google.generativeai as genai
from .config import GENERATION_MODEL


def generate_explanation_for_theoretical_answer(question: str, correct_answer: str, user_answer: str, context: str) -> str:
    """Generates an explanation for a theoretical question, providing the correct answer."""
    prompt = f"""
    You are an AI assistant providing feedback on a theoretical quiz question. The user's answer was incorrect.
    
    Question: {question}
    Correct Answer: {correct_answer}
    User's Answer: {user_answer}
    
    CONTEXT START
    {context}
    CONTEXT END
    
    Based on the provided context, provide a clear, concise explanation (1-2 sentences) of why the Correct Answer is correct. You should also briefly address why the user's answer was incorrect or insufficient.
    """
    try:
        model = genai.GenerativeModel(GENERATION_MODEL)
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        print(f"Error generating theoretical answer explanation: {e}")
        return "Explanation not available due to a generation error."