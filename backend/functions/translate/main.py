import json
import nltk
from deep_translator import GoogleTranslator
from openai import OpenAI
import os
from typing import List, Dict

# Download necessary NLTK data
nltk.download('punkt')

def split_into_sentences(transcript: List[Dict]) -> List[List[Dict]]:
    """Split transcript into sentence groups while preserving timing info"""
    current_sentence = []
    sentences = []
    current_text = ""
    
    for word in transcript:
        current_sentence.append(word)
        current_text += word['text'] + " "
        
        if word['text'].endswith(('.', '!', '?')):
            sentences.append(current_sentence)
            current_sentence = []
            current_text = ""
    
    if current_sentence:  # Add any remaining words
        sentences.append(current_sentence)
    
    return sentences

def translate_text(text: str, from_lang: str, to_lang: str) -> str:
    """Attempt translation with fallback mechanisms"""
    # First try deep-translator
    try:
        print("Using google translator")
        return GoogleTranslator(source=from_lang, target=to_lang).translate(text)
    except Exception as e:
        print(f"Deep-translator failed: {e}")
        
    # Fallback to OpenAI
    try:
        print("Using OpenAI")
        client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": f"Translate the following from {from_lang} to {to_lang}:"},
                {"role": "user", "content": text}
            ]
        )
        return response.choices[0].message.content
    except Exception as e:
        raise Exception(f"All translation methods failed: {e}")

def map_timings(original_words: List[Dict], translated_text: str) -> List[Dict]:
    """Map timings from original words to translated words"""
    translated_words = translated_text.strip().split()
    result = []
    
    if len(original_words) == len(translated_words):
        # Direct mapping if word counts match
        for i, word in enumerate(translated_words):
            result.append({
                'id': original_words[i]['id'],
                'start': original_words[i]['start'],
                'end': original_words[i]['end'],
                'text': word
            })
    else:
        # Distribute time equally if word counts don't match
        total_duration = original_words[-1]['end'] - original_words[0]['start']
        word_duration = total_duration / len(translated_words)
        current_time = original_words[0]['start']
        
        for i, word in enumerate(translated_words):
            result.append({
                'id': f"{original_words[0]['id']}.{i}",
                'start': current_time,
                'end': current_time + word_duration,
                'text': word
            })
            current_time += word_duration
    
    return result

def main(transcript_path: str, from_lang: str, to_lang: str) -> List[Dict]:
    with open(transcript_path, 'r') as f:
        transcript = json.load(f)
    
    # Split into sentences
    sentences = split_into_sentences(transcript)
    final_result = []
    
    # Process each sentence
    for sentence in sentences:
        # Combine sentence words
        sentence_text = " ".join(word['text'] for word in sentence)
        
        # Translate
        translated_text = translate_text(sentence_text, from_lang, to_lang)
        
        # Map timings
        translated_sentence = map_timings(sentence, translated_text)
        final_result.extend(translated_sentence)
    
    return final_result
