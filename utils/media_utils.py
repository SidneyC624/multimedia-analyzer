import cv2
from pathlib import Path
import subprocess
import numpy as np

def has_audio_stream(video_path: str) -> bool:
    """Uses ffprobe to check if video file contains >= 1 audio stream."""
    ffprobe_cmd = [
        "ffprobe",
        "-loglevel", "error",
        "-select_streams", "a",
        "-show_entries", "stream=index",
        "-of", "csv=p=0",
        str(video_path)
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
        str(file_path)
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

    if audio_file_path.exists() and audio_file_path.stat().st_size > 0:
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

def extract_keyframes(video_path: str, sample_rate_sec: float = 1.0):
    """
    Yields sampled video frames along with frame index and timestamp.
    """
    video_path_str = str(video_path)
    cap = cv2.VideoCapture(video_path_str)

    if not cap.isOpened():
        raise ValueError(f"Could not open video file: {video_path_str}")

    try:
        fps = cap.get(cv2.CAP_PROP_FPS)
        if fps <= 0:
            fps = 30

        total_frames = cap.get(cv2.CAP_PROP_FRAME_COUNT)
        frame_step = max(1, int(round(fps * sample_rate_sec)))

        current_frame = 0

        while current_frame < total_frames:
            cap.set(cv2.CAP_PROP_POS_FRAMES, current_frame)
            ret, frame = cap.read()

            if not ret:
                break

            timestamp_sec = round(current_frame / fps, 2)

            yield {
                "frame_index": current_frame,
                "timestamp": timestamp_sec,
                "frame": frame,
                "fps": fps,
                "total_frames": total_frames
            }
            
            current_frame += frame_step

    finally:
        cap.release()


def preprocess_frame(frame: np.ndarray) -> np.ndarray:
    """
    Converts frame to grayscale and applies Gaussian blur to reduce moise
    """
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    return blurred


def detect_and_save_slides(
        video_path: str,
        output_dir: str = "slides",
        threshold: float = 15.0,
        sample_rate_sec: float = 1.0,
) -> list[dict]:
    """
    Analyzes sampled video frames, detects slide transitions based on mean pixel difference

    Returns:
    list[dict[str, Any]]: list of metadata dictionaries for each saved slide
    """
    slides_path  = Path(output_dir)
    slides_path.mkdir(parents=True, exist_ok=True)

    previous_frame = None
    slides = []
    slide_count = 1

    for frame_data in extract_keyframes(video_path=video_path, sample_rate_sec=sample_rate_sec):
        raw_frame = frame_data["frame"]
        timestamp = frame_data["timestamp"]

        current_frame = preprocess_frame(raw_frame)

        # at 1st frame
        if previous_frame is None:
            slide_filename = f"slide_{slide_count:03d}_at_{timestamp:.1f}s.jpg"
            save_path = slides_path / slide_filename
            cv2.imwrite(str(save_path), raw_frame)

            slides.append({
                "slide_index": slide_count,
                "timestamp": timestamp,
                "file_path": str(save_path),
                "change_score": 100.0
            })
            previous_frame = current_frame
            slide_count += 1
            continue

        abs_diff = cv2.absdiff(previous_frame, current_frame)

        change_score = (np.mean(abs_diff) / 255.0) * 100.0

        if change_score >= threshold:
            slide_filename = f"slide_{slide_count:03d}_at_{timestamp:.1f}s.jpg"
            save_path = slides_path / slide_filename
            cv2.imwrite(str(save_path), raw_frame)

            slides.append({
                "slide_index": slide_count,
                "timestamp": timestamp,
                "file_path": str(save_path),
                "change_score": round(change_score, 2)
            })
            previous_frame = current_frame
            slide_count += 1

    print(f"Detected and saved {len(slides)} unique slides to {output_dir}")
    return slides