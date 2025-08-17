import re
from difflib import SequenceMatcher
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

def clean_text(text):
    """Lowercase, remove punctuation and extra whitespace."""
    if not isinstance(text, str):
        return ""
    text = text.lower()
    text = re.sub(r'[^\w\s]', '', text)  # Remove punctuation
    text = re.sub(r'\s+', ' ', text)     # Collapse multiple spaces
    return text.strip()

def is_similar(text1, text2, threshold=0.75):
    """Fuzzy matching similarity check."""
    if not text1 or not text2:
        return False
    try:
        return SequenceMatcher(None, text1, text2).ratio() >= threshold
    except Exception:
        return False

def cosine_sim(text1, text2, threshold=0.75):
    """TF-IDF cosine similarity check."""
    try:
        vectorizer = TfidfVectorizer(stop_words='english')
        vectors = vectorizer.fit_transform([text1, text2])
        sim = cosine_similarity(vectors[0], vectors[1])[0][0]
        return sim >= threshold
    except Exception as e:
        print(f"[⚠️ TF-IDF Error] {e}")
        return False

def deduplicate_articles(articles, threshold=0.75):
    """
    Remove duplicates based on combined text similarity (title, description, full_text)
    using fuzzy and cosine similarity.
    """
    unique = []
    seen_texts = []

    for article in articles:
        if not article.get("title") and not article.get("url"):
            continue

        combined = " ".join([
            article.get("title", ""),
            article.get("description", ""),
            article.get("full_text", "")
        ]).strip()

        cleaned = clean_text(combined)
        if not cleaned:
            continue

        duplicate_found = False
        for seen in seen_texts:
            if is_similar(cleaned, seen, threshold):
                duplicate_found = True
                break
            if cosine_sim(cleaned, seen, threshold):
                duplicate_found = True
                break

        if not duplicate_found:
            unique.append(article)
            seen_texts.append(cleaned)

    print(f"✅ Deduplicated: {len(unique)} unique out of {len(articles)}")
    return unique
