import os
import json
from pathlib import Path
from dotenv import load_dotenv
from pinecone import Pinecone, ServerlessSpec

import pinecone
# print pinecone version number
print("Your pinecone-client version:", pinecone.__version__)

def main():

    # Load environment variables from .env file
    load_dotenv()
    PINECONE_KEY = os.getenv("PINECONE_KEY")
    INDEX_NAME = "example-index"
    NAMESPACE = "example-namespace"

    if not PINECONE_KEY:
        raise ValueError("PINECONE_KEY not found in environment variables.")

    # Initialize Pinecone client
    pc = Pinecone(api_key=PINECONE_KEY)

    #print(pc.__dict__)
    import inspect # Import the inspect module

    print(type(pc))
    print("--- Methods of the Pinecone client (pc) using inspect ---")
    for name, method in inspect.getmembers(pc, inspect.ismethod):
        print(f"- {name}")


if __name__ == "__main__":
    main()
