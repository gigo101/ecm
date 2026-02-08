import os
from pydoc import doc
import pdfplumber
import docx

os.environ["TOKENIZERS_PARALLELISM"] = "false"

from transformers import pipeline

summarizer = pipeline(
    "summarization",
    model="facebook/bart-large-cnn",
    device=-1  # CPU (use 0 if GPU)
)


import fitz  # PyMuPDF
import docx
import pytesseract
from PIL import Image
import io
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import spacy


def extract_text_from_file(filepath: str) -> str:
    """
    Extract text from PDF, DOCX, or TXT files.
    """
    if not filepath or not os.path.exists(filepath):
        return ""

    ext = os.path.splitext(filepath)[1].lower()

    try:
        # 📄 PDF
        if ext == ".pdf":
            text = ""
            with pdfplumber.open(filepath) as pdf:
                for page in pdf.pages:
                    text += page.extract_text() or ""
            return text

        # 📝 DOCX
        elif ext == ".docx":
            doc = docx.Document(filepath)
            return "\n".join(p.text for p in doc.paragraphs)

        # 📃 TXT
        elif ext == ".txt":
            with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
                return f.read()

        else:
            return ""

    except Exception as e:
        print(f"[extract_text_from_file ERROR] {e}")
        return ""


import spacy
nlp = spacy.load("en_core_web_sm")

def classify_document(text: str):
    text = text.lower()

    categories = {
        "Administrative": 0,
        "Academics": 0,
        "Research": 0,
        "Policies": 0,
        "Official Issuances": 0,   # MERGED CATEGORY
        "News & Events": 0,
    }

#MANUAL EDIT: Added "Manual" as a custom policy keyword
    # policy_patterns = [
    #     {"label": "LAW", "pattern": "GDPR"},
    #     {"label": "LAW", "pattern": "HIPAA"},
    #     {"label": "LAW", "pattern": "privacy policy"},
    #     {"label": "CUSTOM_POLICY_KEYWORD", "pattern": "Manual"} # <-- Added "Manual" here
    # ]
    # entity_ruler = nlp.add_pipe("entity_ruler", before="ner", config={"overwrite_ents": True})
    # entity_ruler.add_patterns(policy_patterns)



    research_patterns = [
    {"label": "RESEARCH_TERM", "pattern": "terminal report"},
    {"label": "RESEARCH_TERM", "pattern": "clinical trial"},
    {"label": "RESEARCH_TERM", "pattern": "peer review"},
    {"label": "RESEARCH_TERM", "pattern": "methodology section"},
    {"label": "RESEARCH_TERM", "pattern": "research paper"}
    ]
    doc = nlp(text)

    # --- NER SIGNALS ---
    for ent in doc.ents:
        if ent.label_ in ["ORG", "PERSON"]:
            categories["Administrative"] += 1

        if ent.label_ == "DATE":
            categories["Official Issuances"] += 1

        if ent.label_ in ["LAW", "CUSTOM_POLICY_KEYWORD"]:
            categories["Policies"] += 20

        if ent.label_ == "EVENT":
            categories["News & Events"] += 2
        
        if ent.label_ == "RESEARCH_TERM":
            categories["Research"] += 20

    # --- KEYWORDS FOR EACH CATEGORY ---
    keywords = {
        "Administrative": [
            "office", "admin", "administrative", "committee", "meeting",
            "secretariat", "endorsement", "attendance", "subject"
        ],
        "Academics": [
            "academic", "faculty", "student", "class", "course", "curriculum",
            "syllabus", "lecture", "load", "midterm", "finals"
        ],
        "Research": [
            "research", "study", "rde", "proposal", "ethics", "manuscript",
            "publication", "extension", "innovation", "narrative report", "terminal report", "extension"
        ],
        "Policies": [
            "policy", "guidelines", "procedures", "compliance", "section",
            "article", "provision", "manual", "repealing clauOffse", "effectivity"
        ],

        # MERGED CATEGORY
        "Official Issuances": [
            # Memos/SOs keywords
            "memo", "memorandum", "special order", "directive", "instruction",
            # Resolution keywords
            "resolution", "endorsed", "recommendation", "approved", "council", "board",
            # MOA keywords
            "memorandum of agreement", "moa", "agreement", "parties",
            "obligations", "responsibilities", "deliverables", "terms and conditions",
            "scope of work", "duration", "effectivity", "signatories"
        ],

        "News & Events": [
            "event", "activity", "program", "launching", "workshop",
            "celebration", "highlights", "gallery"
        ],
    }

    # --- KEYWORD SCORING ---
    for category, words in keywords.items():
        for w in words:
            if w in text:
                categories[category] += 2

    # --- STRUCTURAL SIGNALS (VERY IMPORTANT) ---

    # Old: "Resolution"
    if "resolution no" in text:
        categories["Official Issuances"] += 12

    # Old: "Memo / SO"
    if "special order" in text or "so no" in text:
        categories["Official Issuances"] += 10

    if "memorandum" in text:
        categories["Official Issuances"] += 8

    # Old: "MOA"
    if "memorandum of agreement" in text:
        categories["Official Issuances"] += 12

    if "this agreement" in text and "parties" in text:
        categories["Official Issuances"] += 8

    if "terms and conditions" in text:
        categories["Official Issuances"] += 5

    if "obligations of the parties" in text:
        categories["Official Issuances"] += 10

    # Other category structural boosts
    if "faculty" in text and "load" in text:
        categories["Academics"] += 7

    if "research" in text and "abstract" in text:
        categories["Research"] += 5

    if "narrative report" in text:
        categories["Research"] += 30

    if "terminal report" in text:
        categories["Research"] += 30

    if "event" in text or "activity" in text:
        categories["News & Events"] += 5
    
    if "manual" in text:
        categories["Policies"] += 15
    
    if "repealing clause" in text:
        categories["Policies"] += 15

    # --- WINNER ---
    best_category = max(categories, key=categories.get)

    if categories[best_category] < 2:
        return "General"

    return best_category



