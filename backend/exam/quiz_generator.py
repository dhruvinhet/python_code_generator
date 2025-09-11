# In backend/quiz_generator.py

import google.generativeai as genai
import numpy as np
import json
import re
from .config import GENERATION_MODEL, local_embedding_model_instance, GEMINI_EMBEDDING_MODEL_API, LOCAL_EMBEDDING_MODEL_NAME

MAX_CONTEXT_CHARS = 30000

# In backend/quiz_generator.py

# In backend/quiz_generator.py

NOISE_PATTERNS = [
    r'^\s*page\s*\d+\s*(of\s*\d+)?\s*$',        # page numbers only
    r'^\s*\d{1,2}\s*/\s*\d{1,2}\s*/\s*\d{2,4}\s*$', # dates as standalone lines only
    r'^\s*table of contents?\s*$',  # table of contents line only
    r'^\s*(contact|email|phone):\s*.*$',  # contact info lines only
    r'^\s*copyright\s*.*$',  # copyright lines only
    r'^\s*disclaimer\s*.*$',  # disclaimer lines only
]
_noise_regexes = [re.compile(pat, re.IGNORECASE) for pat in NOISE_PATTERNS]

def _strip_noise_lines(text: str) -> str:
    """Remove admin/metadata-like lines so questions focus on learnable content."""
    print(f"DEBUG: _strip_noise_lines input length: {len(text)}")
    print(f"DEBUG: _strip_noise_lines input preview: {text[:200]}...")
    
    # TEMPORARILY DISABLED - return input unchanged for debugging
    print("DEBUG: _strip_noise_lines DISABLED - returning input unchanged")
    return text.strip()
    
    cleaned_lines = []
    removed_lines = []
    total_lines = 0
    
    for line in text.splitlines():
        total_lines += 1
        line_stripped = line.strip()
        if not line_stripped:
            continue
        
        # Check if line matches any noise pattern
        line_matches_noise = False
        matched_pattern = None
        for i, rx in enumerate(_noise_regexes):
            if rx.search(line_stripped):
                line_matches_noise = True
                matched_pattern = NOISE_PATTERNS[i]
                removed_lines.append(f"'{line_stripped}' (matched: {matched_pattern})")
                break
        
        if not line_matches_noise:
            cleaned_lines.append(line)
    
    print(f"DEBUG: _strip_noise_lines processed {total_lines} total lines")
    print(f"DEBUG: _strip_noise_lines kept {len(cleaned_lines)} lines")
    print(f"DEBUG: _strip_noise_lines removed {len(removed_lines)} lines")
    if removed_lines:
        print(f"DEBUG: Sample removed lines: {removed_lines[:5]}")
    
    cleaned = "\n".join(cleaned_lines)
    # squeeze super long whitespace
    result = re.sub(r'\n{3,}', '\n\n', cleaned).strip()
    print(f"DEBUG: _strip_noise_lines output length: {len(result)}")
    print(f"DEBUG: _strip_noise_lines output preview: {result[:200]}...")
    return result

