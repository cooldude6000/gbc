from sentence_transformers import SentenceTransformer
from scipy import spatial
import numpy as np
from config.constants import CURSOR_PHRASES

class CursorReference:
    def __init__(self):
        self.model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
        self.cursor_embeddings = self.model.encode(CURSOR_PHRASES)
        
    def is_cursor_reference(self, text, threshold=0.4):
        """Check if text contains spatial reference"""
        text_embedding = self.model.encode([text])[0]
        similarities = [
            1 - spatial.distance.cosine(text_embedding, phrase_embedding)
            for phrase_embedding in self.cursor_embeddings
        ]
        max_sim = max(similarities)
        max_phrase = CURSOR_PHRASES[np.argmax(similarities)]
        if max_sim > threshold:
            print(f"Text: '{text}'\nBest match: '{max_phrase}' (similarity: {max_sim:.3f})")
        return max_sim > threshold