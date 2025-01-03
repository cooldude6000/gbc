import os
from dotenv import load_dotenv
import openai
import custom_types
import utils

load_dotenv(override=True)
oai = openai.OpenAI(api_key=os.getenv('OPENAI_API_KEY'))


def main(transcript: custom_types.Transcript, query: str) -> custom_types.Range:
    """
    Transcript search. Finds the section of a transcript corresponding to a given query.

    Parameters:
    transcript (Transcript): Transcript of the camera video file.
    query (str): The search query.

    Returns:
    dict (Range): A frame range corresponding to the part of the transcript which fulfils the query.
    """

    # Convert transcript to string
    transcript_text = utils.linearize_transcript(transcript)

    # Create prompt
    prompt = f"""TRANSCRIPT:
{transcript_text}

INSTRUCTIONS:
Return a substring from the transcript above which fulfils the following query: {query}.
The substring must be an exact substring of the original transcript. You must not add or change any words.
"""

    # Execute prompt
    response = oai.chat.completions.create(
        model="gpt-4o-mini",
        temperature=1,
        top_p=1,
        max_tokens=50,
        messages=[{"role": "user", "content": prompt}],
    )
    response = response.choices[0].message.content

    # Log raw response
    print("----- LLM RESPONSE -----")
    print(response)
    print("\n")

    # Extract section of transcript corresponding to response
    word_range = utils.find_section_range(transcript, response)
    print("----- WORD RANGE CORRESPONDING TO LLM RESPONSE -----")
    print(word_range)
    print("\n")

    # If failed to find section, then raise error
    if not word_range:
        raise RuntimeError("Failed to find section range.")

    # Destructure word range
    start_temp, end_temp = word_range
    start_word_index, end_word_index = start_temp, end_temp-1

    # Extract start and end frame
    start_frame = transcript[start_word_index]["start"]
    end_frame = transcript[end_word_index]["end"]

    # Log section of transcript that was selected by LLM
    print("----- TRANSCRIPT SECTION CORRESPONDING TO LLM RESPONSE -----")
    print(utils.linearize_transcript(transcript[start_word_index:end_word_index]))

    print("Start frame:", start_frame)
    print("End frame:", end_frame)
    print("\n")

    return {"start": start_frame, "end": end_frame}
