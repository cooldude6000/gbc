from typing import List, Dict
from openai import OpenAI
import os
from dotenv import load_dotenv
import json
from pathlib import Path

# Load environment variables from .env file
load_dotenv()

def generate_summary(transcript: List[Dict]) -> str:
    """Generate a concise summary (~100 words) of the transcript content"""
    try:
        # Get API key from environment
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            raise ValueError("OPENAI_API_KEY not found in environment variables")

        # Extract all text from transcript
        full_text = " ".join(item['text'] for item in transcript)
        
        # Initialize OpenAI client
        client = OpenAI(api_key=api_key)
        
        # Generate summary using OpenAI
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "Generate a concise summary (about 50 words) of the following transcript:"},
                {"role": "user", "content": full_text}
            ],
            max_tokens=150
        )
        
        return response.choices[0].message.content
        
    except Exception as e:
        raise Exception(f"Failed to generate transcript summary: {e}")

if __name__ == "__main__":
    try:
        # Use Path for cross-platform compatibility
        transcript_path = Path("tests/transcript5.json")
        
        if not transcript_path.exists():
            raise FileNotFoundError(f"Transcript file not found: {transcript_path}")
            
        with open(transcript_path, 'r') as f:
            transcript_data = json.load(f)
        
        summary = generate_summary(transcript_data)
        print(f"Transcript Summary:\n{summary}")
        
    except Exception as e:
        print(f"Error: {e}")