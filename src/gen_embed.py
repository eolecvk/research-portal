import os
from dotenv import load_dotenv
from google import genai

def get_embedding(text: str, model: str = "gemini-embedding-exp-03-07") -> list[float]:
    """
    Generates an embedding for a given text string using Google's Generative AI.

    This method uses the 'from google import genai' import style, while ensuring
    compatibility with the current 'google-generativeai' library API to avoid
    the 'AttributeError: module 'google.generativeai' has no attribute 'Client''.

    Args:
        text (str): The input string to embed.
        model (str): The name of the embedding model to use.
                     Defaults to "gemini-embedding-exp-03-07" as per original request.
                     Note: "models/embedding-001" is a commonly stable alternative.

    Returns:
        list[float]: A list of floats representing the embedding vector.

    Raises:
        ValueError: If the GEMINI_API_KEY environment variable is not set.
        Exception: If there's an error during the API call.
    """
    # Ensure environment variables are loaded
    load_dotenv()
    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        raise ValueError("GEMINI_API_KEY environment variable not set. Please set it in your .env file.")

    client = genai.Client(api_key=api_key) 

    try:
        # Call the embed_content function directly from the 'genai' module.
        # This replaces 'client.models.embed_content()' which is not available.
        response = client.models.embed_content(
                model=model,
                contents=text
                ) 
        # The embedding result is returned as a dictionary, with the vector
        # under the 'embedding' key.
        return response.embeddings[0].values

    except Exception as e:
        print(f"Error getting embedding for text: '{text}'. Error: {e}")
        print(f"Please check your model name ('{model}') and API key, and network connectivity.")
        raise # Re-raise the exception for proper error handling upstream


def gen_embedding_test():

    # Example usage:
    try:
        input_string = "How does alphafold work?"
        embedding_vector = get_embedding(input_string)

        print(f"Embedding for '{input_string}':")
        print(f"First 10 dimensions: {embedding_vector[:10]}")
        print(f"Embedding dimension: {len(embedding_vector)}")

    except ValueError as ve:
        print(f"Configuration Error: {ve}")
    except Exception as ex:
        print(f"An unexpected error occurred during execution: {ex}")


def gen_embedding_reports():

        import json

        vectors = []

        source_dir = "/home/eolus/workspace/research-portal/data/reports/JSON/"
        save_dir = "/home/eolus/workspace/research-portal/data/embeddings/reports"
        for fname in os.listdir(source_dir):
            if not fname.endswith(".json"):
                continue  # Skip non-JSON files

            file_path = os.path.join(source_dir, fname)
            report_name = fname[:-5]
            with open(file_path, "r") as f:
                try:
                    data = json.load(f)
                except json.JSONDecodeError as e:
                    print(f"  - Error decoding {fname}: {e}")
                    continue

            report_date = data.get("report_date")
            content_list = data.get("content", [])

            for i, paragraph in enumerate(content_list):

                _id = f"{report_name}-{i}"
                fname = f"{_id}.json"
                if fname in os.listdir(save_dir):
                    continue
                paragraph_text = paragraph.get("paragraph", "")
                paragraph_title = paragraph.get("title", "")
                embedding = get_embedding(paragraph_text)

                import time
                time.sleep(6)

                vector = {
                        "id": _id,
                        "values": embedding,
                        "metadata": {
                            "report_date": report_date,
                            "report_name": report_name,
                            "paragraph_name" : paragraph_title,
                            "paragraph_text" : paragraph_text
                        }
                    }

                vectors.append(vector)

                # save as json
                outpath = os.path.join(save_dir, fname)
                with open(outpath, "w") as f:
                    json.dump(vector, f, indent=2)

        return vectors


def gen_embedding_questions():
    import json
    with open("/home/eolus/workspace/research-portal/data/questions/questions_v0.json") as f:
        questions = json.load(f)
    for i, question in enumerate(questions):
        embedding = get_embedding(question)
        query = {
            "values" : embedding,
            "text" : question
        }

        with open(f"/home/eolus/workspace/research-portal/data/embeddings/questions/q{i}.json", 'w') as out_f:
            json.dump(query, out_f, indent=2)
    


if __name__ == "__main__":

    gen_embedding_reports()


                
