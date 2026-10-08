import re
import json
from utils.media_utils import extract_audio, detect_and_save_slides, get_media_duration
from ml.transcriber import LectureTranscriber
from typing import Any
import yt_dlp
from pathlib import Path

def download_lecture(youtube_url: str, output_path: str = "samples/test_lecture.mp4") -> str:
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    ydl_opts = {
        "format": "bv*[ext=mp4]+ba[ext=m4a]/b[ext=mp4]",
        "merge_output_format": "mp4",
        "outtmpl": output_path
    }
    print(f"Downloading video from {youtube_url}")
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download(youtube_url)

    print(f"Download complete: {output_path}")
    return output_path

def process_words(segments) -> list[dict]:
    """
    Iterates through faster-whisper segments and groups word objects into sentences
    while retaining start/end timestamps
    """
    sentences = []
    current_sentence_words = []

    sentence_end_pattern = re.compile(r"[.!?]$")

    for segment in segments:
        if not segment.words:
            continue

        for word_info in segment.words:
            word_str = word_info.word.strip()
            if not word_str:
                continue

            current_sentence_words.append(word_info)

            # end of sentence reached
            if sentence_end_pattern.search(word_str):
                sentence_text = " ".join(w.word.strip() for w in current_sentence_words)
                start_time = current_sentence_words[0].start
                end_time = current_sentence_words[-1].end
                avg_confidence = sum(w.probability for w in current_sentence_words) / len(current_sentence_words)

                sentences.append({
                    "text": sentence_text,
                    "start": round(start_time, 2),
                    "end": round(end_time, 2),
                    "confidence": round(avg_confidence, 2),
                    "words": [
                        {
                            "word": w.word.strip(),
                            "start": round(w.start, 2),
                            "end": round(w.end, 2),
                            "probability": round(w.probability, 2)
                        }
                        for w in current_sentence_words
                    ]
                })
                current_sentence_words = []

    # To deal with trailing words without ending with punctuation
    if current_sentence_words:
        sentence_text = " ".join(w.word.strip() for w in current_sentence_words)
        sentences.append({
            "text": sentence_text,
            "start": round(current_sentence_words[0].start, 2),
            "end": round(current_sentence_words[-1].end, 2),
            "confidence": round(sum(w.probability for w in current_sentence_words) / len(current_sentence_words), 2),
            "words": [
                {
                    "word": w.word.strip(),
                    "start": round(w.start, 2),
                    "end": round(w.end, 2),
                    "probability": round(w.probability, 2)
                }
                for w in current_sentence_words
            ]
        })
    return sentences


def align_slides_with_transcript(
        slides_metadata: list[dict],
        sentences: list[dict],
        video_duration: float
) -> list[dict]:
    """
    Maps transcript words/sentences into active slide time windows
    """
    
    if not slides_metadata:
        return []

    all_words = []
    for s in sentences:
        for w in s.get("words", []):
            all_words.append(w)

    synchronized_slides = []

    for i, slide in enumerate(slides_metadata):
        start_time = slide["timestamp"]
        end_time = slides_metadata[i + 1]["timestamp"] if i < len(slides_metadata) - 1 else round(video_duration, 2)

        slide_words = [
            w for w in all_words
            if start_time <= w["start"] < end_time
        ]

        slide_text = " ".join(w["word"] for w in slide_words)

        synchronized_slides.append({
            "slide_id": slide["slide_index"],
            "image_path": slide["file_path"],
            "timestamp_start": start_time,
            "timestamp_end": end_time,
            "word_count": len(slide_words),
            "transcript_text": slide_text,
            "words": slide_words
        })

    return synchronized_slides

        
def run_lecture_pipeline(
        url: str,
        output_json_path: str = "output/synchronized_lecture.json"
        ) -> list[dict]:
    local_video_path = download_lecture(url)
    video_duration = get_media_duration(local_video_path)
    audio_path = extract_audio(local_video_path)

    transcriber = LectureTranscriber(model_size="medium.en")
    raw_segments, info = transcriber.transcribe(audio_path)

    structured_transcript = process_words(raw_segments)

    slides_metadata = detect_and_save_slides(video_path=local_video_path)

    synchronized_data = align_slides_with_transcript(
        slides_metadata=slides_metadata,
        sentences=structured_transcript,
        video_duration=video_duration
    )

    total_words = sum(len(s.get("words", [])) for s in structured_transcript) 

    output_path = Path(output_json_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(synchronized_data, f, indent=2)

    print(f"\n--- Pipeline Complete! ---")
    print(f"Total Slides: {len(synchronized_data)}")
    print(f"Total Words Mapped: {total_words}")
    print(f"Saved payload to: {output_json_path}")

    return synchronized_data

if __name__ == "__main__":
    url = "https://www.youtube.com/watch?v=pTB0EiLXUC8"
    run_lecture_pipeline(url)