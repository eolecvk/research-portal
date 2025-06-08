import os
from dotenv import load_dotenv

# Load environment variables from .env file at module import time
load_dotenv()

# --- API Keys ---
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")

# --- LLM and Embedding Models ---
DEFAULT_EMBEDDING_MODEL = "gemini-embedding-exp-03-07" # As per gen_embed.py
DEFAULT_LLM_MODEL = 'gemini-2.5-flash-preview-05-20' # As per run_cli.py

# --- Pinecone Constants ---
EMBED_DIM = 3072 # As per vector_db.py
INDEX_NAME = "example-index" # As per vector_db.py
NAMESPACE = "example-namespace" # As per vector_db.py
PINECONE_CLOUD = 'aws' # Default from vector_db.py
PINECONE_REGION = 'us-east-1' # Default from vector_db.py
PINECONE_BATCH_SIZE = 100 # Default from vector_db.py

# --- Data Directories (relative to the project root, assuming .env is at root) ---
# It's better to make these relative to the project root rather than hardcoded absolute paths.
# For demonstration, I'll keep the absolute paths if they were crucial for the original setup,
# but ideally, these should be configurable or derived from project root.

# If your 'data' directory is at the project root, you could do:
# PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# DATA_DIR = os.path.join(PROJECT_ROOT, "data")
# REPORTS_JSON_DIR = os.path.join(DATA_DIR, "reports", "JSON")
# EMBEDDINGS_REPORTS_DIR = os.path.join(DATA_DIR, "embeddings", "reports")
# EMBEDDINGS_QUESTIONS_DIR = os.path.join(DATA_DIR, "embeddings", "questions")
# QUESTIONS_JSON_PATH = os.path.join(DATA_DIR, "questions", "questions_v0.json")

# Keeping original hardcoded paths for now, assuming they are accessible to the system
# but recommending a more robust pathing strategy in the repo structure section.
REPORTS_JSON_DIR = "/home/eolus/workspace/research-portal/data/reports/JSON"
EMBEDDINGS_REPORTS_DIR = "/home/eolus/workspace/research-portal/data/embeddings/reports"
EMBEDDINGS_QUESTIONS_DIR = "/home/eolus/workspace/research-portal/data/embeddings/questions"
QUESTIONS_JSON_PATH = "/home/eolus/workspace/research-portal/data/questions/questions_v0.json"

# --- Tool-specific configurations ---
# List of allowed files for the read_file_content tool
# This should ideally be dynamically loaded or managed if the list is large or changes often.
ALLOWED_REPORT_FILES = [
    "company_report_HPG.json",
    "company_report_VHC.json",
    "economics_non_corporate_report.json",
    "strategy_noncorporate_report.json" # assuming it ends with .json
]

# --- Validation ---
if not GEMINI_API_KEY:
    print("WARNING: GEMINI_API_KEY not set in .env. LLM operations may fail.")
if not PINECONE_API_KEY:
    print("WARNING: PINECONE_API_KEY not set in .env. Pinecone operations may fail.")