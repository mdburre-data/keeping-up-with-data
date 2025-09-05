from sentence_transformers import SentenceTransformer
from rapidfuzz import fuzz
import numpy as np

model = SentenceTransformer("all-MiniLM-L6-v2")

def cluster_terms(terms, threshold=0.8):
    """
    Cluster similar fashion queries.
    threshold = cosine similarity cutoff
    """
    if not terms:
        return []

    embeddings = model.encode(terms, normalize_embeddings=True)
    clusters = []
    used = set()

    for i, term in enumerate(terms):
        if i in used:
            continue
        group = [term]
        used.add(i)
        for j in range(i + 1, len(terms)):
            if j in used:
                continue
            sim = np.dot(embeddings[i], embeddings[j])
            if sim > threshold or fuzz.ratio(term, terms[j]) > 80:
                group.append(terms[j])
                used.add(j)
        clusters.append(group)
    return clusters
