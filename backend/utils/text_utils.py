# backend/utils/text_utils.py
import re
import difflib
from typing import List, Set

# Basic cleaning: lowercase, remove extra punctuation but keep words and numbers
def clean_text(s: str) -> str:
    if not isinstance(s, str):
        return ""
    s = s.strip().lower()
    # keep letters, numbers and spaces
    s = re.sub(r"[^a-z0-9\s]", " ", s)
    s = re.sub(r"\s+", " ", s)
    return s.strip()

# Simple Hinglish normalizer: common romanized hindi -> english equivalents or tokens
_HINGlish_MAP = {
    # greetings / small talk
    "namaste": "hello", "kaise": "how", "kaise ho": "how are you",
    "kaise ho?": "how are you",
    "kya": "what", "kya hai": "what is", "kya hai?": "what is",
    "tumhara": "your", "tumhara naam": "your name", "tumhara naam kya hai": "what is your name",
    "mera": "my", "resume": "resume", "job": "job",
    "interview": "interview", "mujhe": "i need", "kaam": "work",
    "kaise karu": "how to do", "kaise karen": "how to do", "kaise banaen": "how to make",
    "kaise banaye": "how to make", "kahan": "where", "kab": "when", "kitna": "how much",
    "dhanyavaad": "thank you", "shukriya": "thank you", "bye": "bye", "alvida":"bye"
}

def hinglish_normalize(s: str) -> str:
    # Replace exact keys first (longer keys first)
    if not s:
        return s
    text = s
    # Try replace multi-word keys first
    for k in sorted(_HINGlish_MAP.keys(), key=lambda x: -len(x)):
        if k in text:
            text = text.replace(k, _HINGlish_MAP[k])
    # final cleanup
    text = re.sub(r"\s+", " ", text).strip()
    return text

# Build vocabulary (unique words) from cleaned question list
def simple_spell_corrector_build(clean_questions: List[str]) -> Set[str]:
    vocab = set()
    for q in clean_questions:
        for w in q.split():
            if len(w) >= 2:
                vocab.add(w)
    return vocab

# Simple token-level spell correction using difflib.get_close_matches
# For each token not in vocab, try to find a close match (threshold by similarity)
def simple_spell_correct(s: str, vocab: Set[str], cutoff: float = 0.78) -> str:
    if not s or not vocab:
        return s
    tokens = s.split()
    corrected_tokens = []
    for t in tokens:
        if t in vocab:
            corrected_tokens.append(t)
            continue
        # short tokens often not correctable
        if len(t) <= 2:
            corrected_tokens.append(t)
            continue
        # find close match
        matches = difflib.get_close_matches(t, vocab, n=1, cutoff=cutoff)
        if matches:
            corrected_tokens.append(matches[0])
        else:
            corrected_tokens.append(t)
    return " ".join(corrected_tokens)
