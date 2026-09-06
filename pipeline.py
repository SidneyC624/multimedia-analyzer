import re

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

        for word_info in segment:
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
                