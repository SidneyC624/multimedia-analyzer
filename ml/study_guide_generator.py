import json
import os
import instructor
from openai import OpenAI

from schemas.study_guide import LectureStudyGuide

def generate_study_guide(
    synchronized_json_path: str,
    api_key: str | None = None
) -> LectureStudyGuide:
    """
    Reads synchronized transcript/slide payload  and generates a stuctured 
    study guide (notes, concepts and flashcards) via gpt-4o-mini
    """

    # Load slides and transcript
    with open(synchronized_json_path, "r", encoding="utf-8") as f:
        synchronized_slides = json.load(f)

    # Format input payload for prompting LLM
    formatted_transcript = []
    for slide in synchronized_slides:
        slide_id = slide["slide_id"]
        t_start = slide["timestamp_start"]
        t_end = slide["timestamp_end"]
        transcript = slide.get("transcript_text", "").strip()

        formatted_transcript.append(
            f"[Slide {slide_id} | Time: {t_start:.1f}s - {t_end:.1f}s]\n"
            f"Transcript Content: {transcript if transcript else 'No speech recorded)'}\n"
        )

    full_context_text = "\n".join(formatted_transcript)

    client = instructor.from_openai(
        OpenAI(api_key=api_key or os.environ.get("OPENAI_API_KEY"))
    )

    system_prompt = (
        "You are an expert AI tutor and educational content developer. "
        "Your task is to analyze the provided timestamped lecture content and produce an executive-level study guide. "
        "Group related consecutive slides into logical chapters based on topic transitions rather than creating 1 chapter per slide. "
        "Ensure markdown summaries include code snippets or structural explanations where relevant."
    )

    user_prompt = (
        f"Here is the synchronized transcript and slde timeline from the lecture: \n\n"
        f"{full_context_text}\n\n"
        f"Please synthesize this into a structured lecture study guide."
    )

    # Call LLM with structured output enforcement
    study_guide: LectureStudyGuide = client.chat.completions.create(
        model="gpt-4o-mini",
        response_model=LectureStudyGuide,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        temperature=0.2
    )

    return study_guide
