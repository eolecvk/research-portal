import os
from dotenv import load_dotenv
from google import genai
from google.genai import types
import datetime
import json # You might need this if you process JSON files within this module

# Load environment variables once at the module level
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY environment variable not set. Please set it in your .env file.")

LLM_CLIENT = genai.Client(api_key=GEMINI_API_KEY)
DEFAULT_MODEL = 'gemini-2.5-flash-preview-05-20'
ALLOWED_FILES_DIRECTORY = '/home/eolus/workspace/research-portal/data/reports/JSON'


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
    Only allows reading files from a pre-defined directory.
    This is a helper function for the LLM tool.
    """    
    return os.listdir(ALLOWED_FILES_DIRECTORY)


def _read_file_content(filename: str) -> str:
    """Reads the content of a specified file and returns it as a string.
    Only allows reading files from a pre-defined directory.
    This is a helper function for the LLM tool.
    """
    filepath = os.path.join(ALLOWED_FILES_DIRECTORY, os.path.basename(filename))
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        return content
    except FileNotFoundError:
        return f"Error: File '{filename}' not found in the allowed directory."
    except IOError as e:
        return f"Error reading file '{filename}': {e}"

def generate_ai_response(user_query: str, model: str = DEFAULT_MODEL) -> str:
    """
    Generates an AI response based on the user query using the Gemini model.
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

Your response must follow this format:

<Your short, direct answer sentence or paragraph, directly addressing the user's query.>

---

**Sources:**
* <Name of Report 1 (without file extension)>
* <Name of Report 2 (without file extension)>
* ... (List all relevant reports)


# Tools

You have access to the following specialized tools to assist with your analysis:

### 1. Get Current Date

* **Tool:** `_get_current_date()`
* **Purpose:** To obtain the current calendar date.
* **When to Use:** This tool is **mandatory** whenever the user's query is relative to the current date (e.g., "today", "this week", "last quarter") or requires time-sensitive information to infer the relevant period for your answer.

### 2. Access Reports

* **Tool:** `_list_reports()`
* **Purpose:** To discover available report files related to companies, economic context, or strategic context.
* **When to Use:** Use this function as the **first step** when you need to find specific financial data or analysis from internal reports.
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
        response = LLM_CLIENT.models.generate_content(
            model=model,
            contents=user_query,
            config=types.GenerateContentConfig(
                tools=[_get_current_date, _list_reports, _read_file_content],
                system_instruction=system_instructions,
                max_output_tokens=500
            )
        )
        return response.text
    except Exception as e:
        print(f"Error generating AI response: {e}")
        raise # Re-raise for calling context to handle