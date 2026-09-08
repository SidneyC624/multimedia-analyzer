import torch
from faster_whisper import WhisperModel

def get_whisper_model(model_size: str = "medium.en") -> WhisperModel:
    """
    Initializes and returns an optimized faster-whisper model.
    """
    if torch.cuda.is_available():
        device = "cuda"
        compute_type = "float16"
    else:
        device = "cpu"
        compute_type = "int8"

    return WhisperModel(
        model_size_or_path=model_size,
        device=device,
        compute_type=compute_type
    )

class LectureTranscriber:
    def __init__(self, model_size: str = "medium.en"):
        self.model = get_whisper_model(model_size)

    def transcribe(self, audio_path: str):
        """
        Transcribes audio file with word-level timestamps
        """
        segments, info  = self.model.transcribe(
            audio_path,
            word_timestamps=True,
            vad_filter=True
        )
        return list(segments), info