import os
import json
import time
import logging
from google import genai
from src.config import (
    GEMINI_API_KEY,
    DEFAULT_EMBEDDING_MODEL,
    REPORTS_JSON_DIR,
    EMBEDDINGS_REPORTS_DIR,
    EMBEDDINGS_QUESTIONS_DIR,
    QUESTIONS_JSON_PATH
)

# Configure logging for this module
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Initialize GenAI client once
if GEMINI_API_KEY:
    try:
        genai_client = genai.Client(api_key=GEMINI_API_KEY)
    except Exception as e:
        logger.error(f"Failed to initialize Google GenAI client: {e}")
        genai_client = None
else:
    logger.warning("GEMINI_API_KEY not set. Embedding generation will fail.")
    genai_client = None


def get_embedding(text: str, model: str = DEFAULT_EMBEDDING_MODEL) -> list[float]:
    """
    Generates an embedding for a given text string using Google's Generative AI.
    """
    if not genai_client:
        raise ValueError("Google GenAI client not initialized. GEMINI_API_KEY might be missing or invalid.")

    try:
        response = genai_client.models.embed_content(
            model=model,
            contents=text
        )
        return response.embeddings[0].values
    except Exception as e:
        logger.error(f"Error getting embedding for text: '{text}'. Model: '{model}'. Error: {e}", exc_info=True)
        raise # Re-raise the exception for proper error handling upstream


def generate_report_embeddings(source_dir: str = REPORTS_JSON_DIR, save_dir: str = EMBEDDINGS_REPORTS_DIR):
    """
    Generates embeddings for paragraphs extracted from JSON reports and saves them.
    """
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)
        logger.info(f"Created save directory: {save_dir}")

    vectors = []
    logger.info(f"Starting to generate embeddings for reports from: {source_dir}")

    for fname in os.listdir(source_dir):
        if not fname.endswith(".json"):
            continue

        file_path = os.path.join(source_dir, fname)
        report_name = fname[:-5] # remove .json

        with open(file_path, "r", encoding='utf-8') as f:
            try:
                data = json.load(f)
            except json.JSONDecodeError as e:
                logger.warning(f"Error decoding JSON from {fname}: {e}. Skipping file.")
                continue

        report_date = data.get("report_date")
        content_list = data.get("content", [])

        for i, paragraph in enumerate(content_list):
            _id = f"{report_name}-{i}"
            output_fname = f"{_id}.json"
            outpath = os.path.join(save_dir, output_fname)

            if os.path.exists(outpath):
                logger.debug(f"Embedding for {_id} already exists. Skipping.")
                continue

            paragraph_text = paragraph.get("paragraph", "")
            paragraph_title = paragraph.get("title", "")

            if not paragraph_text.strip():
                logger.debug(f"Skipping empty paragraph in {report_name} (index {i}).")
                continue

            try:
                embedding = get_embedding(paragraph_text)
            except Exception as e:
                logger.error(f"Failed to get embedding for paragraph {_id}: {e}. Skipping.", exc_info=True)
                continue

            vector = {
                "id": _id,
                "values": embedding,
                "metadata": {
                    "report_date": report_date,
                    "report_name": report_name,
                    "paragraph_title": paragraph_title,
                    "paragraph_text": paragraph_text # Storing text for context, be mindful of size
                }
            }
            vectors.append(vector)

            # Save as JSON immediately after generating
            try:
                with open(outpath, "w", encoding='utf-8') as f_out:
                    json.dump(vector, f_out, indent=2)
                logger.info(f"Generated and saved embedding for: {_id}")
            except IOError as e:
                logger.error(f"Failed to save embedding for {_id} to {outpath}: {e}", exc_info=True)

            # Apply a small delay to respect API rate limits (adjust as needed)
            time.sleep(6) # Consider adaptive rate limiting or batch processing

    logger.info(f"Finished generating embeddings for reports. Total generated: {len(vectors)}")
    return vectors


def generate_question_embeddings(questions_path: str = QUESTIONS_JSON_PATH, save_dir: str = EMBEDDINGS_QUESTIONS_DIR):
    """
    Generates embeddings for predefined questions and saves them.
    """
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)
        logger.info(f"Created save directory: {save_dir}")

    try:
        with open(questions_path, "r", encoding='utf-8') as f:
            questions = json.load(f)
    except FileNotFoundError:
        logger.error(f"Questions file not found: {questions_path}")
        return
    except json.JSONDecodeError as e:
        logger.error(f"Error decoding questions JSON from {questions_path}: {e}")
        return

    logger.info(f"Starting to generate embeddings for {len(questions)} questions from: {questions_path}")

    for i, question in enumerate(questions):
        output_fname = f"q{i}.json"
        outpath = os.path.join(save_dir, output_fname)

        if os.path.exists(outpath):
            logger.debug(f"Embedding for question {i} already exists. Skipping.")
            continue

        try:
            embedding = get_embedding(question)
        except Exception as e:
            logger.error(f"Failed to get embedding for question '{question}' (index {i}): {e}. Skipping.", exc_info=True)
            continue

        query_data = {
            "values": embedding,
            "text": question
        }

        try:
            with open(outpath, 'w', encoding='utf-8') as out_f:
                json.dump(query_data, out_f, indent=2)
            logger.info(f"Generated and saved embedding for question {i}")
        except IOError as e:
            logger.error(f"Failed to save embedding for question {i} to {outpath}: {e}", exc_info=True)

        time.sleep(6) # Apply delay

    logger.info(f"Finished generating embeddings for questions.")


if __name__ == "__main__":
    # Example usage for CLI:
    # python src/gen_embed.py reports
    # python src/gen_embed.py questions
    import argparse

    parser = argparse.ArgumentParser(description="Generate embeddings for reports or questions.")
    parser.add_argument("type", choices=["reports", "questions", "test"],
                        help="Specify 'reports' to generate report embeddings, 'questions' for question embeddings, or 'test' for a quick test.")
    args = parser.parse_args()

    if args.type == "reports":
        generate_report_embeddings()
    elif args.type == "questions":
        generate_question_embeddings()
    elif args.type == "test":
        # Quick test function (similar to your original gen_embedding_test)
        try:
            input_string = "How does alphafold work?"
            embedding_vector = get_embedding(input_string)
            logger.info(f"Embedding for '{input_string}':")
            logger.info(f"First 10 dimensions: {embedding_vector[:10]}")
            logger.info(f"Embedding dimension: {len(embedding_vector)}")
        except ValueError as ve:
            logger.error(f"Configuration Error: {ve}")
        except Exception as ex:
            logger.error(f"An unexpected error occurred during execution: {ex}")