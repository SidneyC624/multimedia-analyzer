from moviepy import VideoFileClip
import cv2
from pathlib import Path
import subprocess

def has_audio_stream(video_path: str) -> bool:
    """Uses ffprobe to check if video file contains >= 1 audio stream."""
    ffprobe_cmd = [
        "ffprobe",
        "-loglevel", "error",
        "-select_streams", "a",
        "-show_entries", "stream=index",
        "-of", "csv=p=0",
        video_path
    ]

    probe_result = subprocess.run(
        ffprobe_cmd, 
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )

    return bool(probe_result.stdout.strip())

def get_media_duration(file_path: str) -> float:
    """Return the total duration of a media file in seconds using ffprobe"""
    ffprobe_cmd = [
        "ffprobe",
        "-loglevel", "error",
        "-show_entries", "format=duration",
        "-of", "csv=p=0",
        file_path
    ]

    result = subprocess.run(
        ffprobe_cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )

    if result.returncode != 0 or not result.stdout.strip():
        raise RuntimeError(f"Could not read duration for {file_path}: {result.stderr}")

    return float(result.stdout.strip())


def extract_audio(video_path: str) -> str:

    # check if audio exists
    if not has_audio_stream(video_path):
        raise ValueError(f"No audio stream found in video file: {video_path}")

    cache_dir = Path("temp_audio")
    cache_dir.mkdir(parents=True, exist_ok=True)

    audio_file_path = cache_dir / f"{Path(video_path).stem}.wav"

    if audio_file_path.exists() and audio_file_path.getsize() > 0:
        return str(audio_file_path)

    # configure ffmpeg parameters
    command = [
        "ffmpeg",
        "-y",
        "-i", video_path,
        "-vn",
        "-ac", "1",
        "-ar", "16000",
        "-c:a", "pcm_s16le",
        str(audio_file_path)
    ]

    result = subprocess.run(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )

    if result.returncode != 0:
        raise RuntimeError(f"FFmpeg audio extraction failed: {result.stderr}")

    # check output existence and duration match
    if not audio_file_path.exists():
        raise FileNotFoundError(f"Audio file was not created at {audio_file_path}")

    video_duration = get_media_duration(video_path)
    audio_duration = get_media_duration(str(audio_file_path))

    if abs(video_duration - audio_duration) > 0.5:
        audio_file_path.unlink(missing_ok=True)
        raise ValueError(
            f"Duration mismatch: Video {video_duration:.2f}s vs Audio ({audio_duration:.2f}s)"
        )

    return str(audio_file_path)

def extract_keyframes(video_path: str, frame_interval: int = 30):
    cap = cv2.VideoCapture(video_path)
    frame_count = 0

    try:
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            if frame_count % frame_interval == 0:
                yield frame_count, frame
            frame_count += 1
    finally:
        cap.release()
    