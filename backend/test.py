from dotenv import load_dotenv
from functions.translate.main import main as translate_transcript
import json

def main():
    load_dotenv()  # Load environment variables if using OpenAI fallback
    
    translated = translate_transcript(
        transcript_path='tests/transcript6.json',
        from_lang='en',
        to_lang='de'
    )
    
    print("\nTranslated Transcript:")
    print(json.dumps(translated, indent=4, ensure_ascii=False))

if __name__ == "__main__":
    main()
