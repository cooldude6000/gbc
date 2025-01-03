import os
import custom_types


def main(
    transcript: custom_types.Transcript,
    camera_video_path: str,
) -> custom_types.Range:
    """
    Trim unnecessary silence at the start/end of a video.

    Parameters:
    transcript (Transcript): Transcript of the camera video file.
    camera_video_path (str): Path to the camera video file.

    Returns:
    dict (Range): A range representing the part of the video to keep.

    Notes:
    - No notes.
    """

    # Log for debugging purposes
    print("trim()", transcript[0:5], camera_video_path)

    for t in transcript:
        if t["text"]:
            start = t["start"]
            break

    for t in reversed(transcript):
        if t["text"]:
            end = t["end"]
            break

    return {"start": start, "end": end}
