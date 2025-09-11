import os
from dotenv import load_dotenv
import google.generativeai as genai
from sentence_transformers import SentenceTransformer # NEW IMPORT

load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY not found in environment variables. Please set it in the .env file.")

genai.configure(api_key=GEMINI_API_KEY)

# Define models
LOCAL_EMBEDDING_MODEL_NAME = 'all-MiniLM-L6-v2' # New: Name for the local model
# Keep the Gemini embedding model name in case of fallback or future use
GEMINI_EMBEDDING_MODEL_API = 'models/embedding-001'
GENERATION_MODEL = 'gemini-2.5-flash' # Or 'gemini-1.0-pro'

# Initialize local embedding model globally
# It will download the model the first time this code runs and has internet access.
local_embedding_model_instance = None
try:
    print(f"Loading local embedding model: {LOCAL_EMBEDDING_MODEL_NAME}...")
    local_embedding_model_instance = SentenceTransformer(LOCAL_EMBEDDING_MODEL_NAME)
    print("Local embedding model loaded successfully.")
except Exception as e:
    print(f"ERROR: Could not load local embedding model {LOCAL_EMBEDDING_MODEL_NAME}: {e}")
    print("Falling back to Gemini embedding API if needed. Ensure internet connection for first download.")

document_store = {}