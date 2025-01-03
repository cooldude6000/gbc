import custom_types
from utils.general import chunk_transcript, linearize_transcript
from ..search import main as search_main

def main(transcript: custom_types.Transcript) -> list[custom_types.Range]:
    layout_changes = []

    intro_query = "Find where the speaker introduces themselves or the product in the video."
    try:
        intro_result = search_main(transcript, intro_query)
        layout_changes.append(intro_result)
    except RuntimeError:
        pass  # coz sometimes there will be no intro, so.

    full_text = linearize_transcript(transcript)
    word_count = len(full_text.split())

    if word_count >= 170:
        chunks = chunk_transcript(transcript, duration=170, overlap=20)
        for chunk in chunks:
            chunk_section = chunk["transcript"]
            if len(chunk_section) < 20:
                continue

            query = (
                "Extract the single most important or impactful sentence from this "
                "transcript section. If you don't think any of the sentences is important, "
                "you must still select at least one sentence from the transcript. The sentence "
                "must be an exact match from the transcript."
            )
            try:
                important_part = search_main(chunk_section, query)
                print(important_part)
                layout_changes.append(important_part)
            except RuntimeError:
                continue  # If the search fails for this chunk, continue with the next one.

    return layout_changes