from sentence_transformers import SentenceTransformer
from utils.general import linearize_transcript, split_into_clauses, find_transcript_segment
from config.constants import FPS, CURSOR_PHRASES
from backend.detectors.cursor_reference import CursorReference
import numpy as np
import cv2
import re
import json
import os

def detect_cursor(frame):
    # we can integrate the YOLO model here to detect the cursor 
    # and pass the frame in props to the model to detect the cursor 
    # and get the x,y co-ordinates of the cursor and return them
    print("smthn")

def process_video(video_path, transcript):
    print("\ninit")
    detector = CursorReference()
    results = []
    
    full_text = linearize_transcript(transcript)
    clauses = split_into_clauses(full_text)
    #print(f"Found {len(clauses)} clauses.")
    
    for clause in clauses:
        if detector.is_cursor_reference(clause):
            segment = find_transcript_segment(clause, transcript)
            if segment:
                cap = cv2.VideoCapture(video_path)
                timestamp_ms = (segment['start'] * 1000) / FPS
                cap.set(cv2.CAP_PROP_POS_MSEC, timestamp_ms)
                ret, frame = cap.read()
                
                if ret:
                    #passing the frame in which we need to identify the cursor position to the detect_cursor function
                    cursor_pos = detect_cursor(frame)
                    if cursor_pos:
                        results.append({
                            'start': segment['start'],
                            'end': segment['end'],
                            'pos': cursor_pos
                        })
                cap.release()
    return results