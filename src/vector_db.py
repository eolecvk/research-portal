import os
import json
import logging
from pinecone import Pinecone, ServerlessSpec
from tqdm import tqdm # Assuming tqdm is installed
from src.config import (
    PINECONE_API_KEY,
    INDEX_NAME,
    NAMESPACE, # Although not used directly in current ops, good to keep in config
    EMBED_DIM,
    PINECONE_CLOUD,
    PINECONE_REGION,
    PINECONE_BATCH_SIZE,
    EMBEDDINGS_REPORTS_DIR
)

# Configure logging for this module
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Initialize Pinecone client once
if PINECONE_API_KEY:
    try:
        pc = Pinecone(api_key=PINECONE_API_KEY)
    except Exception as e:
        logger.error(f"Failed to initialize Pinecone client: {e}")
        pc = None
else:
    logger.warning("PINECONE_API_KEY not set. Pinecone operations will fail.")
    pc = None

def get_or_create_pinecone_index(
    pinecone_client: Pinecone,
    index_name: str = INDEX_NAME,
    dimension: int = EMBED_DIM,
    metric: str = "cosine",
    cloud: str = PINECONE_CLOUD,
    region: str = PINECONE_REGION
):
    """
    Checks if a Pinecone index exists and creates it if it doesn't.
    """
    if not pinecone_client:
        raise ValueError("Pinecone client not initialized.")

    logger.info(f"Checking if index '{index_name}' exists...")
    if not pinecone_client.has_index(index_name):
        logger.info(f"Index '{index_name}' not found. Creating a new index...")
        spec = ServerlessSpec(cloud=cloud, region=region)
        pinecone_client.create_index(
            name=index_name,
            spec=spec,
            dimension=dimension,
            metric=metric
        )
        logger.info(f"Index '{index_name}' created successfully.")
    else:
        logger.info(f"Index '{index_name}' already exists.")

    index = pinecone_client.Index(name=index_name)
    logger.info(f"Index stats for '{index_name}': {index.describe_index_stats()}")
    return index

def load_embedding_vectors(data_dir: str = EMBEDDINGS_REPORTS_DIR) -> list:
    """
    Loads embedding vectors from JSON files in a specified directory.
    """
    vectors = []
    if not os.path.exists(data_dir):
        logger.error(f"Data directory not found: {data_dir}")
        return []

    logger.info(f"Loading vectors from: {data_dir}")
    for filename in os.listdir(data_dir):
        if filename.endswith(".json"):
            file_path = os.path.join(data_dir, filename)
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    # Basic validation for Pinecone vector format
                    if "id" in data and "values" in data and isinstance(data["values"], list):
                        vectors.append(data)
                    else:
                        logger.warning(f"Skipping malformed vector file: '{filename}'. Missing 'id' or 'values' key, or 'values' is not a list.")
            except json.JSONDecodeError:
                logger.warning(f"Skipping file '{filename}' due to a JSON decoding error.")
            except Exception as e:
                logger.warning(f"An unexpected error occurred with file '{filename}': {e}")

    logger.info(f"Successfully loaded {len(vectors)} embedding files.")
    return vectors

def upsert_vectors_to_pinecone(index, vectors: list, batch_size: int = PINECONE_BATCH_SIZE):
    """
    Upserts a list of vectors to the Pinecone index in batches.
    """
    if not vectors:
        logger.info("No vectors to upsert.")
        return

    logger.info(f"Starting upsert of {len(vectors)} vectors to index '{index.name}'...")
    try:
        for start in tqdm(range(0, len(vectors), batch_size), desc="Upserting records batch"):
            batch = vectors[start:start+batch_size]
            index.upsert(vectors=batch)
        logger.info(f"Successfully upserted {len(vectors)} vectors.")
    except Exception as e:
        logger.error(f"Error during vector upsert: {e}", exc_info=True)
        raise

def query_pinecone_index(index, query_vector: list, top_k: int = 5, include_metadata: bool = True):
    """
    Queries the Pinecone index with a given query vector.
    """
    if not index:
        raise ValueError("Pinecone index not provided or not initialized.")
    if not query_vector:
        raise ValueError("Query vector cannot be empty.")

    logger.info(f"Querying index '{index.name}' for top {top_k} results...")
    try:
        query_results = index.query(
            vector=query_vector,
            top_k=top_k,
            include_metadata=include_metadata
        )
        logger.info("Query successful.")
        return query_results
    except Exception as e:
        logger.error(f"Error during Pinecone query: {e}", exc_info=True)
        raise

if __name__ == "__main__":
    # Example usage for CLI:
    # python src/vector_db.py init
    # python src/vector_db.py upsert
    # python src/vector_db.py query <path_to_question_json>

    import argparse
    from src.gen_embed import get_embedding # Needed for test query

    parser = argparse.ArgumentParser(description="Manage Pinecone vector database.")
    parser.add_argument("action", choices=["init", "upsert", "query"],
                        help="Specify 'init' to create/get index, 'upsert' to load and upload vectors, or 'query' to test a query.")
    parser.add_argument("--query_file", type=str,
                        help="Path to a JSON file containing a question embedding (for 'query' action).")
    args = parser.parse_args()

    if not pc:
        logger.error("Pinecone client not available. Exiting.")
        sys.exit(1) # Exit if client didn't initialize

    pinecone_index = None
    try:
        if args.action == "init":
            pinecone_index = get_or_create_pinecone_index(pc)
            logger.info("Index initialization complete.")
        elif args.action == "upsert":
            pinecone_index = get_or_create_pinecone_index(pc) # Ensure index exists
            vectors_to_upload = load_embedding_vectors()
            upsert_vectors_to_pinecone(pinecone_index, vectors_to_upload)
            logger.info("Vector upsert complete.")
        elif args.action == "query":
            if not args.query_file:
                parser.error("--query_file is required for 'query' action.")

            pinecone_index = get_or_create_pinecone_index(pc) # Ensure index exists
            try:
                with open(args.query_file, 'r', encoding='utf-8') as f:
                    query_data = json.load(f)
                    question_txt = query_data.get('text', 'N/A')
                    question_vec = query_data.get('values')

                if not question_vec:
                    logger.error(f"Could not find 'values' (embedding) in {args.query_file}")
                    sys.exit(1)

                logger.info(f"Querying with question: {question_txt}")
                query_results = query_pinecone_index(pinecone_index, question_vec, top_k=2)
                print(f"Results for '{question_txt}':")
                print(json.dumps(query_results.to_dict(), indent=2)) # .to_dict() to pretty print Pinecone results

            except FileNotFoundError:
                logger.error(f"Query file not found: {args.query_file}")
            except json.JSONDecodeError:
                logger.error(f"Error decoding JSON from query file: {args.query_file}")
            except Exception as e:
                logger.error(f"An error occurred during query execution: {e}", exc_info=True)
        else:
            parser.print_help()

    except ValueError as ve:
        logger.error(f"Configuration Error: {ve}")
    except Exception as ex:
        logger.error(f"An unexpected error occurred: {ex}", exc_info=True)