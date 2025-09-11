import os
import uuid
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from werkzeug.utils import secure_filename
from io import BytesIO
import json
import faiss
import sqlite3
from .revision_generator import generate_revision_text, generate_revision_pdf, generate_topic_summary # Ensure generate_topic_summary is imported
from .quiz_generator import generate_evenly_distributed_contexts, generate_mcq, generate_theoretical_qa

import random

# Import your modules
from .document_processor import (
    extract_text_from_document,  # Updated function name
    chunk_text,
    get_embeddings,
    save_document_data,
    load_document_data,
    init_db,
    get_all_documents_meta,
    save_quiz_to_db,
    get_quizzes_for_document,
    save_chat_history_to_db,
    get_chat_history,
    get_all_chat_sessions_meta,
    save_quiz_results_to_db
)

from .quiz_generator import retrieve_relevant_chunks, build_balanced_context, generate_mcq, generate_theoretical_qa, generate_explanation
from .evaluator import evaluate_theoretical_answer, analyze_quiz_performance, get_question_topic
from .story_generator import generate_story_explanation
from .learning_generator import (
    generate_initial_explanation,
    generate_next_question,
    generate_correct_answer,
    evaluate_user_answer as evaluate_learning_answer,
    generate_first_question,
    generate_explanation_for_correct_answer
)
from .config import document_store

from .document_processor import (
    extract_text_from_document,
    chunk_text,
    get_embeddings,
    save_document_data,
    load_document_data,
    init_db,
    get_all_documents_meta,
    save_quiz_to_db,
    get_quizzes_for_document,
    save_chat_history_to_db,
    get_chat_history,
    get_all_chat_sessions_meta,
    save_quiz_results_to_db,
    get_quiz_results_from_db,
    DB_PATH,  # Add this line
    FAISS_INDEX_DIR # You might also need this for other functions
)


import logging

from flask import Blueprint

exam_bp = Blueprint('exam', __name__)
CORS(exam_bp)
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
exam_bp.config = {}
exam_bp.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Configure logging
logging.basicConfig(level=logging.INFO)

# Database initialization will be handled in the main app
# with app.app_context():
#     init_db()

