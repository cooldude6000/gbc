import os
import json
from openai import OpenAI
from dotenv import load_dotenv
from utils.general import get_transcript_words

def generate_title(transcript_path: str) -> str:
    load_dotenv(override=True)
    client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

    with open(transcript_path, 'r') as f:
        transcript = json.load(f)

    text = get_transcript_words(transcript, 200)  # Configurable word count

    prompt = f"""TRANSCRIPT EXCERPT:
{text}

INSTRUCTIONS:
Create a concise title (max 8 words) that captures the main topic.
The title should be clear and descriptive.
Only return the title, nothing else.
"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        temperature=0.7,
        max_tokens=20,
        messages=[{"role": "user", "content": prompt}]
    )
    
    title = response.choices[0].message.content.strip()
    return title

if __name__ == "__main__":
    title = generate_title("tests/transcript5.json")
    print(f"Generated Title: {title}")