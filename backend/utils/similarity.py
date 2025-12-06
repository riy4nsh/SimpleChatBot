# backend/utils/similarity.py
import importlib
import numpy as np

try:
    sbert_spec = importlib.util.find_spec("sentence_transformers")
    if sbert_spec is not None:
        from sentence_transformers import SentenceTransformer
        SBERT_AVAILABLE = True
    else:
        SBERT_AVAILABLE = False
except Exception:
    SBERT_AVAILABLE = False

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

class SimilarityEngine:
    """
    Uses SBERT embeddings if available; otherwise TF-IDF.
    most_similar(query) -> (best_index, score)
    """
    def __init__(self, references):
        self.refs = references
        self.use_sbert = SBERT_AVAILABLE
        if self.use_sbert:
            try:
                self.model = SentenceTransformer('all-MiniLM-L6-v2')
                self.ref_emb = self.model.encode(self.refs, convert_to_numpy=True)
            except Exception as e:
                # fallback to TF-IDF if model load fails
                print("[SimilarityEngine] SBERT init failed:", e)
                self.use_sbert = False
                self._init_tfidf()
        else:
            self._init_tfidf()

    def _init_tfidf(self):
        self.vectorizer = TfidfVectorizer(ngram_range=(1,2), lowercase=True)
        self.ref_vec = self.vectorizer.fit_transform(self.refs)

    def most_similar(self, query):
        if self.use_sbert:
            q_emb = self.model.encode([query], convert_to_numpy=True)
            sims = cosine_similarity(q_emb, self.ref_emb)[0]
        else:
            q_vec = self.vectorizer.transform([query])
            sims = cosine_similarity(q_vec, self.ref_vec)[0]
        idx = int(np.argmax(sims))
        return idx, sims[idx]
