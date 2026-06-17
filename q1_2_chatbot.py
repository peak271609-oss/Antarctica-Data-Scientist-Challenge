import os
from dotenv import load_dotenv
from google import genai

# AI assistance note: using AI for research to understand how a simple chatbot can be embedded in a GUI

load_dotenv()

def ask_about_repos(question, repo_names):

    api_key = os.getenv("GEMINI_API_KEY")
    model_name = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")

    if not api_key:
        return (
            "Gemini API key is missing.\n\n"
            "Please create a .env file and add:\n"
            "GEMINI_API_KEY=your_api_key_here"
        )

    if not repo_names:
        return "No available repository names. Please scrape GitHub repositories first."

    client = genai.Client(api_key=api_key)

    repo_text = "\n".join(f"- {name}" for name in repo_names)

    prompt = f"""
You are an AI chatbot embedded in a GitHub repository scraper GUI.

The user can ask questions about the GitHub repository names below.
Only answer based on the repository names.
Do not pretend to know the repository contents unless the name clearly suggests it.

Repository names:
{repo_text}

User question:
{question}

Answer clearly and concisely.
"""

    try:
        response = client.models.generate_content(
            model=model_name,
            contents=prompt
        )
        return response.text

    except Exception as error:
        return f"Error calling Gemini API: {error}"