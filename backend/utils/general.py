import json
import custom_types
import math
import re

def get_transcript_words(transcript, word_count):
    return " ".join([word["text"] for word in transcript[:word_count]])

def linearize_transcript(transcript):
    return " ".join([word["text"] for word in transcript])

def split_into_clauses(text):
    """Split text into clauses based on punctuation and conjunctions."""
    clause_pattern = r'(?<=[.,;])\s+|(?=\band\b|\bbut\b|\bor\b)'
    clauses = re.split(clause_pattern, text)
    return [clause.strip() for clause in clauses if clause.strip()]

#we might have to improve this function - using sliding window/rabin karp
def find_transcript_segment(clause, transcript):
    words = clause.split()
    if len(words) < 3:
        return None
        
    word1, word2, word3 = words[0:3]
    
    for i in range(len(transcript) - 2):
        current = transcript[i]
        next_seg = transcript[i + 1]
        third_seg = transcript[i + 2]
        
        if (current["text"].lower() == word1.lower() and 
            next_seg["text"].lower() == word2.lower() and
            third_seg["text"].lower() == word3.lower()):
            return current
        
    return None

def chunk_transcript(transcript, duration, overlap=0):
    # Calculate words per minute of speech
    overall_duration = transcript[-1]["end"]
    wpm = 150
    if overall_duration:
        wpm = int(len(transcript) / (overall_duration / 30 / 60))
        wpm = min(280, max(50, wpm))

    # Calculate chunking parameters
    max_words_per_chunk = int(wpm / 60 / 30 * duration)
    overlap = int(wpm / 60 / 30 * overlap)

    num_chunks = max(1, math.floor(len(transcript) / max_words_per_chunk))

    chunks = []
    for i in range(num_chunks):
        start = i * max_words_per_chunk
        end = (i + 1) * max_words_per_chunk + overlap

        range_dict = {"start": start, "end": end}
        range_dict = extend_to_complete_sentences(range_dict, transcript)
        start, end = range_dict["start"], range_dict["end"]

        if i == num_chunks - 1:
            end = len(transcript)

        chunks.append({"offset": start, "transcript": transcript[start:end]})

    return chunks

def read_test_data(test_number: int):
    """
    Reads and returns the test data for a given test number.

    This function loads a test's transcript from a JSON file, and constructs paths
    for the associated camera and screen videos based on the test number.

    Parameters:
    test_number (int): The identifier for the test data to be read.

    Returns:
    tuple: A tuple containing:
        - transcript (dict): The test's transcript data loaded from a JSON file.
        - camera_video_path (str): The path to the test's camera video file.
        - screen_video_path (str): The path to the test's screen video file.

    Notes:
    - No notes.
    """
    # Read test transcript
    with open(f"tests/{test_number}/transcript.json") as f:
        transcript = json.load(f)

    # Create test camera_video_path
    camera_video_path = f"tests/{test_number}/camera_video.mp4"

    # Create test screen_video_path
    screen_video_path = f"tests/{test_number}/screen_video.mp4"

    return transcript, camera_video_path, screen_video_path

def extend_to_complete_sentences(
    word_range: custom_types.Range, transcript: custom_types.Transcript
) -> custom_types.Range:
    """
    Given a range and a transcript, this function extends the start/end of the
    range such that it results in a complete sentence when we perform
    transcript[word_range["start"]:word_range["end"]].

    Parameters:
    word_range (Range): The initial range of words, where word_range["start"] is
                        the index of the first word in the transcript (inclusive)
                        and word_range["end"] is the index of the last word in the
                        transcript (exclusive).
    transcript (Transcript): The corresponding transcript.

    Returns:
    word_range (Range): The updated range of words.
    """
    eos = ["?", "!", "."]

    start = word_range["start"]
    end = word_range["end"]

    # Extend start backwards
    while start > 0 and transcript[start - 1]["text"][-1] not in eos:
        start -= 1

    # Extend end forwards
    while end < len(transcript) - 1 and transcript[end - 1]["text"][-1] not in eos:
        end += 1

    return {"start": start, "end": end}