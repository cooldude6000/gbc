import openai
from typing import List, Dict

def get_full_text(transcript: List[Dict]) -> str:
    """Combines all transcript segments into single text"""
    return " ".join(segment["text"] for segment in transcript)

def get_chapters_from_gpt(text: str) -> List[Dict]:
    """Uses GPT to identify natural chapter breaks and titles"""
    prompt = """
    This is a transcript of a video. Please identify 3-5 main chapters/segments and their titles.
    For each chapter provide:
    1. A short title (max 5 words)
    2. The starting words of that segment
    
    Format your response exactly like this:
    Chapter 1: <title>
    Starts with: "<first few words>"
    
    Chapter 2: <title>
    Starts with: "<first few words>"
    """
    
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant that analyzes video transcripts."},
            {"role": "user", "content": f"{text}\n\n{prompt}"}
        ]
    )
    return parse_gpt_response(response.choices[0].message.content)

def find_start_index(transcript: List[Dict], starting_words: str) -> int:
    """Finds the start index in transcript where the given words appear"""
    for segment in transcript:
        if segment["text"].strip() in starting_words:
            return segment["start"]
    return 0

def generate_chapters(transcript: List[Dict]) -> List[Dict]:
    """Main function to generate chapters"""
    full_text = get_full_text(transcript)
    gpt_chapters = get_chapters_from_gpt(full_text)
    
    chapters = []
    for i, chapter in enumerate(gpt_chapters):
        start = find_start_index(transcript, chapter["starting_words"])
        # End is either next chapter's start or end of transcript
        end = gpt_chapters[i+1]["start"] if i < len(gpt_chapters)-1 else transcript[-1]["end"]
        
        chapters.append({
            "start": start,
            "end": end,
            "title": chapter["title"]
        })
    
    return chapters

if __name__ == "__main__":
    import json
    import os
    
    openai.api_key = os.getenv("OPENAI_API_KEY")
    
    with open("tests/transcript5.json", "r") as f:
        transcript = json.load(f)
    
    chapters = generate_chapters(transcript)
    print(json.dumps(chapters, indent=2))