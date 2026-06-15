"""Automatic clip extraction with signal-aware scoring."""

import re
from dataclasses import dataclass, field
from typing import Dict, List, Optional

from src.asr import ASRSegment


@dataclass
class Clip:
    start: float
    end: float
    text: str
    score: float
    hook_sentence: str = ""
    metadata: Dict = field(default_factory=dict)


class SignalClipper:
    """Extract high-signal clips from ASR transcripts.

    Scores clips based on:
    - keyword matches (price, health, civic terms, etc.)
    - sentiment shift / contrast
    - duration sweet spot
    - hook density (topic transitions)
    """

    def __init__(
        self,
        signal_keywords: Optional[List[str]] = None,
        min_duration: float = 15.0,
        max_duration: float = 90.0,
        target_duration: float = 45.0,
        max_clips: int = 5,
    ):
        self.signal_keywords = set(signal_keywords or [
            "price", "cost", "రేటు", "ధర", "ఖర్చు",
            "health", "ఆరోగ్యం", "ఆసుపత్రి",
            "water", "నీరు", "వరద",
            "job", "ఉద్యోగం", "రోజువారీ",
            "government", "ప్రభుత్వం", "ఎన్నిక",
            "farmer", "రైతు", "పంట",
            "inflation", "ధరల పెరుగుదల",
        ])
        self.min_duration = min_duration
        self.max_duration = max_duration
        self.target_duration = target_duration
        self.max_clips = max_clips

    def extract_clips(self, segments: List[ASRSegment]) -> List[Clip]:
        """Return ranked clips from transcript segments."""
        if not segments:
            return []

        candidates = self._generate_candidates(segments)
        scored = [self._score_clip(clip, segments) for clip in candidates]
        scored.sort(key=lambda c: c.score, reverse=True)
        return scored[: self.max_clips]

    def _generate_candidates(self, segments: List[ASRSegment]) -> List[Clip]:
        """Generate candidate windows from segments."""
        candidates: List[Clip] = []
        n = len(segments)
        for i in range(n):
            for j in range(i, min(i + 6, n)):
                start = segments[i].start
                end = segments[j].end
                duration = end - start
                if duration < self.min_duration:
                    continue
                if duration > self.max_duration:
                    break
                text = " ".join(seg.text for seg in segments[i : j + 1])
                candidates.append(
                    Clip(
                        start=start,
                        end=end,
                        text=text,
                        score=0.0,
                    )
                )
        return candidates

    def _score_clip(self, clip: Clip, all_segments: List[ASRSegment]) -> Clip:
        """Score a single candidate clip."""
        duration = clip.end - clip.start
        keyword_hits = sum(1 for kw in self.signal_keywords if kw.lower() in clip.text.lower())
        words = clip.text.split()
        word_count = len(words)

        # Duration score: peak at target_duration, taper off.
        duration_score = max(0.0, 1.0 - abs(duration - self.target_duration) / self.target_duration)

        # Keyword score: normalize by word count.
        keyword_score = min(1.0, keyword_hits / max(1, word_count / 10))

        # Sentiment shift: detect contrast words.
        contrast_words = {"but", "however", "actually", "truth", "real", "కానీ", "నిజం", "అసలు"}
        contrast_hits = sum(1 for w in contrast_words if w in clip.text.lower())
        contrast_score = min(1.0, contrast_hits / 2.0)

        # Hook density: transitions between subtopics (rough proxy: sentence breaks).
        transitions = clip.text.count("。") + clip.text.count("।") + clip.text.count("?") + clip.text.count("!")
        hook_score = min(1.0, transitions / 2.0)

        score = (
            0.4 * keyword_score +
            0.25 * duration_score +
            0.2 * contrast_score +
            0.15 * hook_score
        )

        clip.score = round(score, 3)
        clip.hook_sentence = self._extract_hook_sentence(clip.text)
        clip.metadata = {
            "keyword_hits": keyword_hits,
            "duration": duration,
            "word_count": word_count,
        }
        return clip

    def _extract_hook_sentence(self, text: str) -> str:
        """Pick the first sentence containing a signal keyword as the hook."""
        sentences = re.split(r"[।.!?]\s+", text)
        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence:
                continue
            for kw in self.signal_keywords:
                if kw.lower() in sentence.lower():
                    return sentence
        return sentences[0].strip() if sentences else text
