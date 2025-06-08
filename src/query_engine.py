# src/query_engine.py

import os
import datetime
import logging
from google import genai
from google.genai import types

# Import configurations and API key from src/config.py
from src.config import (
    GEMINI_API_KEY,
    DEFAULT_LLM_MODEL,
    REPORTS_JSON_DIR
)

# Configure logging for this module
logger = logging.getLogger(__name__)

# Initialize LLM Client (ensure API key is available)
if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY environment variable not set. Please set it in your .env file.")
LLM_CLIENT = genai.Client(api_key=GEMINI_API_KEY)


# --- Helper Functions (Tools) ---

def _get_current_date() -> str:
    """Returns the current date spelled out, like 'June 16th 2025'.
    This is a helper function for the LLM tool.
    """
    now = datetime.datetime.now()
    day = now.day
    if 11 <= day <= 13:
        suffix = "th"
    else:
        suffix = {1: "st", 2: "nd", 3: "rd"}.get(day % 10, "th")
    return now.strftime(f"%B {day}{suffix} %Y")


def _list_reports() -> list[str]:
    """List the names of the reports available
    Only allows reading files from a pre-defined directory (REPORTS_JSON_DIR).
    This is a helper function for the LLM tool.
    """
    try:
        return os.listdir(REPORTS_JSON_DIR)
    except FileNotFoundError:
        logger.error(f"Reports directory not found: {REPORTS_JSON_DIR}")
        return []
    except Exception as e:
        logger.error(f"Error listing reports in {REPORTS_JSON_DIR}: {e}", exc_info=True)
        return []


def _read_file_content(filename: str) -> str:
    """Reads the content of a specified file and returns it as a string.
    Only allows reading files from a pre-defined directory (REPORTS_JSON_DIR).
    This is a helper function for the LLM tool.
    """
    filepath = os.path.join(REPORTS_JSON_DIR, os.path.basename(filename))
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        return content
    except FileNotFoundError:
        return f"Error: File '{filename}' not found in the allowed directory."
    except IOError as e:
        return f"Error reading file '{filename}': {e}"


def generate_ai_response(conversation_history: list[dict], model: str = DEFAULT_LLM_MODEL) -> str:
    """
    Generates an AI response based on the entire conversation history using the Gemini model.
    Utilizes predefined tools for current date and file reading.
    """
    system_instructions = """
# Context

You are a **professional and helpful financial analyst AI**. Your primary goal is to **accurately and concisely answer financial questions** posed by other analysts.

* If a question is **ambiguous or lacks necessary detail**, you must **ask clarifying questions** to understand the user's precise intent.
* If you **lack specific information or data** required to provide a complete answer, you must **clearly state what information is missing**.

# Tone

Maintain a **professional, concise, and highly informative** tone. Your responses should be direct and to the point.

# Response Format

Your response should either be a simple text sentence, paragraph or be valid Markdown format.
Use bold to highlight the key facts in case you need to produce a longer answer.
When the answer contains information from reports it should be formatted like this:

<Your short, direct answer sentence or paragraph, directly addressing the user's query.>

*Sources:*  
+ *<Name of Report 1 (without file extension)>*
+ *<Name of Report 2 (without file extension)>*
... (List all relevant reports)


# Tools

You have access to the following specialized tools to assist with your analysis:

### 1. Get Current Date

* **Tool:** `_get_current_date()`
* **Purpose:** To obtain the current calendar date.
* **When to Use:** This tool is **mandatory** whenever the user's query is relative to the current date (e.g., "today", "this week", "last quarter") or requires time-sensitive information to infer the relevant period for your answer.

### 2. Access Reports

* **Tool:** `_list_reports()`
* **Purpose:** To discover available report files related to companies, economic context, or strategic context.
* **When to Use:** Use this function as the **first first step** when you need to find specific financial data or analysis from internal reports.
* **Usage Flow:**
    1.  **Call `_list_reports()`**: This will return a list of all available report filenames.
    2.  **Identify Relevant Reports**: Examine the returned filenames to determine which reports are most likely to contain the information needed for the user's query.
    3.  **Read Report Content**: Use the `_read_file_content(file)` method to access the full content of a specific report. Replace `file` with the exact filename obtained from `_list_reports()`.

* **Expected Report Filename Patterns:**
    * **Company Reports:** `"company_report_<company_name>_<report_date>.json"`
        * *Example:* `"company_report_VHC_2025-06-07.json"`
    * **Economic Reports:** `"economics_non_corporate_report_<report_date>.json"`
        * *Example:* `"economics_non_corporate_report_2025-06-05.json"`
    * **Strategic Reports:** `"strategy_noncorporate_report_<report_date>.json"`
        * *Example:* `"strategy_noncorporate_report_2025-06-01.json"`
"""

    try:
        logger.info(f"Incoming conversation history length: {len(conversation_history)}")
        if conversation_history:
            logger.debug(f"Last message in history: {conversation_history[-1]}")

        response = LLM_CLIENT.models.generate_content(
            model=model,
            contents=conversation_history,
            config=types.GenerateContentConfig(
                tools=[_get_current_date, _list_reports, _read_file_content],
                system_instruction=system_instructions,
                max_output_tokens=2048
            )
        )

        # Log the raw response object to see its structure
        logger.info(f"Raw Gemini API response: {response}")

        # Access .text directly. If it's empty, check candidates for other types of content.
        if response.text:
            logger.info(f"Gemini API generated text response: {response.text}")
            return response.text
        else:
            # If no text, check if there are candidates and if they have content parts
            # This is more robust than directly accessing .parts on the response object
            if response.candidates and response.candidates[0].content and response.candidates[0].content.parts:
                for part in response.candidates[0].content.parts:
                    if part.function_call:
                        logger.warning(f"Gemini model returned a tool call instead of text: {part.function_call}")
                        # In a more advanced scenario, you'd execute the tool here
                        # and send the result back to the model in a follow-up turn.
                        # For now, return a generic message if no text is present.
                        return "I need to perform an action with my tools to answer that, but I can't provide a direct text response for it yet. Can you please rephrase?"
                    else:
                        logger.warning(f"Gemini model returned non-text content: {part}")
            else:
                logger.warning("Gemini model returned an empty response with no text or identifiable content.")
            return "I couldn't generate a text response for that. Can you please rephrase or provide more details?"

    except Exception as e:
        logger.error(f"Error generating AI response: {e}", exc_info=True)
        raise # Re-raise for calling context to handle
