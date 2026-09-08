import re
import json
from utils.media_utils import extract_audio
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

def run_lecture_pipeline(video_path: str) -> tuple[list[dict], Any]:
    local_video_path = download_lecture(video_path)
    audio_path = extract_audio(local_video_path)

    transcriber = LectureTranscriber(model_size="medium.en")
    raw_segments, info = transcriber.transcribe(audio_path)

    structured_transcript = process_words(raw_segments)

    print(f"Processed {len(structured_transcript)} sentences")
    return structured_transcript, info

if __name__ == "__main__":
    video_path = "something"

    transcript, info = run_lecture_pipeline("https://www.youtube.com/watch?v=pTB0EiLXUC8")

    output_json = "temp_audio/processed_transcript.json"
    Path(output_json).parent.mkdir(parents=True, exist_ok=True)

    with open("temp_audio/processed_transcript.json", "w", encoding="utf-8") as f:
        json.dump(transcript, f, indent=2)

    print(f"Pipeline finished successfully!\n Saved structured transcript to {output_json}")