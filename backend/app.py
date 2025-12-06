# backend/app.py
import os
import time
import json
import re
import importlib
from typing import List, Tuple
from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
from utils.text_utils import clean_text, hinglish_normalize, simple_spell_corrector_build, simple_spell_correct

# Try to import sentence-transformers (SBERT)
SBERT_AVAILABLE = importlib.util.find_spec("sentence_transformers") is not None
if SBERT_AVAILABLE:
    from sentence_transformers import SentenceTransformer

# Try to import sklearn vectorizer (should be installed)
from sklearn.feature_extraction.text import TfidfVectorizer

app = FastAPI(title="ReyMini - Enhanced Similarity Backend")

# CORS (adjust origins in production)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
RESP_PATH = os.path.join(BASE_DIR, "responses.json")

with open(RESP_PATH, "r", encoding="utf-8") as f:
    RAW_DATA = json.load(f)

# Preprocess dataset questions & answers
ORIG_QUESTIONS = [item.get("question", "").strip() for item in RAW_DATA]
ANSWERS = [item.get("answer", "") for item in RAW_DATA]

# Build cleaned question forms (for vectorization / embeddings)
CLEAN_QUESTIONS = []
for q in ORIG_QUESTIONS:
    q1 = clean_text(q)
    q2 = hinglish_normalize(q1)
    CLEAN_QUESTIONS.append(q2)

# Build simple spell-corrector vocabulary from dataset tokens
SPELL_VOCAB = simple_spell_corrector_build(CLEAN_QUESTIONS)

# Similarity backend: prefer SBERT if available, otherwise TF-IDF
use_sbert = False
if SBERT_AVAILABLE:
    try:
        model = SentenceTransformer('all-MiniLM-L6-v2')
        Q_EMB = model.encode(CLEAN_QUESTIONS, convert_to_numpy=True)
        use_sbert = True
        print("[INFO] Using SBERT (all-MiniLM-L6-v2) for semantic matching.")
    except Exception as e:
        print("[WARN] SBERT load failed, falling back to TF-IDF. Error:", e)
        use_sbert = False

if not use_sbert:
    vectorizer = TfidfVectorizer(ngram_range=(1,2), lowercase=True)
    Q_VEC = vectorizer.fit_transform(CLEAN_QUESTIONS)
    print("[INFO] Using TF-IDF vectorizer for matching (fallback).")

# Stats
_scores: List[float] = []
_total_queries = 0

class Query(BaseModel):
    q: str

def compute_similarity(query: str) -> Tuple[np.ndarray, np.ndarray]:
    """
    Returns (indices_sorted_desc, scores_sorted_desc)
    """
    if use_sbert:
        q_emb = model.encode([query], convert_to_numpy=True)
        sims = cosine_similarity(q_emb, Q_EMB)[0]
    else:
        q_vec = vectorizer.transform([query])
        sims = cosine_similarity(q_vec, Q_VEC)[0]
    idxs_sorted = sims.argsort()[::-1]
    scores_sorted = sims[idxs_sorted]
    return idxs_sorted, scores_sorted

@app.post("/reply")
def reply(payload: Query):
    """
    Main reply endpoint:
    - cleans & normalizes query
    - optional spell-correction based on dataset vocab
    - computes top-3 matches and applies thresholds
    - logs scores and running average to terminal
    """
    global _scores, _total_queries

    raw_q = payload.q or ""
    raw_q = raw_q.strip()
    if raw_q == "":
        return {"answer": "Kuch type karo pehle.", "score": 0.0}

    # Cleaning + hinglish normalization
    q = clean_text(raw_q)
    q = hinglish_normalize(q)

    # Spell correction (token-level) — helps typos
    q_corrected = simple_spell_correct(q, SPELL_VOCAB)
    if q_corrected != q:
        corrected_used = True
        q = q_corrected
    else:
        corrected_used = False

    start = time.time()
    idxs, scores = compute_similarity(q)
    elapsed_ms = (time.time() - start) * 1000.0

    # Top-3 candidates
    top_k = min(3, len(idxs))
    top_idxs = idxs[:top_k]
    top_scores = scores[:top_k]

    best_idx = int(top_idxs[0])
    best_score = float(top_scores[0])

    # Update stats
    _scores.append(best_score)
    _total_queries += 1
    avg_score = sum(_scores) / len(_scores) if _scores else 0.0

    # Terminal logging
    print("----------------------------------------------------------------")
    print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Query: \"{raw_q}\"")
    if corrected_used:
        print(f" -> Spell-corrected query to: \"{q}\"")
    print(f" -> Best match idx: {best_idx} | Score: {best_score:.4f} | Time: {elapsed_ms:.1f} ms")
    # show top-3 brief
    for rank, (i, s) in enumerate(zip(top_idxs, top_scores), start=1):
        snippet = ORIG_QUESTIONS[int(i)][:120].replace("\n"," ")
        print(f"   {rank}. (score={s:.4f}) [{i}] {snippet}")
    print(f" -> Total queries: {_total_queries} | Running avg score: {avg_score:.4f}")
    print("----------------------------------------------------------------")

    # Threshold logic
    if best_score >= 0.65:
        return {"answer": ANSWERS[best_idx], "score": best_score}
    if 0.45 <= best_score < 0.65:
        # Provide the best answer but mention partial confidence
        return {
            "answer": f"{ANSWERS[best_idx]}",
            "score": best_score
        }
    # low confidence -> ask for rephrase
    return {"answer": "I’m not fully sure about that. Could you rephrase the question?", "score": best_score}

@app.get("/stats")
def stats():
    avg_score = sum(_scores)/len(_scores) if _scores else 0.0
    return {"total_queries": _total_queries, "running_avg_score": avg_score, "use_sbert": use_sbert}