def build_balanced_context(chunks, max_chars: int = MAX_CONTEXT_CHARS) -> str:
    """
    Build a context that samples across the entire document (not just the start),
    staying within the char budget. This ensures coverage of the whole doc.
    """
    if not chunks:
        return ""
    total = len(chunks)
    step = max(1, total // 50)
    selected = []
    char_count = 0
    for i in range(0, total, step):
        c = chunks[i]
        if not c:
            continue
        if char_count + len(c) > max_chars:
            break
        selected.append(c)
        char_count += len(c)
    if char_count < max_chars:
        for i in range(0, total):
            c = chunks[i]
            if not c:
                continue
            if char_count + len(c) > max_chars:
                break
            selected.append(c)
            char_count += len(c)
    context = "\n\n".join(selected)[:max_chars]
    return _strip_noise_lines(context)

def _extract_json_from_text(raw: str):
    """Extract JSON from a raw LLM response (handles code-fences, stray text)."""
    raw = raw.strip()
    fenced = re.search(r"```json\s*(.*?)\s*```", raw, flags=re.DOTALL | re.IGNORECASE)
    if fenced:
        raw = fenced.group(1).strip()
    else:
        fenced2 = re.search(r"```\s*(.*?)\s*```", raw, flags=re.DOTALL)
        if fenced2:
            raw = fenced2.group(1).strip()
    start = raw.find('[')
    end = raw.rfind(']')
    if start != -1 and end != -1 and end > start:
        raw = raw[start:end+1]
    return json.loads(raw)

def _safe_llm_json(prompt: str):
    """Call Gemini and return parsed JSON or raise an error."""
    model = genai.GenerativeModel(GENERATION_MODEL)
    resp = model.generate_content(prompt)
    text = (getattr(resp, "text", None) or "").strip()
    
    fenced = re.search(r"```json\s*(.*?)\s*```", text, flags=re.DOTALL | re.IGNORECASE)
    if fenced:
        raw_json_text = fenced.group(1).strip()
    else:
        raw_json_text = text

    cleaned_json_text = re.sub(r',\s*\}', '}', raw_json_text)
    cleaned_json_text = re.sub(r',\s*\]', ']', cleaned_json_text)
    cleaned_json_text = re.sub(r'\s+', ' ', cleaned_json_text)
    
    try:
        return json.loads(cleaned_json_text)
    except json.JSONDecodeError as e:
        print(f"JSON parsing failed: {e}")
        print(f"Malformed LLM output:\n{text}")
        print(f"Cleaned JSON text:\n{cleaned_json_text}")
        return []
    except Exception as e:
        print(f"An unexpected error occurred during JSON parsing: {e}")
        return []

def retrieve_relevant_chunks(query, faiss_index, chunks, k=5):
    """
    Retrieves the top-k most relevant chunks from the FAISS index based on a query.
    """
    try:
        if local_embedding_model_instance:
            print(f"Using local embedding model for query: {LOCAL_EMBEDDING_MODEL_NAME}")
            query_embedding = local_embedding_model_instance.encode([query], convert_to_numpy=True)[0]
        else:
            print(f"Using Gemini embedding model for query: {GEMINI_EMBEDDING_MODEL_API}")
            query_embedding_response = genai.embed_content(
                model=GEMINI_EMBEDDING_MODEL_API,
                content=query,
                task_type="RETRIEVAL_QUERY"
            )
            query_embedding = np.array(query_embedding_response['embedding']).astype('float32')
        
        query_embedding = query_embedding.reshape(1, -1)
        
        if faiss_index is None or faiss_index.ntotal == 0:
            print("FAISS index is empty or not built correctly for retrieval.")
            return []

        distances, indices = faiss_index.search(query_embedding, k)
        
        relevant_chunks = [chunks[i] for i in indices[0] if i < len(chunks)]
        return relevant_chunks
    except Exception as e:
        print(f"Error retrieving chunks: {e}")
        return []

# In backend/quiz_generator.py


def generate_explanation(question, correct_answer, context):
    """Generates an explanation for a correct answer using the provided context."""
    model = genai.GenerativeModel(GENERATION_MODEL)
    prompt = f"""Given the following context, explain why the correct answer to the question is what it is.

    Context: {context}
    Question: {question}
    Correct Answer: {correct_answer}

    Explanation:"""
    response = model.generate_content(prompt)
    return response.text


# In backend/quiz_generator.py

# In backend/quiz_generator.py
quiz_so_far = []    

# In backend/quiz_generator.py

def generate_mcq(context: str, num_questions: int = 1, difficulty: str = "Medium", topics=None, existing_questions: list = []):
    """
    Generates a single MCQ based on a specific, narrow context.
    """
    context = (context or "")[:MAX_CONTEXT_CHARS]
    topic_hint = ""
    if topics:
        topic_hint = f'Target topics (distribute coverage if possible): {", ".join(topics)}.'

    difficulty_instructions = ""
    if difficulty == "Easy":
        difficulty_instructions = """
        Difficulty: EASY.
        - Questions should be direct and ask for factual recall from a single sentence or phrase in the text.
        - Avoid complex concepts or inferential questions.
        - Options should be straightforward, with one clearly correct answer and three clearly incorrect distractors.
        """
    elif difficulty == "Medium":
        difficulty_instructions = """
        Difficulty: MEDIUM.
        - Questions should require understanding and synthesis of information from a few sentences or a small paragraph.
        - Test for comprehension of core concepts, not just rote memorization.
        - Options should be plausible, requiring careful reading to distinguish the correct answer.
        """
    elif difficulty == "Hard":
        difficulty_instructions = """
        Difficulty: HARD.
        - Questions should be inferential, analytical, or comparative, requiring the user to connect ideas from multiple sections of the document.
        - Focus on synthesis of complex topics or understanding implicit relationships.
        - Distractors should be highly plausible and relate to concepts in the text, but be subtly incorrect.
        """

    system_rules = f"""
    You are generating a single high-quality {difficulty} MCQ question from the provided academic content.
    Ignore and avoid creating questions from metadata like university names, grading, marks, syllabus, course codes, etc.

    Rules:
    - Create exactly 1 question.
    - The question must be based on factual/conceptual content from the context (not admin info).
    - Provide 4 distinct, plausible options labeled A, B, C, D (no duplicates; no "All of the above"/"None of the above").
    - Only one correct option. The "correct_answer" must be a single letter: A, B, C, or D.
    {topic_hint}
    {difficulty_instructions}

    Return ONLY a JSON array with this schema:
    [
      {{
        "question": "string",
        "options": {{"A":"string","B":"string","C":"string","D":"string"}},
        "correct_answer": "A" | "B" | "C" | "D"
      }}
    ]
    """
    prompt = f"""{system_rules}

    CONTEXT START
    {context}
    CONTEXT END
    """
    try:
        items = _safe_llm_json(prompt)
        valid = []
        for q in items:
            question = (q.get("question") or "").strip()
            # Perform semantic similarity check here
            if not is_semantically_similar(question, existing_questions, local_embedding_model_instance):
                valid.append(q)
            else:
                print(f"Skipping semantically similar question: {question}")
        return valid[:num_questions]
    except Exception as e:
        print("MCQ generation error:", e)
        return []

def generate_theoretical_qa(context: str, num_questions: int = 1, difficulty: str = "Medium", topics=None, existing_questions: list = []):
    """
    Generates a single short-answer theoretical question and answer at a specified difficulty.
    """
    context = (context or "")[:MAX_CONTEXT_CHARS]
    topic_hint = ""
    if topics:
        topic_hint = f'Target topics (distribute coverage if possible): {", ".join(topics)}.'

    difficulty_instructions = ""
    if difficulty == "Easy":
        difficulty_instructions = """
        Difficulty: EASY.
        - Questions should be direct, short, and test for basic recall of facts or definitions.
        - Answers should be simple, single-sentence responses.
        """
    elif difficulty == "Medium":
        difficulty_instructions = """
        Difficulty: MEDIUM.
        - Questions should require explaining a concept or a process.
        - Answers should be concise but comprehensive, requiring a few sentences.
        """
    elif difficulty == "Hard":
        difficulty_instructions = """
        Difficulty: HARD.
        - Questions should be open-ended, requiring synthesis, comparison, or analysis of multiple concepts.
        - Answers should be detailed, well-structured paragraphs.
        """
        
    system_rules = f"""
    You are generating a single short-answer theoretical question and answer at {difficulty} difficulty.
    Ignore admin/metadata (university, grading, marks, syllabus, codes). Focus on learnable content.

    Rules:
    - Create exactly 1 question-answer pair.
    - The question must be clear, specific, and grounded in the context (no trivia about admin/credits).
    - The answer must be concise, correct, and directly supported by the context.
    {topic_hint}
    {difficulty_instructions}

    Return ONLY a JSON array with this schema:
    [
      {{"question":"string","correct_answer":"string"}},
      ...
    ]
    """
    prompt = f"""{system_rules}

    CONTEXT START
    {context}
    CONTEXT END
    """
    try:
        items = _safe_llm_json(prompt)
        valid = []
        seen_questions = set(q.lower() for q in existing_questions)
        for qa in items:
            if not isinstance(qa, dict):
                continue
            q = (qa.get("question") or "").strip()
            a = (qa.get("correct_answer") or "").strip()
            if not q or not a:
                continue
            if q.lower() in seen_questions:
                continue
            valid.append({"question": q, "correct_answer": a})
            seen_questions.add(q.lower())
        return valid[:num_questions]
    except Exception as e:
        print("Theoretical QA generation error:", e)
        return []
    
    

def is_administrative_chunk(text: str, aggressive: bool = True) -> bool:
    """
    Checks if a chunk of text is likely administrative or meta-data.
    The 'aggressive' flag controls the strictness of the filter.
    """
    text_lower = text.lower()
    admin_keywords = [
        'learning objectives', 'course outcomes', 'assessment', 'syllabus',
        'prerequisites', 'grading', 'course code', 'evaluation',
        'skill development', 'curriculum', 'lecture notes',
        'module', 'unit', 'chapter', 'section', 'introduction', 'about this document',
        'overview', 'course description', 'course format', 'expected outcomes',
        'course policies', 'disclaimer', 'confidentiality', 'copyright'
    ]

    keyword_count = sum(1 for keyword in admin_keywords if keyword in text_lower)
    
    # Aggressive mode filters if two or more keywords are present.
    # Lenient mode filters only if one or more keywords are present.
    threshold = 2 if aggressive else 1
    
    return keyword_count >= threshold

def _strip_noise_lines(text: str, aggressive_filter: bool = True) -> str:
    """
    Removes admin/metadata-like lines and entire administrative chunks.
    This function combines line-level and chunk-level filtering.
    """
    print(f"DEBUG: _strip_noise_lines (second function) called with aggressive_filter={aggressive_filter}")
    print(f"DEBUG: _strip_noise_lines (second function) input length: {len(text)}")
    
    # TEMPORARILY DISABLED - return input unchanged for debugging
    print("DEBUG: _strip_noise_lines (second function) DISABLED - returning input unchanged")
    return text.strip()
    
    cleaned_lines = []
    
    # First, filter line by line using existing regex patterns
    for line in text.splitlines():
        line_stripped = line.strip()
        if not line_stripped:
            continue
        if any(rx.search(line_stripped) for rx in _noise_regexes):
            continue
        cleaned_lines.append(line)
        
    cleaned_text = "\n".join(cleaned_lines).strip()
    
    # Second, check if the resulting chunk is administrative
    if is_administrative_chunk(cleaned_text, aggressive=aggressive_filter):
        return "" # Return an empty string if the whole chunk is administrative
    
    # Squeeze super long whitespace
    return re.sub(r'\n{3,}', '\n\n', cleaned_text)
    
    # Squeeze super long whitespace
    return re.sub(r'\n{3,}', '\n\n', cleaned_text)

# In backend/quiz_generator.py

def generate_evenly_distributed_contexts(chunks, num_questions):
    """
    Divides the document's chunks into N sections and cleans them to ensure even content coverage.
    Performs a second, less aggressive pass if not enough contexts are generated.
    """
    if not chunks:
        return []

    if len(chunks) < num_questions:
        num_questions = len(chunks)

    chunk_per_question = max(1, len(chunks) // num_questions)
    
    contexts = []
    
    # First Pass: Aggressive Filtering
    for i in range(num_questions):
        start_index = i * chunk_per_question
        end_index = start_index + chunk_per_question
        if i == num_questions - 1:
            end_index = len(chunks)
        
        context_chunks = chunks[start_index:end_index]
        full_context = "\n\n".join(context_chunks)
        cleaned_context = _strip_noise_lines(full_context, aggressive_filter=True)
        
        if cleaned_context:
            contexts.append(cleaned_context)

    # Second Pass: Lenient Filtering
    if len(contexts) < num_questions:
        print("Not enough contexts generated from aggressive filtering. Trying a more lenient pass.")
        contexts = [] # Reset contexts
        for i in range(num_questions):
            start_index = i * chunk_per_question
            end_index = start_index + chunk_per_question
            if i == num_questions - 1:
                end_index = len(chunks)
            
            context_chunks = chunks[start_index:end_index]
            full_context = "\n\n".join(context_chunks)
            cleaned_context = _strip_noise_lines(full_context, aggressive_filter=False)
            
            if cleaned_context:
                contexts.append(cleaned_context)
    
    # Third Pass: Use raw chunks as a last resort to ensure the count is met.
    if len(contexts) < num_questions:
        print("Falling back to unfiltered content to meet the requested question count.")
        contexts = [] # Reset contexts
        for i in range(num_questions):
            start_index = i * chunk_per_question
            end_index = start_index + chunk_per_question
            if i == num_questions - 1:
                end_index = len(chunks)
            
            context_chunks = chunks[start_index:end_index]
            full_context = "\n\n".join(context_chunks)
            
            if full_context:
                contexts.append(full_context)
    
    return contexts


def is_semantically_similar(new_question, existing_questions, embedding_model, threshold=0.9):
    """Checks if a new question is semantically too similar to any existing questions."""
    if not existing_questions:
        return False
    
    # Generate embeddings for the new question and all existing questions
    question_embeddings = embedding_model.encode([new_question] + existing_questions, convert_to_numpy=True)
    new_q_embedding = question_embeddings[0]
    existing_q_embeddings = question_embeddings[1:]
    
    # Calculate cosine similarity between the new question and all existing questions
    similarities = np.dot(existing_q_embeddings, new_q_embedding) / (np.linalg.norm(existing_q_embeddings, axis=1) * np.linalg.norm(new_q_embedding))
    
    return np.any(similarities > threshold)