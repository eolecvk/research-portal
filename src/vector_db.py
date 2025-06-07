import os
import json
from pathlib import Path
from dotenv import load_dotenv
from pinecone import Pinecone, ServerlessSpec

# --- 1. Configuration & Initialization ---

# Load environment variables from .env file
load_dotenv()
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
if not PINECONE_API_KEY:
    raise ValueError("PINECONE_API_KEY not found in environment variables.")

# Define constants
INDEX_NAME = "example-index"
NAMESPACE = "example-namespace"
EMBED_DIM = 3072

# Define REPORT_DIR relative to this script's location
REPORT_DIR = "/home/eolus/workspace/research-portal/data/reports/JSON"

# Initialize Pinecone client
pc = Pinecone(api_key=PINECONE_API_KEY)


def get_index(
    pinecone_client: Pinecone,
    index_name: str,
    dimension: int,
    metric: str = "cosine",
    cloud: str = 'aws',
    region: str = 'us-east-1'
):
    """
    Checks if a Pinecone index exists and creates it if it doesn't.

    Args:
        pinecone_client: An initialized Pinecone client instance.
        index_name: The name of the index to create.
        dimension: The embedding dimension for the index.
        metric: The distance metric for the index.
        cloud: The cloud provider for the ServerlessSpec.
        region: The cloud region for the ServerlessSpec.
    """
    print(f"Checking if index '{index_name}' exists...")
    if not pinecone_client.has_index(index_name):
        print(f"Index '{index_name}' not found. Creating a new index...")
        spec = ServerlessSpec(cloud=cloud, region=region)
        pinecone_client.create_index(
            name=index_name,
            spec=spec,
            dimension=dimension,
            metric=metric
        )
        print(f"Index '{index_name}' created successfully.")
    else:
        print(f"Index '{index_name}' already exists.")

    # View index stats of our new, empty index
    index = pc.Index(name=index_name)
    index.describe_index_stats()

    return index



def load_vectors(data_dir="/home/eolus/workspace/research-portal/data/embeddings/reports"):
    vectors = []
    # return the list
    for filename in os.listdir(data_dir):
        # Check if the file is a JSON file
        if filename.endswith(".json"):
            # Create the full path to the file
            file_path = os.path.join(data_dir, filename)
            
            try:
                # Open the file, load its JSON content, and append to the list
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    vectors.append(data)
            except json.JSONDecodeError:
                print(f"Warning: Skipping file '{filename}' due to a JSON decoding error.")
            except Exception as e:
                print(f"Warning: An unexpected error occurred with file '{filename}': {e}")

    print(f"Successfully loaded {len(vectors)} files.")
    return vectors

def upsert_vectors(index, vectors, batch_size = 100):
    from tqdm import tqdm

    for start in tqdm(range(0, len(vectors), batch_size), "Upserting records batch"):
        batch = vectors[start:start+batch_size]
        index.upsert(vectors=batch)



def query(index, query):
    #xq = create_embedding(query)
    # Retrieve from Pinecone
    # Get relevant contexts (including the questions)
    #query_results = index.query(vector=xq, top_k=2, include_metadata=True)
    #query_results
    pass


# --- 3. Main Execution Block ---

if __name__ == "__main__":

    index = get_index(
        pinecone_client=pc,
        index_name=INDEX_NAME,
        dimension=EMBED_DIM
    )


    #vectors = load_vectors()
    #upsert_vectors(index, vectors)

    # Test query

    # Load a question
    fpath = "/home/eolus/workspace/research-portal/data/embeddings/questions/q1.json"
    import json
    with open(fpath, 'r') as f:
        query = json.load(f)
        question_txt = query['text']
        question_vec = query['values']
        query_results = index.query(vector=question_vec, top_k=2, include_metadata=True)

        print(question_txt)
        print(query_results)


