from typing import TypedDict, List


class Range(TypedDict):
    start: int
    end: int


class Point(TypedDict):
    x: int
    y: int


class Word(TypedDict):
    id: str
    start: int
    end: int
    text: str

class CursorPosition(TypedDict):
    x: float
    y: float

class CursorSegment(TypedDict):
    start: int
    end: int
    pos: CursorPosition

class CursorPhrase(TypedDict):
    text: str
    embedding: List[float]

class CursorReference(TypedDict):
    start: int
    end: int
    text: str
    similarity: float

Transcript = List[Word]