def generate_summary(text: str, query: str, embedder, top_k: int = 3):
    """
    Query-focused extractive summary
    """
    if not text.strip():
        return ""

    sentences = [s.strip() for s in text.split(".") if len(s.strip()) > 40]

    if not sentences:
        return ""

    query_embedding = embedder.encode(query).reshape(1, -1)
    sentence_embeddings = embedder.encode(sentences)

    scores = cosine_similarity(query_embedding, sentence_embeddings)[0]

    ranked = sorted(
        zip(sentences, scores),
        key=lambda x: x[1],
        reverse=True
    )

    summary_sentences = [s for s, _ in ranked[:top_k]]

    return ". ".join(summary_sentences) + "."


def generate_abstractive_summary(text: str, max_chars: int = 3000):
    """
    Generate an abstractive summary of a document.
    """

    if not text or len(text.strip()) < 200:
        return ""

    # Truncate safely (BART max tokens ~1024)
    text = text[:max_chars]

    try:
        result = summarizer(
            text,
            max_length=150,
            min_length=60,
            do_sample=False
        )
        return result[0]["summary_text"]
    except Exception as e:
        print("Summary error:", e)
        return ""



nlp = spacy.load("en_core_web_sm")

def get_relevant_sentences(text: str, query: str, embedder, top_k=5):
    if not text or not query:
        return []

    doc = nlp(text)
    sentences = [sent.text.strip() for sent in doc.sents if len(sent.text.strip()) > 20]

    if not sentences:
        return []

    sentence_embeddings = embedder.encode(sentences)
    query_embedding = embedder.encode(query).reshape(1, -1)

    similarities = cosine_similarity(query_embedding, sentence_embeddings)[0]

    ranked = sorted(
        zip(sentences, similarities),
        key=lambda x: x[1],
        reverse=True
    )

    return [
        {"sentence": s, "score": round(float(score), 3)}
        for s, score in ranked[:top_k]
        if score > 0.35
    ]
