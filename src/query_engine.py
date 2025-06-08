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

    You are a helpful financial analyst tasked with answering other analysts questions.
    If the question is not clear, ask for clarification about what the user needs to know.
    If you are missing information to make a complete answer to the user's question, let the user know about the missing information.

    
    # Tone

    Be professional, concise and informative.
    

    # Response format

    <Short response sentence or paragraph>

    Sources:
       + <Name of the reports containing information relevant to the response(do not include file extension)>
       ...


    # Tools

    Everytime you are given a date relative to the current date, infer it based on the current date given by the function `_get_current_date`.

    When relevant, look for information in the files available using the `_read_file_content(filename)` method, where filename in:
    "company_report_HPG.json" (if you need to find info about HPG)
    "company_report_VHC.json" (if you need to find info about VHC)
    "economics_non_corporate_report.json" (if you need to find info about the economic context)
    "strategy_noncorporate_report" (if you need to find info about the strategic context)
    """

    try:
        response = LLM_CLIENT.models.generate_content(
            model=model,
            contents=user_query,
            config=types.GenerateContentConfig(
                tools=[_get_current_date, _read_file_content],
                system_instruction=system_instructions,
                max_output_tokens=500
            )
        )
        return response.text
    except Exception as e:
        print(f"Error generating AI response: {e}")
        raise # Re-raise for calling context to handle