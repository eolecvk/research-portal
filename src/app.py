# main Flask app file

import logging
from flask import Flask, request, jsonify, send_from_directory
from src.query_engine import generate_ai_response
from src.config import GEMINI_API_KEY
from src.download_data import download_if_needed

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = Flask(__name__, static_folder='static')

if not GEMINI_API_KEY:
    logger.error("GEMINI_API_KEY environment variable not set. The API will not function correctly.")

@app.route('/')
def index():
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/api/query', methods=['POST'])
def handle_query():
    data = request.get_json()
    conversation_history = data.get('history')

    if not conversation_history:
        logger.warning("Received query request with no conversation history.")
        return jsonify({"error": "No conversation history provided"}), 400

    if conversation_history and conversation_history[-1]['role'] == 'user':
        logger.info(f"Received user query: '{conversation_history[-1]['parts'][0]['text']}'")
    else:
        logger.info("Received query request with history (last message not a user query).")

    try:
        response_text = generate_ai_response(conversation_history)
        logger.info("Successfully generated AI response.")
        return jsonify({"response": response_text})
    except ValueError as ve:
        logger.error(f"Configuration error during AI response generation: {ve}", exc_info=True)
        return jsonify({"error": f"Configuration error: {ve}. Please check server setup."}), 500
    except Exception as e:
        logger.error(f"An unexpected error occurred during AI response generation: {e}", exc_info=True)
        return jsonify({"error": f"An internal server error occurred: {e}"}), 500

def main():
    logger.info("Checking data availability...")
    download_if_needed()

    logger.info("Starting Flask backend server...")
    app.run(debug=True, host='0.0.0.0', port=5000)

if __name__ == '__main__':
    main()