@exam_bp.route('/upload', methods=['POST'])
def upload_document():
    if 'file' not in request.files:
        return jsonify({"error": "No file part in the request"}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
    
    allowed_extensions = {'pdf', 'docx', 'pptx'}
    if not '.' in file.filename or file.filename.rsplit('.', 1)[1].lower() not in allowed_extensions:
        return jsonify({"error": "Unsupported file type. Only PDF, DOCX, PPTX allowed."} ), 400

    if file:
        filename = secure_filename(file.filename)
        existing_doc_id = None
        for doc_id, doc_info in document_store.items():
            if doc_info['original_filename'] == filename:
                existing_doc_id = doc_id
                break
        
        if existing_doc_id:
            return jsonify({"message": "Document already uploaded!", "document_id": existing_doc_id}), 200

        file_path = os.path.join(exam_bp.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        
        pages = extract_text_from_document(file_path)  # Updated function name
        if not pages:
            os.remove(file_path)
            return jsonify({"error": "Failed to extract text from document."} ), 500

        raw_text = '\n\n'.join(pages)  # For compatibility
        chunks = chunk_text(pages)
        if not chunks:
            os.remove(file_path)
            return jsonify({"error": "No meaningful text chunks could be extracted."} ), 500

        embeddings = get_embeddings(chunks)
        if embeddings is None:
            os.remove(file_path)
            return jsonify({"error": "Failed to generate embeddings. Check API key/service access or local model status."} ), 500

        faiss_index = faiss.IndexFlatL2(embeddings.shape[1])
        faiss_index.add(embeddings)

        doc_id = str(uuid.uuid4())
        save_document_data(doc_id, filename, faiss_index, chunks, pages)
        
        document_store[doc_id] = {
            "original_filename": filename,
            "pages": pages,
            "chunks": chunks,
            "faiss_index": faiss_index,
            "generated_quiz": None
        }
        
        os.remove(file_path)
        return jsonify({"message": "Document uploaded and processed successfully!", "document_id": doc_id}), 200
    
    return jsonify({"error": "Something went wrong during file upload."} ), 500



# In backend/app.py

from .quiz_generator import retrieve_relevant_chunks
from .evaluator import evaluate_theoretical_answer, generate_explanation_for_theoretical_answer


# In backend/app.py

# In backend/app.py

@exam_bp.route('/evaluate-answer', methods=['POST'])
def evaluate_answer():
    data = request.get_json()
    document_id = data.get('document_id')
    question_index = data.get('question_index')
    user_answer = data.get('user_answer')
    quiz_id = data.get('quiz_id')

    if not document_id or document_id not in document_store:
        loaded_data = load_document_data(document_id)
        if loaded_data:
            document_store[document_id] = loaded_data
        else:
            return jsonify({"error": "Document not found."} ), 404
    
    doc_info = document_store[document_id]
    quiz = doc_info.get('generated_quiz')

    if not quiz or question_index is None or not (0 <= question_index < len(quiz)):
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute('SELECT quiz_data FROM quizzes WHERE quiz_id = ?', (quiz_id,))
        row = cursor.fetchone()
        conn.close()
        if row:
            quiz = json.loads(row[0])
        else:
            return jsonify({"error": "Quiz or question not found."} ), 404

    question_data = quiz[question_index]
    
    explanation = ""
    evaluation_result = {}

    if 'options' in question_data:  # MCQ
        correct_option_letter = question_data['correct_answer'].strip()
        is_correct = user_answer.upper() == correct_option_letter
        
        correct_answer_text = question_data['options'][correct_option_letter]

        if is_correct:
            feedback = "Correct!"
        else:
            feedback = f"Incorrect. The correct answer was {correct_option_letter}."
            try:
                faiss_index = doc_info['faiss_index']
                all_chunks = doc_info['chunks']
                context_chunks = retrieve_relevant_chunks(question_data['question'], faiss_index, all_chunks, k=3)
                context_str = "\n\n".join(context_chunks)
                explanation = generate_explanation(question_data['question'], correct_answer_text, context_str)
            except Exception as e:
                print(f"Error during context retrieval or explanation generation: {e}")
                explanation = "Explanation not available due to a processing error."
            
        evaluation_result = {
            "is_correct": is_correct,
            "feedback": feedback,
            "correct_answer_text": correct_answer_text,
            "explanation": explanation
        }

    else:  # Theoretical
        correct_answer = question_data['correct_answer']
        evaluation = evaluate_theoretical_answer(correct_answer, user_answer)
        is_correct = evaluation['is_correct']
        
        # Always retrieve context for a theoretical explanation, regardless of correctness
        try:
            faiss_index = doc_info['faiss_index']
            all_chunks = doc_info['chunks']
            context_chunks = retrieve_relevant_chunks(question_data['question'], faiss_index, all_chunks, k=3)
            context_str = "\n\n".join(context_chunks)

            # Generate a response based on correctness
            if is_correct:
                explanation = "Your answer is correct! Here is a more detailed explanation."
            else:
                explanation = generate_explanation_for_theoretical_answer(question_data['question'], correct_answer, user_answer, context_str)
        except Exception as e:
            print(f"Error generating theoretical explanation: {e}")
            explanation = "Explanation not available due to a processing error."

        evaluation_result = {
            "is_correct": is_correct,
            "feedback": evaluation['feedback'],
            "correct_answer_text": correct_answer,
            "explanation": explanation
        }
    
    complete_result = {
        "question": question_data['question'],
        "userAnswer": user_answer,
        "correctAnswer": question_data.get('correct_answer'),
        "evaluation": evaluation_result,
        "is_mcq": 'options' in question_data
    }
    
    if 'quiz_results_temp' not in document_store[document_id]:
        document_store[document_id]['quiz_results_temp'] = []
    if 'user_answers_temp' not in document_store[document_id]:
        document_store[document_id]['user_answers_temp'] = []

    document_store[document_id]['quiz_results_temp'].append(complete_result)
    document_store[document_id]['user_answers_temp'].append({
        "question_index": question_index,
        "user_answer": user_answer,
        "question_text": question_data['question']
    })

    analysis = None
    if len(document_store[document_id]['quiz_results_temp']) == len(quiz):
        analysis = analyze_quiz_performance(document_store[document_id]['quiz_results_temp'])
        save_quiz_results_to_db(quiz_id, document_store[document_id]['user_answers_temp'], document_store[document_id]['quiz_results_temp'])
        
    return jsonify({"evaluation": evaluation_result, "analysis": analysis}), 200


@exam_bp.route('/evaluate-quiz', methods=['POST'])
def evaluate_quiz():
    data = request.get_json()
    quiz_id = data.get('quiz_id')
    answers = data.get('answers')

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('SELECT document_id, quiz_data FROM quizzes WHERE quiz_id = ?', (quiz_id,))
    row = cursor.fetchone()
    conn.close()

    if not row:
        return jsonify({"error": "Quiz not found."} ), 404

    document_id, quiz_data_json = row
    quiz_data = json.loads(quiz_data_json)

    if document_id not in document_store:
        loaded_data = load_document_data(document_id)
        if loaded_data:
            document_store[document_id] = loaded_data
        else:
            return jsonify({"error": "Document not found."} ), 404

    results = []
    for i, (question_data, user_answer) in enumerate(zip(quiz_data, answers)):
        is_correct = user_answer.upper() == question_data['correct_answer'].strip()
        explanation = ""
        if not is_correct:
            try:
                faiss_index = document_store[document_id]['faiss_index']
                all_chunks = document_store[document_id]['chunks']
                context_chunks = retrieve_relevant_chunks(question_data['question'], faiss_index, all_chunks, k=3)
                context_str = "\n\n".join(context_chunks)
                explanation = generate_explanation(question_data['question'], question_data['options'][question_data['correct_answer']], context_str)
            except Exception as e:
                print(f"Error during context retrieval or explanation generation: {e}")
                explanation = "Explanation not available due to a processing error."

        results.append({
            "question": question_data['question'],
            "userAnswer": user_answer,
            "correctAnswer": question_data['correct_answer'],
            "evaluation": {
                "is_correct": is_correct,
                "explanation": explanation
            }
        })

    analysis = analyze_quiz_performance(results)
    save_quiz_results_to_db(quiz_id, answers, results)

    return jsonify({"results": results, "analysis": analysis}), 200


@exam_bp.route('/generate-revision-sheet/<quiz_id>', methods=['GET'])
def generate_revision_sheet(quiz_id):
    logging.info(f"Attempting to generate revision sheet for quiz_id: {quiz_id}")
    quiz_submission_data = get_quiz_results_from_db(quiz_id)
    logging.info(f"Quiz submission data from DB: {quiz_submission_data}")

    if not quiz_submission_data:
        return jsonify({"error": "Quiz results not found. Please complete a quiz first."} ), 404

    quiz_results_list = quiz_submission_data.get('quiz_results', [])

    if not quiz_results_list:
        return jsonify({"error": "No quiz results available for this submission."} ), 404

    # Re-run analysis on the full quiz results to get weak/strong areas
    analysis = analyze_quiz_performance(quiz_results_list)
    
    # Retrieve the document ID for the revision sheet title
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('SELECT document_id FROM quizzes WHERE quiz_id = ?', (quiz_id,))
    doc_id_row = cursor.fetchone()
    conn.close()
    logging.info(f"Document ID row from quizzes table: {doc_id_row}")

    if not doc_id_row:
        return jsonify({"error": "Could not find the original document for this quiz."} ), 404

    doc_id = doc_id_row[0]
    if doc_id not in document_store:
        logging.info(f"Document ID {doc_id} not in memory, loading from disk.")
        loaded_data = load_document_data(doc_id)
        if loaded_data:
            document_store[doc_id] = loaded_data
        else:
            logging.info(f"Failed to load document data for ID {doc_id}.")
            return jsonify({"error": f"Could not load document data for ID {doc_id}."}), 404

    doc_info = document_store[doc_id]
    document_title = doc_info.get('original_filename', "Revision Sheet")
    faiss_index = doc_info.get('faiss_index')
    chunks = doc_info.get('chunks')

    if not faiss_index or not chunks:
        return jsonify({"error": "Context data (index or chunks) is missing for this document."} ), 500

    # Pass the quiz results, analysis, and context to the revision generation function
    revision_text = generate_revision_text(quiz_results_list, analysis, document_title, faiss_index, chunks)

    pdf_buffer = BytesIO()
    generate_revision_pdf(revision_text, pdf_buffer)
    pdf_buffer.seek(0)
    
    return send_file(
        pdf_buffer,
        as_attachment=True,
        download_name=f"{document_title.replace('.pdf', '').replace('.docx', '')}_Revision_Sheet.pdf",
        mimetype='application/pdf'
    )



@exam_bp.route('/quiz-results/<quiz_id>', methods=['GET'])
def get_quiz_results(quiz_id):
    try:
        results_data = get_quiz_results_from_db(quiz_id)
        if results_data:
            quiz_results_list = results_data.get('quiz_results', [])
            
            # Recalculate analysis before sending to frontend
            if quiz_results_list:
                analysis = analyze_quiz_performance(quiz_results_list)
                results_data['analysis'] = analysis
            
            return jsonify(results_data), 200
        return jsonify({"error": "Quiz results not found."} ), 404
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": f"An unexpected error occurred: {e}"} ), 500


import uuid # Ensure uuid is imported

@exam_bp.route('/story-mode/<document_id>', methods=['GET'])
def story_mode(document_id):
    if document_id not in document_store:
        loaded_data = load_document_data(document_id)
        if loaded_data:
            document_store[document_id] = loaded_data
        else:
            return jsonify({"error": "Document not found in storage."} ), 404
    
    doc_info = document_store[document_id]
    pages = doc_info['pages']
    ext = os.path.splitext(doc_info['original_filename'])[1].lower()

    if not pages:
        return jsonify({"error": "No content available for this document."} ), 500

    explanations = []
    if ext in ['.pdf', '.docx']:
        # Per page for PDF/DOCX
        for i, page_text in enumerate(pages):
            if page_text.strip():
                explanation = generate_story_explanation(page_text, f"{doc_info['original_filename']} - Page {i+1}")
                explanations.append({"section": f"Page {i+1}", "explanation": explanation})
    elif ext == '.pptx':
        # Group every 3-4 slides
        group_size = 4
        for i in range(0, len(pages), group_size):
            group_pages = pages[i:i+group_size]
            group_text = '\n\n'.join(group_pages)
            if group_text.strip():
                start_slide = i + 1
                end_slide = min(i + group_size, len(pages))
                explanation = generate_story_explanation(group_text, f"{doc_info['original_filename']} - Slides {start_slide}-{end_slide}")
                explanations.append({"section": f"Slides {start_slide}-{end_slide}", "explanation": explanation})
    else:
        return jsonify({"error": "Unsupported file type for Story Mode."} ), 400

    # New code to save to chat history
    session_id = str(uuid.uuid4())
    messages = []
    for exp in explanations:
        messages.append({
            "role": "system",
            "content": f"### {exp['section']}\n\n{exp['explanation']}"
        })
    
    save_chat_history_to_db(session_id, document_id, 'Story Mode', messages)

    # Return the explanations and the new session_id
    return jsonify({"explanations": explanations, "session_id": session_id}), 200

@exam_bp.route('/learning-mode/start', methods=['POST'])
def start_learning_session():
    data = request.get_json()
    document_ids = data.get('document_ids')
    topic = data.get('topic')

    if not document_ids or len(document_ids) == 0:
        return jsonify({"error": "No documents selected."} ), 400
    if not topic:
        return jsonify({"error": "Please provide a topic to learn about."} ), 400

    # Use only the first document for learning mode to avoid regenerating embeddings
    doc_id = document_ids[0]
    if doc_id not in document_store:
        loaded_data = load_document_data(doc_id)
        if loaded_data:
            document_store[doc_id] = loaded_data
        else:
            return jsonify({"error": f"Document with ID {doc_id} not found in storage."} ), 404
    
    doc_info = document_store[doc_id]
    combined_raw_text = '\n\n'.join(doc_info.get('pages', []))
    all_chunks_for_search = doc_info.get('chunks', [])
    faiss_index_for_search = doc_info.get('faiss_index')

    if not all_chunks_for_search or faiss_index_for_search is None:
        return jsonify({"error": "No content available for this learning session."} ), 500
    
    # Use existing FAISS index instead of regenerating embeddings
    if faiss_index_for_search.ntotal == 0:
        return jsonify({"error": "No valid FAISS index found for the selected document."} ), 500

    context_query = f"Explanation of the topic {topic} from the selected documents."
    retrieved_chunks = retrieve_relevant_chunks(
        context_query,
        faiss_index_for_search,
        all_chunks_for_search,
        k=min(20, len(all_chunks_for_search))
    )
    full_context_text = '\n\n'.join(retrieved_chunks) if retrieved_chunks else combined_raw_text[:min(len(combined_raw_text), 10000)]

    if not full_context_text:
        return jsonify({"error": "Could not find relevant information for this topic in the selected documents."} ), 500

    # Generate initial explanation
    initial_explanation = generate_initial_explanation(full_context_text, "Selected Documents", topic)

    # Generate the first question
    initial_question_text = generate_first_question(full_context_text, "Selected Documents", topic)

    # Combine explanation and question for the initial message
    initial_message_for_user = f"{initial_explanation}\n\n{initial_question_text}"

    session_id = str(uuid.uuid4())
    messages = [
        {"role": "system", "content": initial_message_for_user, "document_ids": [doc_id], "topic": topic}
    ]
    save_chat_history_to_db(session_id, document_ids[0], 'Learning Mode', messages)

    return jsonify({
        "session_id": session_id,
        "initial_message": initial_message_for_user,  # Send the combined explanation and question
        "initial_question": initial_question_text  # Send only the question separately
    }), 200

@exam_bp.route('/learning-mode/respond', methods=['POST'])
def respond_to_learning_session():
    try:
        data = request.get_json()
        print(f"Received data: {data}")  # Debug log for incoming request
        session_id = data.get('session_id')
        user_answer = data.get('user_answer')
        document_ids_in_request = data.get('document_ids', [])
        topic_in_request = data.get('topic', 'learning')

        messages = get_chat_history(session_id)
        if not messages:
            return jsonify({"error": "Session not found."} ), 404
            
        session_meta = messages[0]  # The first message contains metadata
        document_ids_in_session = session_meta.get('document_ids', document_ids_in_request or [])
        topic_in_session = session_meta.get('topic', topic_in_request or 'learning')
        
        if not document_ids_in_session:
            return jsonify({"error": "Document context lost for this session."} ), 500

        # Load document data for context
        doc_id = document_ids_in_session[0]
        if doc_id not in document_store:
            loaded_data = load_document_data(doc_id)
            if loaded_data:
                document_store[doc_id] = loaded_data
            else:
                return jsonify({"error": f"Document {doc_id} not found."} ), 404
        doc_info = document_store[doc_id]
        document_title = doc_info['original_filename']
        all_chunks = doc_info.get('chunks', [])

        # Find the last question asked
        last_question = ""
        for msg in reversed(messages):
            if msg['role'] == 'system' and msg['content'].strip().endswith('?'):
                last_question = msg['content']
                break
        if not last_question:
            return jsonify({"error": "No question found to respond to."} ), 400

        # Build context from previous system messages and ensure document content
        previous_explanations = [msg['content'] for msg in messages if msg['role'] == 'system' and not msg['content'].strip().endswith('?')]
        context_for_next = '\n\n'.join(previous_explanations)
        if not context_for_next and all_chunks:
            context_query = f"Content related to {topic_in_session} or the user answer '{user_answer}'"
            retrieved_chunks = retrieve_relevant_chunks(
                context_query,
                doc_info['faiss_index'],
                all_chunks,
                k=min(20, len(all_chunks))
            )
            context_for_next = '\n\n'.join(retrieved_chunks) if retrieved_chunks else '\n\n'.join(all_chunks[:10000])
        # Fallback to initial document content if still empty
        if not context_for_next and doc_info.get('pages'):
            context_for_next = '\n\n'.join(doc_info['pages'][:10000])

        if not context_for_next:
            print(f"⚠️ No valid context found for session {session_id}")
            return jsonify({"error": "No relevant content available to generate a response."} ), 500

        # Generate correct answer and evaluate
        correct_answer = generate_correct_answer(context_for_next, document_title, topic_in_session, last_question)
        evaluation = evaluate_learning_answer(correct_answer, user_answer)
        is_correct = evaluation['is_correct']

        classification = evaluation.get("classification", "irrelevant")
        feedback = evaluation.get("feedback", "No feedback available.")

        system_message = ""
        if classification == "correct":
            system_message = f"Correct! {feedback}"
        else:
            explanation = generate_explanation_for_correct_answer(context_for_next, document_title, topic_in_session, correct_answer)
            if classification == "incorrect":
                system_message = f"That's not quite right. {feedback}\n\nThe correct answer is: \"{correct_answer}\"\n\nExplanation: {explanation}"
            else: # irrelevant or error
                system_message = f"Your answer seems to be off-topic. The correct answer is: \"{correct_answer}\"\n\nExplanation: {explanation}"

        # Generate next question for all cases
        next_question = generate_next_question(context_for_next, document_title, topic_in_session, user_answer, is_correct, correct_answer)
        system_message += f"\n\n---\n\nHere is your next question:\n\n{next_question}"
        
        messages.append({"role": "user", "content": user_answer})
        messages.append({"role": "system", "content": system_message})
        save_chat_history_to_db(session_id, document_ids_in_session[0], 'Learning Mode', messages)

        return jsonify({
            "evaluation": evaluation,
            "next_message": system_message
        }), 200
    except Exception as e:
        print(f"🔥 Unexpected error in /learning-mode/respond: {e}")
        import traceback; traceback.print_exc()
        return jsonify({"error": "An error occurred. Please try again."} ), 500
    
@exam_bp.route('/documents', methods=['GET'])
def get_documents():
    docs = get_all_documents_meta()
    return jsonify(docs), 200

@exam_bp.route('/document/<document_id>/quizzes', methods=['GET'])
def get_document_quizzes(document_id):
    quizzes = get_quizzes_for_document(document_id)
    return jsonify(quizzes), 200

@exam_bp.route('/quiz/<quiz_id>', methods=['GET'])
def get_single_quiz(quiz_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('SELECT quiz_data FROM quizzes WHERE quiz_id = ?', (quiz_id,))
    row = cursor.fetchone()
    conn.close()
    if row:
        return jsonify(json.loads(row[0])), 200
    return jsonify({"error": "Quiz not found."} ), 404

# In backend/app.py

# ... (all existing code) ...

@exam_bp.route('/chat-sessions', methods=['GET'])
def get_all_chat_sessions():
    sessions = get_all_chat_sessions_meta()
    return jsonify(sessions), 200

@exam_bp.route('/chat-sessions/<chat_id>', methods=['DELETE'])
def delete_chat_session(chat_id):
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Check if the session exists
        cursor.execute("SELECT chat_id FROM chat_sessions WHERE chat_id = ?", (chat_id,))
        session_exists = cursor.fetchone()
        
        if not session_exists:
            conn.close()
            return jsonify({"error": "Chat session not found."}), 404
        
        # Delete the chat session from the chat_sessions table
        cursor.execute("DELETE FROM chat_sessions WHERE chat_id = ?", (chat_id,))
        
        # Also delete the associated quiz data if it's a quiz session
        cursor.execute("DELETE FROM quizzes WHERE quiz_id = ?", (chat_id,))
        
        conn.commit()
        conn.close()
        
        # Check if it was also a quiz session and remove from in-memory store if needed
        # This part is optional but good practice
        for doc_id, doc_info in document_store.items():
            if 'generated_quiz' in doc_info and doc_info['generated_quiz'] is not None and doc_info['generated_quiz'][0].get('quiz_id') == chat_id:
                doc_info['generated_quiz'] = None
                
        return jsonify({"message": "Chat session deleted successfully."} ), 200
        
    except Exception as e:
        logging.error(f"Error deleting chat session {chat_id}: {e}")
        return jsonify({"error": "An error occurred while deleting the session."} ), 500

...

@exam_bp.route('/chat-history', methods=['POST'])
def save_chat_messages():
    data = request.get_json()
    chat_id = data.get('chat_id')
    document_id_from_request = data.get('document_id')
    quiz_type_from_request = data.get('quiz_type')
    messages = data.get('messages')

    if not chat_id or not messages:
        return jsonify({"error": "Missing chat_id or messages."} ), 400

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Try to get metadata from quizzes table first
    cursor.execute('SELECT document_id, quiz_type FROM quizzes WHERE quiz_id = ?', (chat_id,))
    row = cursor.fetchone()
    conn.close()

    if row:
        document_id, quiz_type = row
    else:
        # Fallback to metadata from the request if not found in the quizzes table
        document_id = document_id_from_request
        quiz_type = quiz_type_from_request
        
        if not document_id or not quiz_type:
             return jsonify({"error": "Quiz/document metadata not found and not provided in request."} ), 404

    save_chat_history_to_db(chat_id, document_id, quiz_type, messages)
    return jsonify({"message": "Chat history saved successfully!"}), 200

@exam_bp.route('/chat-history/<chat_id>', methods=['GET'])
def get_chat_messages(chat_id):
    messages = get_chat_history(chat_id)
    return jsonify(messages), 200

@exam_bp.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "running", "message": "Backend is healthy"}), 200

# Blueprint does not run standalone
# print("Registered routes:", app.url_map)
# if __name__ == '__main__':
#     app.run(debug=True, port=5001)

# @app.before_request
# def log_before_request():
#     print(f"\n➓ Incoming {request.method} {request.path}")
#     print("Active routes:", app.url_map)

# ------------------------------------------------------------------------------------------------------
# ------------------------------------------------------------------------------------------------------
# ------------------------------------------------------------------------------------------------------
# ------------------------------------------------------------------------------------------------------


# In backend/app.py

from .quiz_generator import generate_evenly_distributed_contexts, generate_mcq, generate_theoretical_qa
# Ensure _strip_noise_lines is imported as well
from .quiz_generator import _strip_noise_lines 


# In backend/app.py

from .quiz_generator import generate_evenly_distributed_contexts, generate_mcq, generate_theoretical_qa, _strip_noise_lines 

def clean_initial_text(text: str) -> str:
    """Conservatively removes administrative text from the start of a document."""
    lines = text.splitlines()
    clean_lines = []

    # Define administrative keywords that indicate metadata blocks
    admin_keywords = ['course code', 'course id', 'batch', 'roll no', 'semester', 'section']

    # Only remove lines that are clearly administrative metadata
    # Don't remove entire blocks just because one line matches
    for line in lines:
        line_lower = line.lower().strip()
        # Only skip lines that are pure administrative metadata
        if (any(keyword in line_lower for keyword in admin_keywords) and
            len(line_lower.split()) <= 5):  # Only skip short administrative lines
            continue
        clean_lines.append(line)

    return "\n".join(clean_lines).strip()

@exam_bp.route("/generate-quiz", methods=["POST"])
def generate_quiz():
    try:
        print(f"DEBUG: Request headers: {dict(request.headers)}")
        print(f"DEBUG: Request method: {request.method}")
        print(f"DEBUG: Request data: {request.get_data()}")
        data = request.json
        print(f"DEBUG: Parsed JSON data: {data}")
        if data is None:
            print("DEBUG: request.json is None")
            return jsonify({"error": "Invalid JSON data"}), 400
        document_ids = data.get("document_ids")
        print(f"DEBUG: document_ids = {document_ids}")
        if not document_ids:
            print("DEBUG: No document_ids provided")
            return jsonify({"error": "Missing document_ids"}), 400
        doc_id = document_ids[0]
        print(f"DEBUG: Using doc_id = {doc_id}")

        num_questions = int(data.get("num_questions", 5))
        difficulty = data.get("difficulty", "Medium")
        qtype = data.get("quiz_type", "MCQ")

        if not doc_id or doc_id not in document_store:
            loaded_data = load_document_data(doc_id)
            if loaded_data:
                document_store[doc_id] = loaded_data
            else:
                return jsonify({"error": f"Invalid or missing document ID: {doc_id}"}), 400

        document_pages = document_store[doc_id]["pages"]
        raw_text = "\n\n".join(document_pages)

        print(f"DEBUG: Raw text length: {len(raw_text)}")
        print(f"DEBUG: Raw text preview: {raw_text[:500]}...")

        filtered_initial_text = clean_initial_text(raw_text)
        print(f"DEBUG: After clean_initial_text length: {len(filtered_initial_text)}")
        print(f"DEBUG: After clean_initial_text preview: {filtered_initial_text[:500]}...")

        cleaned_raw_text = _strip_noise_lines(filtered_initial_text)
        print(f"DEBUG: After _strip_noise_lines length: {len(cleaned_raw_text)}")
        print(f"DEBUG: After _strip_noise_lines preview: {cleaned_raw_text[:500]}...")

        # Split cleaned text into logical pages for chunking
        if cleaned_raw_text.strip():
            # Split by double newlines to create logical "pages"
            logical_pages = [page.strip() for page in cleaned_raw_text.split('\n\n') if page.strip()]
            if not logical_pages:
                logical_pages = [cleaned_raw_text]  # fallback if no double newlines
        else:
            logical_pages = []

        print(f"DEBUG: Number of logical pages: {len(logical_pages)}")

        chunks = chunk_text(logical_pages)
        print(f"DEBUG: Number of chunks created: {len(chunks)}")

        if not chunks:
            print("DEBUG: No chunks created - investigating further...")
            print(f"DEBUG: logical_pages length: {len(logical_pages)}")
            print(f"DEBUG: logical_pages content: {logical_pages[:3] if logical_pages else 'Empty'}")
            return jsonify({"error": "No content found for this document after filtering."}), 400

        questions = []
        
        # --- NEW HYBRID APPROACH ---
        
        # 1. Generate questions from the most relevant chunks (e.g., 50% of the total questions)
        num_relevant_questions = num_questions // 2
        if num_relevant_questions > 0:
            query = "Generate quiz questions on the most important topics in the document."
            relevant_chunks = retrieve_relevant_chunks(query, document_store[doc_id]["faiss_index"], chunks, k=num_relevant_questions)
            
            for chunk in relevant_chunks:
                if qtype.lower() == "mcq":
                    q_list = generate_mcq(chunk, 1, difficulty)
                else:
                    q_list = generate_theoretical_qa(chunk, 1, difficulty)
                if q_list:
                    questions.extend(q_list)

        # 2. Generate the remaining questions from evenly distributed chunks
        num_distributed_questions = num_questions - len(questions)
        if num_distributed_questions > 0:
            distributed_contexts = generate_evenly_distributed_contexts(chunks, num_distributed_questions)

            for context in distributed_contexts:
                if qtype.lower() == "mcq":
                    q_list = generate_mcq(context, 1, difficulty)
                else:
                    q_list = generate_theoretical_qa(context, 1, difficulty)
                if q_list:
                    questions.extend(q_list)
        
        # Final check to ensure we have the requested number of questions
        if len(questions) < num_questions:
            print("Warning: Could not generate the requested number of questions. Using all available questions.")
        
        # Shuffle the final list of questions to mix up the relevant and distributed questions
        random.shuffle(questions)
        questions = questions[:num_questions] # Truncate to the requested number of questions

        if not questions:
            return jsonify({"error": "No valid questions could be generated."} ), 500

        quiz_id = str(uuid.uuid4())
        save_quiz_to_db(quiz_id, doc_id, qtype, num_questions, questions)
        
        document_store[doc_id]['generated_quiz'] = questions

        return jsonify({"quiz": questions, "quiz_id": quiz_id})

    except Exception as e:
        import traceback
        traceback.print_exc()
        print("Error in /generate-quiz:", e)
        return jsonify({"error": str(e)}), 500
    
# In backend/app.py

def is_administrative_question(question_text: str) -> bool:
    """
    Checks if a question is likely administrative or curriculum-based.
    """
    admin_patterns = [
        'learning objectives', 'course outcomes', 'curriculum', 
        'skill development', 'course objectives', 'upon completion',
        'professional core'
    ]
    return any(pattern in question_text.lower() for pattern in admin_patterns)