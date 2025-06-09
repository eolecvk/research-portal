import os
from dotenv import load_dotenv

# Load environment variables from .env file at module import time
load_dotenv()

# --- API Keys ---
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")

# --- Supabase S3 Configuration ---
SUPABASE_S3_ENDPOINT_URL = os.getenv("SUPABASE_S3_ENDPOINT_URL")
SUPABASE_S3_REGION_NAME = os.getenv("SUPABASE_S3_REGION_NAME")
SUPABASE_S3_ACCESS_ID = os.getenv("SUPABASE_S3_ACCESS_ID")
SUPABASE_S3_ACCESS_KEY = os.getenv("SUPABASE_S3_ACCESS_KEY")
SUPABASE_S3_BUCKET_NAME = os.getenv("SUPABASE_S3_BUCKET_NAME")


# --- LLM and Embedding Models ---
DEFAULT_EMBEDDING_MODEL = "gemini-embedding-exp-03-07"  # As per gen_embed.py
DEFAULT_LLM_MODEL = 'gemini-2.5-flash-preview-05-20'    # As per run_cli.py

# --- Pinecone Constants ---
EMBED_DIM = 3072  # As per vector_db.py
INDEX_NAME = "example-index"  # As per vector_db.py
NAMESPACE = "example-namespace"  # As per vector_db.py
PINECONE_CLOUD = 'aws'  # Default from vector_db.py
PINECONE_REGION = 'us-east-1'  # Default from vector_db.py
PINECONE_BATCH_SIZE = 100  # Default from vector_db.py

# --- Data Directories ---
REPORTS_JSON_DIR = "/home/eolus/workspace/research-portal/data/reports/JSON"
EMBEDDINGS_REPORTS_DIR = "/home/eolus/workspace/research-portal/data/embeddings/reports"
EMBEDDINGS_QUESTIONS_DIR = "/home/eolus/workspace/research-portal/data/embeddings/questions"
QUESTIONS_JSON_PATH = "/home/eolus/workspace/research-portal/data/questions/questions_v0.json"

# --- Tool-specific configurations ---
ALLOWED_REPORT_FILES = [
    "company_report_HPG.json",
    "company_report_VHC.json",
    "economics_non_corporate_report.json",
    "strategy_noncorporate_report.json"
]

# --- Validation ---
if not GEMINI_API_KEY:
    print("WARNING: GEMINI_API_KEY not set in .env. LLM operations may fail.")
if not PINECONE_API_KEY:
    print("WARNING: PINECONE_API_KEY not set in .env. Pinecone operations may fail.")
if not SUPABASE_S3_ENDPOINT_URL or not SUPABASE_S3_ACCESS_ID or not SUPABASE_S3_ACCESS_KEY:
    print("WARNING: Supabase S3 credentials not fully set in .env. S3 operations may fail.")
