import os
from dotenv import load_dotenv
from google import genai
from google.genai import types

MODEL = 'gemini-2.5-flash-preview-05-20'
#MODEL = 'gemini-2.0-flash-001'

ALLOWED_FILES_DIRECTORY = '/home/eolus/workspace/research-portal/data/reports/JSON'

def read_file_content(filename: str) -> str:
    """Reads the content of a specified file and returns it as a string.
    Only allows reading files from a pre-defined directory.

    Args:
        filename (str): The name of the file to read.

    Returns:
        str: The content of the file, or an error message if the file cannot be read or is not allowed.
    """
    # Construct the full path, ensuring it's within the allowed directory
    # This is crucial for security to prevent path traversal attacks
    filepath = os.path.join(ALLOWED_FILES_DIRECTORY, os.path.basename(filename)) # os.path.basename prevents ../../ attacks

    # Optional: Further restrict to a specific list of allowed files if needed
    # if os.path.basename(filename) not in ['Q1_2024_Financial_Report.txt', 'Current_Market_Data.csv']:
    #     return f"Error: Access to file '{filename}' is not allowed."
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        return content
    except FileNotFoundError:
        return f"Error: File '{filename}' not found in the allowed directory."
    except IOError as e:
        return f"Error reading file '{filename}': {e}"





import datetime

def get_current_date() -> str:
    """Returns the current date spelled out, like 'June 16th 2025'.
    """
    now = datetime.datetime.now()
    day = now.day

    # Determine the day suffix (st, nd, rd, th)
    if 11 <= day <= 13:
        suffix = "th"
    else:
        suffix = {1: "st", 2: "nd", 3: "rd"}.get(day % 10, "th")

    # Format the month and year, then combine with the day and suffix
    return now.strftime(f"%B {day}{suffix} %Y")

def main():

    # Ensure environment variables are loaded
    load_dotenv()
    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        raise ValueError("GEMINI_API_KEY environment variable not set. Please set it in your .env file.")

    client = genai.Client(api_key=api_key) 

    while True:

        query = input("\n\nQuestion:\n > ")

        system_instructions = """
        You are a helpful financial analyst tasked with answering other analysts questions.

Everytime you are given a date relative to the current date, infer it based on the current date given by the function `get_current_date`.

When relevant, look for information in the files available using the `read_file_content(filename)` method, where filename in:
"company_report_HPG.json" (if you need to find info about HPG)
"company_report_VHC.json" (if you need to find info about VHC)
"economics_non_corporate_report.json" (if you need to find info about the economic context)
"strategy_noncorporate_report" (if you need to find info about the strategic context)
"""

        try:
            # Make the request to Gemini
            print("Thinking...")
            response = client.models.generate_content(
                model='gemini-2.5-flash-preview-05-20',
                contents=query,
                config=types.GenerateContentConfig(
                    tools=[get_current_date, read_file_content],
                    system_instruction=system_instructions,
                    max_output_tokens=500))


            print(response.text)

        except Exception as e:
            print(f"An error occurred during the API request: {e}")



if __name__ == "__main__":
    main()