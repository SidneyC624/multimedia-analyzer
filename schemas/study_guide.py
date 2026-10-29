from pydantic import BaseModel, Field
from typing import List

class Flashcard(BaseModel):
    front: str = Field(
        ...,
        description="Question or prompt testing a core concept, key term, or syntax from the chapter"
    )
    back: str = Field(
        ...,
        description="Concise, precise answer or explanation."
    )

class Chapter(BaseModel):
    timestamp_start: float = Field(..., description="Start timestamp of the logical topic boundary in seconds")
    timestamp_end: float = Field(..., description="End timestamp of the logical topic boundary in seconds")
    title: str = Field(..., description="Concise, descriptive title for this conceptual section.")
    key_concepts: List[str] = Field(..., description="List of 3-5 core technical key terms introduced.")
    summary_markdown: str = Field(
        ...,
        description="Comprehensice summary formatted in clean Markdown (using bullet points, bold text, and code blocks where applicaable)."
    )
    flashcards: List[Flashcard] = Field(..., description="3-5 high value study flashcards derived specifically from this section")

class LectureStudyGuide(BaseModel):
    course_topic: str = Field(..., description="The overall subject or high-level title of the lecture.")
    overall_summary: str = Field(..., description="An executive summary of the whole lecture in 2-3 paragraphs.")
    chapters: List[Chapter] = Field(..., description="Chronological chapters dividing the lecture into logical conceptual units")