import assemblyai as aai
import uuid
import os
import json

aai.settings.api_key = "c88a63312cb34a2ab566821a463d0b52"

FPS = 30

config = aai.TranscriptionConfig(
    language_code="en",
    speech_model="best",
)

# Start transcription
transcriber = aai.Transcriber(config=config)

audio_path = os.path.join(os.path.dirname(__file__), "audiofiles", "testaudio.mp3")

response = transcriber.transcribe(audio_path).json_response
words = response["words"]

# This can happen if there are no words in the audio (e.g. if there is no audio stream)
if not words:
    print("No words found in audio")
    exit(1)

# Reformat the response
words = [
    {
        "id": str(uuid.uuid4()),
        "start": round(word["start"] / 1000 * FPS),
        "end": round(word["end"] / 1000 * FPS),
        "text": word["text"],
    }
    for word in words
]

tests_dir = os.path.join(os.path.dirname(__file__), "tests")
os.makedirs(tests_dir, exist_ok=True)

output_path = os.path.join(tests_dir, "transcript5.json")
with open(output_path, 'w') as f:
    json.dump(words, f, indent=2)