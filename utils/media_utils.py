from moviepy import VideoFileClip
import cv2

def extract_audio(video_path: str, audio_path: str):
    video_clip = VideoFileClip(video_path)
    if video_clip.audio != None:
        video_clip.audio.write_audiofile(audio_path)
    video_clip.close()


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
    