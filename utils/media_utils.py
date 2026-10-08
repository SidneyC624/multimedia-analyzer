import cv2
from pathlib import Path
import subprocess
import numpy as np
import imagehash
from PIL import Image
from collections import deque

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


def preprocess_frame(frame: np.ndarray) -> np.ndarray:
    """
    Converts frame to grayscale and applies Gaussian blur to reduce moise
    """
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    return blurred


def compute_structural_diff(frame1_gray: np.ndarray, frame2_gray: np.ndarray, min_contour_area: int = 150) -> float:
    """
    Finds structural changes using connected component contour detection
    Triggers on localized region additions
    """
    abs_diff = cv2.absdiff(frame1_gray, frame2_gray)
    _, binary_diff = cv2.threshold(abs_diff, 20, 255, cv2.THRESH_BINARY)

    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))
    dilated_diff = cv2.dilate(binary_diff, kernel, iterations=2)

    contours, _ = cv2.findContours(dilated_diff, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    total_changed_bounded_area = 0
    for cnt in contours:
        area = cv2.contourArea(cnt)
        # Otherwise most likely noise
        if area >= min_contour_area:
            total_changed_bounded_area += area

    return (total_changed_bounded_area / binary_diff.size) * 100.0


def is_frame_valid(
        frame_gray: np.ndarray, 
        blur_thresh: float = 5.0, 
        edge_thresh: float = 0.005) -> bool:
    """Checks if frame is too blurry or blank (lacking content)"""
    laplacian_var = cv2.Laplacian(frame_gray, cv2.CV_64F).var()
    if laplacian_var < blur_thresh:
        return False

    edges = cv2.Canny(frame_gray, 100, 200)
    edge_density = (np.count_nonzero(edges) / edges.size) * 100.0
    return edge_density >= edge_thresh


def compute_orb_similarity(frame1_gray: np.ndarray, frame2_gray: np.ndarray) -> float:
    """
    Computes scale-invariant feature similarity using ORB keypoints
    Returns a match ratio between 0.0 and 1.0. High ratio -> most likely zoomed/scaled duplicate.
    """
    orb = cv2.ORB_create(nfeatures=500)
    kp1, des1 = orb.detectAndCompute(frame1_gray, None)
    kp2, des2 = orb.detectAndCompute(frame2_gray, None)

    bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
    matches = bf.match(des1, des2)

    if not matches:
        return 0.0

    matches = sorted(matches, key=lambda x: x.distance)
    good_matches = [m for m in matches if m.distance < 50]

    min_keypoints = min(len(kp1), len(kp2))
    return len(good_matches) / min_keypoints if min_keypoints > 0 else 0.0



def detect_and_save_slides(
        video_path: str,
        output_dir: str = "slides",
        sample_interval: float = 0.2,
        min_change_percent: float = 0.02,
        stable_diff_thresh: float = 0.15,
        stable_required_sec: float = 1.0,
        max_unstable_sec: float = 4.0,
        phash_threshold: int = 6, # Hamming distance for deduplication
        window_size: int = 3, # For sliding window tolerance
        dup_struct_diff_thesh = 0.02,
        orb_sim_thresh = 0.60
) -> list[dict]:
    """
    Analyzes sampled video frames, detects slide transitions based on structural difference, 
    filters out transition animations, motion blur and blank frames

    Returns:
    list[dict[str, Any]]: list of metadata dictionaries for each saved slide
    """
    slides_path  = Path(output_dir)
    slides_path.mkdir(parents=True, exist_ok=True)

    cap = cv2.VideoCapture(video_path)
    fps = cap.get(cv2.CAP_PROP_FPS)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    duration_sec = total_frames / fps if fps > 0 else 0

    candidates = []
    reference_frame = None
    prev_frame = None

    stable_timer = 0.0
    unstable_timer = 0.0
    pending_candidate = None

    diff_history = deque(maxlen=window_size)
    current_time = 0.0

    while current_time < duration_sec:
        # Jump to current timestamp
        cap.set(cv2.CAP_PROP_POS_MSEC, current_time * 1000.0)
        ret, raw_frame = cap.read()
        if not ret:
            break

        current_gray = preprocess_frame(raw_frame)

        if reference_frame is None:
            if is_frame_valid(current_gray):
                reference_frame = current_gray
                prev_frame = current_gray
                candidates.append((current_time, raw_frame))
            current_time += sample_interval
            continue

        # for detecting if change has begun and change has settled
        diff_from_ref = compute_structural_diff(reference_frame,current_gray)
        diff_from_prev = compute_structural_diff(prev_frame, current_gray)
        diff_history.append(diff_from_prev)

        avg_diff_from_prev = sum(diff_history) / len(diff_history)

        if diff_from_ref >= min_change_percent:
            unstable_timer += sample_interval

            if avg_diff_from_prev < stable_diff_thresh:
                stable_timer += sample_interval
                pending_candidate = (current_time, raw_frame, current_gray)
            else:
                # still moving
                stable_timer = max(0.0, stable_timer - sample_interval)

            is_stable = stable_timer >= stable_required_sec and pending_candidate is not None

            is_timeout = unstable_timer >= max_unstable_sec

            if is_stable or is_timeout:
                if pending_candidate:
                    ts, cand_frame, cand_gray = pending_candidate
                else:
                    ts, cand_frame, cand_gray = current_time, raw_frame, current_gray
                
                if is_frame_valid(cand_gray):
                    candidates.append((ts, cand_frame))
                    reference_frame = cand_gray
                stable_timer = 0.0
                unstable_timer = 0.0
                pending_candidate = None
                diff_history.clear()
        else:
            stable_timer = 0.0
            unstable_timer = 0.0
            pending_candidate = None
        
        current_time += sample_interval
        prev_frame = current_gray

    cap.release()
        
    # Removing Duplicates with Perceptual Hash
    final_slides = []
    last_hash = None
    last_frame_gray = None
    slide_count = 1

    for ts, frame in candidates:
        curr_gray = preprocess_frame(frame)
        pil_img = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
        curr_hash = imagehash.phash(pil_img)

        if last_hash is not None:
            hash_dist = curr_hash - last_hash
            # Compute pixel diff to ensure zooms are retained even if pHash is similar
            struct_diff = compute_structural_diff(last_frame_gray, curr_gray)
            orb_sim = compute_orb_similarity(last_frame_gray, curr_gray)

            if struct_diff < dup_struct_diff_thesh:
                continue

            if hash_dist < phash_threshold and orb_sim > orb_sim_thresh:   
                continue

        slide_filename = f"slide_{slide_count:03d}_at_{ts:.1f}s.jpg"
        save_path = slides_path / slide_filename
        cv2.imwrite(str(save_path), frame)

        final_slides.append({
            "slide_index": slide_count,
            "timestamp": ts,
            "file_path": str(save_path)
        })
        last_hash = curr_hash
        last_frame_gray = curr_gray
        slide_count += 1

    print(f"Detected and saved {len(final_slides)} unique slides to {output_dir}")
    return final_slides