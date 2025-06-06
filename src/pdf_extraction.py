prompt = """
Task:
Extract paragraph titles and their corresponding text from the provided PDF document.

Instructions:
- Include only:
  - Paragraph titles (if available) and their associated paragraph text
  - Any bullet-point summaries associated with each paragraph
- Exclude:
  - Tables
  - Charts or graphs
  - Footers and headers
  - Legal disclaimers or notices

Formatting Guidelines:
- Paragraph text must be in valid Markdown syntax.
- Bullet points should be formatted as Markdown list items (e.g., "- Item").
- All output must use ASCII characters only (no Unicode or special symbols).

Output Format:
Return a single JSON object structured as follows:
{
  "report_date": "DD/MM/YYYY",  // Extract this from the document content
  "content": [
    {
      "title": "Title of the paragraph",
      "paragraph": "Markdown-formatted paragraph text."
    },
    ...
  ]
}

Constraints:
- The output must be valid JSON.
- Use only ASCII characters in both keys and values.
- Do not include any explanatory text, comments, or metadata outside the JSON object.
"""