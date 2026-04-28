import fitz  # PyMuPDF
import docx
import pytesseract
from PIL import Image
import io
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import spacy
import os
os.environ["TOKENIZERS_PARALLELISM"] = "false"

from transformers import pipeline

summarizer = pipeline(
    "summarization",
    model="facebook/bart-large-cnn",
    device=-1  # CPU; use 0 if GPU
)

def extract_text_from_file(filepath: str):
    # PDF
    if filepath.lower().endswith(".pdf"):
        doc = fitz.open(filepath)
        text = ""

        for page in doc:
            # Try normal text extraction first
            extracted = page.get_text().strip()
            
            if extracted:
                text += extracted + "\n"
            else:
                # OCR fallback for scanned PDFs
                pix = page.get_pixmap()
                img_bytes = pix.tobytes("png")
                img = Image.open(io.BytesIO(img_bytes))
                ocr_text = pytesseract.image_to_string(img)
                text += ocr_text + "\n"

        return text

    # DOCX
    if filepath.lower().endswith(".docx"):
        document = docx.Document(filepath)
        return "\n".join([para.text for para in document.paragraphs])

    # Images (JPG, PNG, TIFF)
    if filepath.lower().endswith((".png", ".jpg", ".jpeg", ".tiff")):
        img = Image.open(filepath)
        return pytesseract.image_to_string(img)

    # TXT
    try:
        with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
            return f.read()
    except:
        return ""


# import spacy
# nlp = spacy.load("en_core_web_sm")

# import re

# def classify_document(text: str):
#     if not text or len(text.strip()) < 50:
#         return "General"

#     text = text.lower()
#     doc = nlp(text)

#     # -------------------------------
#     # CATEGORY DEFINITIONS
#     # -------------------------------
#     scores = {
#         "Administrative": 0,
#         "Academics": 0,
#         "Research": 0,
#         "Policies": 0,
#         "Official Issuances": 0,
#         "News & Events": 0,
#     }

#     CATEGORY_KEYWORDS = {
#         "Administrative": [
#             "office", "administrative", "committee", "meeting",
#             "attendance", "secretariat", "endorsement"
#         ],
#         "Academics": [
#             "student", "faculty", "curriculum", "course",
#             "syllabus", "lecture", "midterm", "finals"
#         ],
#         "Research": [
#             "research", "study", "methodology", "abstract",
#             "publication", "innovation", "terminal report"
#         ],
#         "Policies": [
#             "policy", "policies", "guidelines", "procedures",
#             "provision", "manual", "compliance"
#         ],
#         "Official Issuances": [
#             "memorandum", "circular", "resolution",
#             "special order", "directive", "moa", "agreement"
#         ],
#         "News & Events": [
#             "event", "activity", "workshop", "celebration"
#         ]
#     }

#     STRONG_PATTERNS = {
#         "Policies": [
#             r"policies,\s*guidelines\s*and\s*procedures",
#             r"accounting manual",
#             r"this circular is issued to prescribe",
#             r"repealing clause",
#         ],
#         "Official Issuances": [
#             r"circular no\.",
#             r"memorandum of agreement",
#             r"resolution no\.",
#             r"effectivity",
#         ],
#         "Research": [
#             r"terminal report",
#             r"narrative report"
#         ]
#     }

#     PRIORITY_ORDER = [
#         "Policies",
#         "Official Issuances",
#         "Research",
#         "Academics",
#         "Administrative",
#         "News & Events"
#     ]

#     # -------------------------------
#     # 1. KEYWORD SCORING
#     # -------------------------------
#     for category, words in CATEGORY_KEYWORDS.items():
#         for w in words:
#             if w in text:
#                 scores[category] += 2

#     # -------------------------------
#     # 2. STRONG PATTERN MATCHING
#     # -------------------------------
#     for category, patterns in STRONG_PATTERNS.items():
#         for pattern in patterns:
#             if re.search(pattern, text):
#                 scores[category] += 15

#     # -------------------------------
#     # 3. STRUCTURAL SIGNALS
#     # -------------------------------
#     if "manual" in text:
#         scores["Policies"] += 25

#     if "prescribing" in text:
#         scores["Policies"] += 20

#     if "effectivity" in text:
#         scores["Official Issuances"] += 10

#     if "abstract" in text and "research" in text:
#         scores["Research"] += 10

#     # -------------------------------
#     # 4. SAFE NER SIGNALS ONLY
#     # -------------------------------
#     for ent in doc.ents:
#         if ent.label_ == "DATE":
#             scores["Official Issuances"] += 1

#     # -------------------------------
#     # 5. POLICY OVERRIDE (CRITICAL FIX)
#     # -------------------------------
#     # if scores["Policies"] >= 30:
#     #     return "Policies"
    
#     # Detect strong Official Issuance signals FIRST
#     if (
#         "special order" in text
#         or "office special order" in text
#         or "so no" in text
#     ):
#         return "Official Issuances"


#     # Policy override ONLY for real policy documents
#     if (
#         scores["Policies"] >= 30
#         and (
#             "manual" in text
#             or "policy" in text
#             or "policies, guidelines and procedures" in text
#             or "prescribing" in text
#         )
#     ):
#         return "Policies"

#     # -------------------------------
#     # 6. CLEAN ADMIN NOISE
#     # -------------------------------
#     if scores["Administrative"] < 5:
#         scores["Administrative"] = 0

#     # -------------------------------
#     # 7. FINAL DECISION (PRIORITY-AWARE)
#     # -------------------------------
#     sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)
#     top_score = sorted_scores[0][1]

#     if top_score < 3:
#         return "General"

#     top_candidates = [cat for cat, score in sorted_scores if score >= top_score - 2]

#     for category in PRIORITY_ORDER:
#         if category in top_candidates:
#             return category

#     return sorted_scores[0][0]


# import spacy
# nlp = spacy.load("en_core_web_sm")

# import re

# def classify_document(text: str):
#     if not text or len(text.strip()) < 50:
#         return "General"

#     text = text.lower()
#     doc = nlp(text)

#     # -------------------------------
#     # CATEGORY DEFINITIONS
#     # -------------------------------
#     scores = {
#         "Administrative": 0,
#         "Academics": 0,
#         "Research": 0,
#         "Policies": 0,
#         "Official Issuances": 0,
#         "News & Events": 0,
#     }

#     CATEGORY_KEYWORDS = {
#         "Administrative": [
#             "office", "administrative", "committee", "meeting",
#             "attendance", "secretariat", "endorsement"
#         ],
#         "Academics": [
#             "student", "faculty", "curriculum", "course",
#             "syllabus", "lecture", "midterm", "finals"
#         ],
#         "Research": [
#             "research", "study", "methodology", "abstract",
#             "publication", "innovation", "terminal report"
#         ],
#         "Policies": [
#             "policy", "policies", "guidelines", "procedures",
#             "provision", "manual", "compliance"
#         ],
#         "Official Issuances": [
#             "memorandum", "circular", "resolution",
#             "special order", "directive", "moa", "agreement"
#         ],
#         "News & Events": [
#             "event", "activity", "workshop", "celebration"
#         ]
#     }

#     STRONG_PATTERNS = {
#         "Policies": [
#             r"policies,\s*guidelines\s*and\s*procedures",
#             r"accounting manual",
#             r"this circular is issued to prescribe",
#             r"repealing clause",
#         ],
#         "Official Issuances": [
#             r"circular no\.",
#             r"memorandum of agreement",
#             r"resolution no\.",
#             r"effectivity",
#         ],
#         "Research": [
#             r"terminal report",
#             r"narrative report"
#         ]
#     }

#     PRIORITY_ORDER = [
#         "Policies",
#         "Official Issuances",
#         "Research",
#         "Academics",
#         "Administrative",
#         "News & Events"
#     ]

#     # -------------------------------
#     # 0. 🔥 HARD RULES (TOP PRIORITY)
#     # -------------------------------

#     # ✅ Official Issuance detection (strong)
#     if re.search(r"(special order|office special order|so no\.?\s*\d+)", text):
#         return "Official Issuances"

#     if re.search(r"(memorandum|circular no\.|resolution no\.)", text):
#         return "Official Issuances"

#     # ✅ Manual / User Guide detection (NEW FIX)
#     if re.search(r"(user manual|manual\s*\d+\.\d+|system manual)", text):
#         return "Policies"

#     # OCR fallback (procedural structure)
#     if "manual" in text and (
#         "how to" in text or
#         "step 1" in text or
#         "step 2" in text
#     ):
#         return "Policies"

#     # -------------------------------
#     # 1. KEYWORD SCORING
#     # -------------------------------
#     for category, words in CATEGORY_KEYWORDS.items():
#         for w in words:
#             if w in text:
#                 scores[category] += 2

#     # -------------------------------
#     # 2. STRONG PATTERN MATCHING
#     # -------------------------------
#     for category, patterns in STRONG_PATTERNS.items():
#         for pattern in patterns:
#             if re.search(pattern, text):
#                 scores[category] += 15

#     # -------------------------------
#     # 3. STRUCTURAL SIGNALS
#     # -------------------------------
#     if "manual" in text:
#         scores["Policies"] += 25

#     if "prescribing" in text:
#         scores["Policies"] += 20

#     if "effectivity" in text:
#         scores["Official Issuances"] += 10

#     if "abstract" in text and "research" in text:
#         scores["Research"] += 10

#     # -------------------------------
#     # 4. SAFE NER SIGNALS ONLY
#     # -------------------------------
#     for ent in doc.ents:
#         if ent.label_ == "DATE":
#             scores["Official Issuances"] += 1

#     # -------------------------------
#     # 5. POLICY OVERRIDE (REFINED)
#     # -------------------------------
#     if (
#         scores["Policies"] >= 30
#         and (
#             "manual" in text
#             or "policy" in text
#             or "guidelines" in text
#             or "procedures" in text
#             or "prescribing" in text
#         )
#     ):
#         return "Policies"

#     # -------------------------------
#     # 6. CLEAN ADMIN NOISE
#     # -------------------------------
#     if scores["Administrative"] < 5:
#         scores["Administrative"] = 0

#     # -------------------------------
#     # 7. FINAL DECISION (PRIORITY-AWARE)
#     # -------------------------------
#     sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)
#     top_score = sorted_scores[0][1]

#     if top_score < 3:
#         return "General"

#     top_candidates = [cat for cat, score in sorted_scores if score >= top_score - 2]

#     for category in PRIORITY_ORDER:
#         if category in top_candidates:
#             return category

#     return sorted_scores[0][0]

# import spacy
# import re

# nlp = spacy.load("en_core_web_sm")


# def classify_document(text: str):
#     if not text or len(text.strip()) < 50:
#         return "General"

#     text = text.lower()
#     doc = nlp(text)

#     # -------------------------------
#     # CATEGORY DEFINITIONS
#     # -------------------------------
#     scores = {
#         "Administrative": 0,
#         "Academics": 0,
#         "Research": 0,
#         "Policies": 0,
#         "Official Issuances": 0,
#         "News & Events": 0,
#     }

#     CATEGORY_KEYWORDS = {
#         "Administrative": [
#             "office", "administrative", "committee", "meeting",
#             "attendance", "secretariat", "endorsement"
#         ],
#         "Academics": [
#             "student", "faculty", "curriculum", "course",
#             "syllabus", "lecture", "midterm", "finals"
#         ],
#         "Research": [
#             "research", "study", "methodology", "abstract",
#             "publication", "innovation", "terminal report"
#         ],
#         "Policies": [
#             "policy", "policies", "guidelines", "procedures",
#             "provision", "manual", "compliance"
#         ],
#         "Official Issuances": [
#             "memorandum", "circular", "resolution",
#             "special order", "directive", "moa", "agreement"
#         ],
#         "News & Events": [
#             "event", "activity", "workshop", "celebration"
#         ]
#     }

#     STRONG_PATTERNS = {
#         "Policies": [
#             r"policies,\s*guidelines\s*and\s*procedures",
#             r"accounting manual",
#             r"repealing clause",
#         ],
#         "Official Issuances": [
#             r"\bcircular\s*no\.",
#             r"\bmemorandum\s*no\.",
#             r"\bresolution\s*no\.",
#             r"memorandum of agreement",
#             r"effectivity",
#         ],
#         "Research": [
#             r"terminal report",
#             r"narrative report"
#         ]
#     }

#     PRIORITY_ORDER = [
#         "Policies",
#         "Official Issuances",
#         "Research",
#         "Academics",
#         "Administrative",
#         "News & Events"
#     ]

#     # -------------------------------
#     # 0. 🔥 HARD RULES (TOP PRIORITY)
#     # -------------------------------

#     # ✅ 1. MANUAL DETECTION (HIGHEST PRIORITY)
#     if "manual" in text:
#         return "Policies"

#     # ✅ 2. STRICT OFFICIAL ISSUANCE DETECTION
#     if re.search(r"(special order|office special order|so no\.?\s*\d+)", text):
#         return "Official Issuances"

#     if re.search(r"\b(memorandum|circular|resolution)\s*(no\.|#)", text):
#         return "Official Issuances"

#     # -------------------------------
#     # 1. KEYWORD SCORING
#     # -------------------------------
#     for category, words in CATEGORY_KEYWORDS.items():
#         for w in words:
#             if w in text:
#                 scores[category] += 2

#     # -------------------------------
#     # 2. STRONG PATTERN MATCHING
#     # -------------------------------
#     for category, patterns in STRONG_PATTERNS.items():
#         for pattern in patterns:
#             if re.search(pattern, text):
#                 scores[category] += 15

#     # -------------------------------
#     # 3. STRUCTURAL SIGNALS
#     # -------------------------------
#     if "manual" in text:
#         scores["Policies"] += 25

#     if "prescribing" in text:
#         scores["Policies"] += 20

#     if "effectivity" in text:
#         scores["Official Issuances"] += 10

#     if "abstract" in text and "research" in text:
#         scores["Research"] += 10

#     # -------------------------------
#     # 4. SAFE NER SIGNALS
#     # -------------------------------
#     for ent in doc.ents:
#         if ent.label_ == "DATE":
#             scores["Official Issuances"] += 1

#     # -------------------------------
#     # 5. POLICY OVERRIDE
#     # -------------------------------
#     if (
#         scores["Policies"] >= 30
#         and (
#             "policy" in text
#             or "guidelines" in text
#             or "procedures" in text
#             or "prescribing" in text
#         )
#     ):
#         return "Policies"

#     # -------------------------------
#     # 6. CLEAN ADMIN NOISE
#     # -------------------------------
#     if scores["Administrative"] < 5:
#         scores["Administrative"] = 0

#     # -------------------------------
#     # 7. FINAL DECISION
#     # -------------------------------
#     sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)
#     top_score = sorted_scores[0][1]

#     if top_score < 3:
#         return "General"

#     top_candidates = [cat for cat, score in sorted_scores if score >= top_score - 2]

#     for category in PRIORITY_ORDER:
#         if category in top_candidates:
#             return category

#     return sorted_scores[0][0]

# import spacy
# import re

# nlp = spacy.load("en_core_web_sm")


# def classify_document(text: str):
#     if not text or len(text.strip()) < 50:
#         return "General"

#     text = text.lower()
#     doc = nlp(text)

#     # -------------------------------
#     # CATEGORY DEFINITIONS
#     # -------------------------------
#     scores = {
#         "Administrative": 0,
#         "Academics": 0,
#         "Research": 0,
#         "Policies": 0,
#         "Official Issuances": 0,
#         "News & Events": 0,
#     }

#     CATEGORY_KEYWORDS = {
#         "Administrative": [
#             "office", "administrative", "committee", "meeting",
#             "attendance", "secretariat", "endorsement",
#             "form", "certification", "certify", "annex", "signature"
#         ],
#         "Academics": [
#             "student", "faculty", "curriculum", "course",
#             "syllabus", "lecture", "midterm", "finals"
#         ],
#         "Research": [
#             "research", "study", "methodology", "abstract",
#             "publication", "innovation", "terminal report"
#         ],
#         "Policies": [
#             "policy", "policies", "guidelines", "procedures",
#             "provision", "manual", "compliance"
#         ],
#         "Official Issuances": [
#             "memorandum", "circular", "resolution",
#             "special order", "directive", "moa", "agreement"
#         ],
#         "News & Events": [
#             "event", "activity", "workshop", "celebration"
#         ]
#     }

#     STRONG_PATTERNS = {
#         "Policies": [
#             r"policies,\s*guidelines\s*and\s*procedures",
#             r"accounting manual",
#             r"repealing clause",
#         ],
#         "Official Issuances": [
#             r"\bcircular\s*no\.",
#             r"\bmemorandum\s*no\.",
#             r"\bresolution\s*no\.",
#             r"memorandum of agreement",
#             r"effectivity",
#         ],
#         "Research": [
#             r"terminal report",
#             r"narrative report"
#         ]
#     }

#     PRIORITY_ORDER = [
#         "Policies",
#         "Official Issuances",
#         "Research",
#         "Academics",
#         "Administrative",
#         "News & Events"
#     ]

#     # -------------------------------
#     # 0. 🔥 HARD RULES (TOP PRIORITY)
#     # -------------------------------

#     # ✅ 1. MANUAL DETECTION
#     if "manual" in text:
#         return "Policies"

#     # ✅ 2. OFFICIAL ISSUANCES
#     if re.search(r"(special order|office special order|so no\.?\s*\d+)", text):
#         return "Official Issuances"

#     if re.search(r"\b(memorandum|circular|resolution)\s*(no\.|#)", text):
#         return "Official Issuances"

#     # ✅ 3. FORM / CERTIFICATION (NEW FIX)
#     if re.search(r"(certification form|annex\s*[a-z]|do hereby certify|signature)", text):
#         return "Administrative"

#     # -------------------------------
#     # 1. KEYWORD SCORING
#     # -------------------------------
#     for category, words in CATEGORY_KEYWORDS.items():
#         for w in words:
#             if w in text:
#                 scores[category] += 2

#     # -------------------------------
#     # 2. STRONG PATTERN MATCHING
#     # -------------------------------
#     for category, patterns in STRONG_PATTERNS.items():
#         for pattern in patterns:
#             if re.search(pattern, text):
#                 scores[category] += 15

#     # -------------------------------
#     # 3. STRUCTURAL SIGNALS
#     # -------------------------------
#     if "manual" in text:
#         scores["Policies"] += 25

#     if "prescribing" in text:
#         scores["Policies"] += 20

#     if "effectivity" in text:
#         scores["Official Issuances"] += 10

#     if "abstract" in text and "research" in text:
#         scores["Research"] += 10

#     # -------------------------------
#     # 4. SAFE NER SIGNALS
#     # -------------------------------
#     for ent in doc.ents:
#         if ent.label_ == "DATE":
#             scores["Official Issuances"] += 1

#     # -------------------------------
#     # 5. POLICY OVERRIDE
#     # -------------------------------
#     if (
#         scores["Policies"] >= 30
#         and (
#             "policy" in text
#             or "guidelines" in text
#             or "procedures" in text
#             or "prescribing" in text
#         )
#     ):
#         return "Policies"

#     # -------------------------------
#     # 6. CLEAN ADMIN NOISE
#     # -------------------------------
#     if scores["Administrative"] < 5:
#         scores["Administrative"] = 0

#     # -------------------------------
#     # 7. FINAL DECISION
#     # -------------------------------
#     sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)
#     top_score = sorted_scores[0][1]

#     if top_score < 3:
#         return "General"

#     top_candidates = [cat for cat, score in sorted_scores if score >= top_score - 2]

#     for category in PRIORITY_ORDER:
#         if category in top_candidates:
#             return category

#     return sorted_scores[0][0]


# import spacy
# import re

# nlp = spacy.load("en_core_web_sm")


# def classify_document(text: str):
#     if not text or len(text.strip()) < 50:
#         return "General"

#     text = text.lower()
#     doc = nlp(text)

#     # -------------------------------
#     # CATEGORY DEFINITIONS
#     # -------------------------------
#     scores = {
#         "Administrative": 0,
#         "Academics": 0,
#         "Research": 0,
#         "Policies": 0,
#         "Official Issuances": 0,
#         "News & Events": 0,
#     }

#     CATEGORY_KEYWORDS = {
#         "Administrative": [
#             "office", "administrative", "committee", "meeting",
#             "attendance", "secretariat", "endorsement",
#             "form", "certification", "certify", "annex", "signature"
#         ],
#         "Academics": [
#             "student", "faculty", "curriculum", "course",
#             "syllabus", "lecture", "midterm", "finals"
#         ],
#         "Research": [
#             "research", "study", "methodology", "abstract",
#             "publication", "innovation", "terminal report"
#         ],
#         "Policies": [
#             "policy", "policies", "guidelines", "procedures",
#             "provision", "manual", "compliance"
#         ],
#         "Official Issuances": [
#             "memorandum", "circular", "resolution",
#             "special order", "directive", "moa", "agreement"
#         ],
#         "News & Events": [
#             "event", "activity", "workshop", "seminar", "training", "orientation"
#         ]
#     }

#     STRONG_PATTERNS = {
#         "Policies": [
#             r"policies,\s*guidelines\s*and\s*procedures",
#             r"accounting manual",
#             r"repealing clause",
#         ],
#         "Official Issuances": [
#             r"\bcircular\s*no\.",
#             r"\bmemorandum\s*no\.",
#             r"\bresolution\s*no\.",
#             r"memorandum of agreement",
#             r"effectivity",
#         ],
#         "Research": [
#             r"terminal report",
#             r"narrative report"
#         ]
#     }

#     PRIORITY_ORDER = [
#         "Policies",
#         "Official Issuances",
#         "Research",
#         "Academics",
#         "Administrative",
#         "News & Events"
#     ]

#     # -------------------------------
#     # 0. 🔥 HARD RULES (TOP PRIORITY)
#     # -------------------------------

#     # ✅ 1. MANUAL DETECTION
#     if "manual" in text:
#         return "Policies"

#     # ✅ 2. OFFICIAL ISSUANCES
#     if re.search(r"(special order|office special order|so no\.?\s*\d+)", text):
#         return "Official Issuances"

#     if re.search(r"\b(memorandum|circular|resolution)\s*(no\.|#)", text):
#         return "Official Issuances"

#     # ✅ 3. FORM / CERTIFICATION
#     if re.search(r"(certification form|annex\s*[a-z]|do hereby certify|signature)", text):
#         return "Administrative"

#     # ✅ 4. EVENT / WORKSHOP DETECTION (NEW FIX)
#     if re.search(r"(workshop|orientation|seminar|training|conference)", text):
#         return "News & Events"

#     # -------------------------------
#     # 1. KEYWORD SCORING
#     # -------------------------------
#     for category, words in CATEGORY_KEYWORDS.items():
#         for w in words:
#             if w in text:
#                 scores[category] += 2

#     # -------------------------------
#     # 2. STRONG PATTERN MATCHING
#     # -------------------------------
#     for category, patterns in STRONG_PATTERNS.items():
#         for pattern in patterns:
#             if re.search(pattern, text):
#                 scores[category] += 15

#     # -------------------------------
#     # 3. STRUCTURAL SIGNALS
#     # -------------------------------
#     if "manual" in text:
#         scores["Policies"] += 25

#     if "prescribing" in text:
#         scores["Policies"] += 20

#     if "effectivity" in text:
#         scores["Official Issuances"] += 10

#     if "abstract" in text and "research" in text:
#         scores["Research"] += 10

#     # -------------------------------
#     # 4. SAFE NER SIGNALS
#     # -------------------------------
#     for ent in doc.ents:
#         if ent.label_ == "DATE":
#             scores["Official Issuances"] += 1

#     # -------------------------------
#     # 5. POLICY OVERRIDE
#     # -------------------------------
#     if (
#         scores["Policies"] >= 30
#         and (
#             "policy" in text
#             or "guidelines" in text
#             or "procedures" in text
#             or "prescribing" in text
#         )
#     ):
#         return "Policies"

#     # -------------------------------
#     # 6. CLEAN ADMIN NOISE
#     # -------------------------------
#     if scores["Administrative"] < 5:
#         scores["Administrative"] = 0

#     # -------------------------------
#     # 7. FINAL DECISION
#     # -------------------------------
#     sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)
#     top_score = sorted_scores[0][1]

#     if top_score < 3:
#         return "General"

#     top_candidates = [cat for cat, score in sorted_scores if score >= top_score - 2]

#     for category in PRIORITY_ORDER:
#         if category in top_candidates:
#             return category

#     return sorted_scores[0][0]

# import spacy
# import re

# nlp = spacy.load("en_core_web_sm")


# def classify_document(text: str):
#     if not text or len(text.strip()) < 50:
#         return "General"

#     text = text.lower()
#     doc = nlp(text)

#     # -------------------------------
#     # CATEGORY DEFINITIONS
#     # -------------------------------
#     scores = {
#         "Administrative": 0,
#         "Academics": 0,
#         "Research": 0,
#         "Policies": 0,
#         "Official Issuances": 0,
#         "News & Events": 0,
#     }

#     CATEGORY_KEYWORDS = {
#         "Administrative": [
#             "office", "administrative", "committee", "meeting",
#             "attendance", "secretariat", "endorsement",
#             "form", "certification", "certify", "annex", "signature"
#         ],
#         "Academics": [
#             "student", "faculty", "curriculum", "course",
#             "syllabus", "lecture", "midterm", "finals"
#         ],
#         "Research": [
#             "research", "study", "methodology", "abstract",
#             "publication", "innovation", "terminal report"
#         ],
#         "Policies": [
#             "policy", "policies", "guidelines", "procedures",
#             "provision", "manual", "compliance"
#         ],
#         "Official Issuances": [
#             "memorandum", "circular", "resolution",
#             "special order", "directive", "moa", "agreement"
#         ],
#         "News & Events": [
#             "event", "activity", "workshop", "seminar", "training", "orientation", "conference"
#         ]
#     }

#     STRONG_PATTERNS = {
#         "Policies": [
#             r"policies,\s*guidelines\s*and\s*procedures",
#             r"accounting manual",
#             r"repealing clause",
#         ],
#         "Official Issuances": [
#             r"\bcircular\s*no\.",
#             r"\bmemorandum\s*no\.",
#             r"\bresolution\s*no\.",
#             r"memorandum of agreement",
#             r"effectivity",
#         ],
#         "Research": [
#             r"terminal report",
#             r"narrative report"
#         ]
#     }

#     PRIORITY_ORDER = [
#         "Policies",
#         "Official Issuances",
#         "Research",
#         "Academics",
#         "Administrative",
#         "News & Events"
#     ]

#     # -------------------------------
#     # 0. 🔥 HARD RULES (TOP PRIORITY)
#     # -------------------------------

#     # ✅ 1. MANUAL DETECTION
#     if "manual" in text:
#         return "Policies"

#     # ✅ 2. EVENT DETECTION (FIXED PRIORITY)
#     if re.search(r"(orientation workshop|workshop|seminar|training|conference)", text):
#         return "News & Events"

#     # ✅ 3. OFFICIAL ISSUANCES
#     if re.search(r"(special order|office special order|so no\.?\s*\d+)", text):
#         return "Official Issuances"

#     if re.search(r"\b(memorandum|circular|resolution)\s*(no\.|#)", text):
#         return "Official Issuances"

#     # ✅ 4. FORM / CERTIFICATION
#     if re.search(r"(certification form|annex\s*[a-z]|do hereby certify|signature)", text):
#         return "Administrative"

#     # -------------------------------
#     # 1. KEYWORD SCORING
#     # -------------------------------
#     for category, words in CATEGORY_KEYWORDS.items():
#         for w in words:
#             if w in text:
#                 scores[category] += 2

#     # -------------------------------
#     # 2. STRONG PATTERN MATCHING
#     # -------------------------------
#     for category, patterns in STRONG_PATTERNS.items():
#         for pattern in patterns:
#             if re.search(pattern, text):
#                 scores[category] += 15

#     # -------------------------------
#     # 3. STRUCTURAL SIGNALS
#     # -------------------------------
#     if "manual" in text:
#         scores["Policies"] += 25

#     if "prescribing" in text:
#         scores["Policies"] += 20

#     if "effectivity" in text:
#         scores["Official Issuances"] += 10

#     if "abstract" in text and "research" in text:
#         scores["Research"] += 10

#     # -------------------------------
#     # 4. SAFE NER SIGNALS
#     # -------------------------------
#     for ent in doc.ents:
#         if ent.label_ == "DATE":
#             scores["Official Issuances"] += 1

#     # -------------------------------
#     # 5. POLICY OVERRIDE (PROTECTED)
#     # -------------------------------
#     if (
#         scores["Policies"] >= 30
#         and not re.search(r"(workshop|orientation|seminar|training|conference)", text)
#         and (
#             "policy" in text
#             or "guidelines" in text
#             or "procedures" in text
#             or "prescribing" in text
#         )
#     ):
#         return "Policies"

#     # -------------------------------
#     # 6. CLEAN ADMIN NOISE
#     # -------------------------------
#     if scores["Administrative"] < 5:
#         scores["Administrative"] = 0

#     # -------------------------------
#     # 7. FINAL DECISION
#     # -------------------------------
#     sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)
#     top_score = sorted_scores[0][1]

#     if top_score < 3:
#         return "General"

#     top_candidates = [cat for cat, score in sorted_scores if score >= top_score - 2]

#     for category in PRIORITY_ORDER:
#         if category in top_candidates:
#             return category

#     return sorted_scores[0][0]

# import spacy
# import re

# nlp = spacy.load("en_core_web_sm")


# def classify_document(text: str):
#     if not text or len(text.strip()) < 50:
#         return "General"

#     text = text.lower()
#     doc = nlp(text)

#     # -------------------------------
#     # CATEGORY DEFINITIONS
#     # -------------------------------
#     scores = {
#         "Administrative": 0,
#         "Academics": 0,
#         "Research": 0,
#         "Policies": 0,
#         "Official Issuances": 0,
#         "News & Events": 0,
#     }

#     CATEGORY_KEYWORDS = {
#         "Administrative": [
#             "office", "administrative", "committee", "meeting",
#             "attendance", "secretariat", "endorsement",
#             "form", "certification", "certify", "annex", "signature",
#             "evaluation", "rating", "score", "criteria", "bidder"
#         ],
#         "Academics": [
#             "student", "faculty", "curriculum", "course",
#             "syllabus", "lecture", "midterm", "finals"
#         ],
#         "Research": [
#             "research", "study", "methodology", "abstract",
#             "publication", "innovation", "terminal report"
#         ],
#         "Policies": [
#             "policy", "policies", "guidelines", "procedures",
#             "provision", "manual", "compliance"
#         ],
#         "Official Issuances": [
#             "memorandum", "circular", "resolution",
#             "special order", "directive", "moa", "agreement"
#         ],
#         "News & Events": [
#             "event", "activity", "workshop", "seminar", "training", "orientation", "conference"
#         ]
#     }

#     STRONG_PATTERNS = {
#         "Policies": [
#             r"policies,\s*guidelines\s*and\s*procedures",
#             r"accounting manual",
#             r"repealing clause",
#         ],
#         "Official Issuances": [
#             r"\bcircular\s*no\.",
#             r"\bmemorandum\s*no\.",
#             r"\bresolution\s*no\.",
#             r"memorandum of agreement",
#             r"effectivity",
#         ],
#         "Research": [
#             r"terminal report",
#             r"narrative report"
#         ]
#     }

#     PRIORITY_ORDER = [
#         "Policies",
#         "Official Issuances",
#         "Research",
#         "Academics",
#         "Administrative",
#         "News & Events"
#     ]

#     # -------------------------------
#     # 0. 🔥 HARD RULES (TOP PRIORITY)
#     # -------------------------------

#     # ✅ 1. MANUAL DETECTION
#     if "manual" in text:
#         return "Policies"

#     # ✅ 2. EVENT DETECTION
#     if re.search(r"(orientation workshop|workshop|seminar|training|conference)", text):
#         return "News & Events"

#     # ✅ 3. OFFICIAL ISSUANCES
#     if re.search(r"(special order|office special order|so no\.?\s*\d+)", text):
#         return "Official Issuances"

#     if re.search(r"\b(memorandum|circular|resolution)\s*(no\.|#)", text):
#         return "Official Issuances"

#     # ✅ 4. FORM / CERTIFICATION
#     if re.search(r"(certification form|annex\s*[a-z]|do hereby certify|signature)", text):
#         return "Administrative"

#     # ✅ 5. EVALUATION / RATING (🔥 NEW FIX)
#     if re.search(r"(evaluation|rating|score|criteria|final rating|bidder)", text):
#         return "Administrative"

#     # -------------------------------
#     # 1. KEYWORD SCORING
#     # -------------------------------
#     for category, words in CATEGORY_KEYWORDS.items():
#         for w in words:
#             if w in text:
#                 scores[category] += 2

#     # -------------------------------
#     # 2. STRONG PATTERN MATCHING
#     # -------------------------------
#     for category, patterns in STRONG_PATTERNS.items():
#         for pattern in patterns:
#             if re.search(pattern, text):
#                 scores[category] += 15

#     # -------------------------------
#     # 3. STRUCTURAL SIGNALS
#     # -------------------------------
#     if "manual" in text:
#         scores["Policies"] += 25

#     if "prescribing" in text:
#         scores["Policies"] += 20

#     if "effectivity" in text:
#         scores["Official Issuances"] += 10

#     if "abstract" in text and "research" in text:
#         scores["Research"] += 10

#     # -------------------------------
#     # 4. SAFE NER SIGNALS
#     # -------------------------------
#     for ent in doc.ents:
#         if ent.label_ == "DATE":
#             scores["Official Issuances"] += 1

#     # -------------------------------
#     # 5. POLICY OVERRIDE (PROTECTED)
#     # -------------------------------
#     if (
#         scores["Policies"] >= 30
#         and not re.search(r"(workshop|orientation|seminar|training|conference)", text)
#         and (
#             "policy" in text
#             or "guidelines" in text
#             or "procedures" in text
#             or "prescribing" in text
#         )
#     ):
#         return "Policies"

#     # -------------------------------
#     # 6. CLEAN ADMIN NOISE
#     # -------------------------------
#     if scores["Administrative"] < 5:
#         scores["Administrative"] = 0

#     # -------------------------------
#     # 7. FINAL DECISION
#     # -------------------------------
#     sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)
#     top_score = sorted_scores[0][1]

#     if top_score < 3:
#         return "General"

#     top_candidates = [cat for cat, score in sorted_scores if score >= top_score - 2]

#     for category in PRIORITY_ORDER:
#         if category in top_candidates:
#             return category

#     return sorted_scores[0][0]


# import spacy
# import re

# nlp = spacy.load("en_core_web_sm")


# def classify_document(text: str):
#     if not text or len(text.strip()) < 50:
#         return "General"

#     text = text.lower()
#     doc = nlp(text)

#     # -------------------------------
#     # CATEGORY DEFINITIONS
#     # -------------------------------
#     scores = {
#         "Administrative": 0,
#         "Academics": 0,
#         "Research": 0,
#         "Policies": 0,
#         "Official Issuances": 0,
#         "News & Events": 0,
#     }

#     CATEGORY_KEYWORDS = {
#         "Administrative": [
#             "office", "administrative", "committee", "meeting",
#             "attendance", "secretariat", "endorsement",
#             "form", "certification", "certify", "annex", "signature",
#             "evaluation", "rating", "score", "criteria", "bidder"
#         ],
#         "Academics": [
#             "student", "faculty", "curriculum", "course",
#             "syllabus", "lecture", "midterm", "finals"
#         ],
#         "Research": [
#             "research", "study", "methodology", "abstract",
#             "publication", "innovation", "terminal report"
#         ],
#         "Policies": [
#             "policy", "policies", "guidelines", "procedures",
#             "provision", "manual", "compliance"
#         ],
#         "Official Issuances": [
#             "memorandum", "circular", "resolution",
#             "special order", "directive", "moa", "agreement"
#         ],
#         "News & Events": [
#             "event", "activity", "workshop", "seminar",
#             "training", "orientation", "conference"
#         ]
#     }

#     STRONG_PATTERNS = {
#         "Policies": [
#             r"policies,\s*guidelines\s*and\s*procedures",
#             r"accounting manual",
#             r"repealing clause",
#         ],
#         "Official Issuances": [
#             r"\bcircular\s*no\.",
#             r"\bmemorandum\s*no\.",
#             r"\bresolution\s*no\.",
#             r"memorandum of agreement",
#             r"effectivity",
#         ],
#         "Research": [
#             r"terminal report",
#             r"narrative report"
#         ]
#     }

#     PRIORITY_ORDER = [
#         "Policies",
#         "Official Issuances",
#         "Research",
#         "Academics",
#         "Administrative",
#         "News & Events"
#     ]

#     # -------------------------------
#     # 0. 🔥 HARD RULES (TOP PRIORITY)
#     # -------------------------------

#     # ✅ 1. MANUAL DETECTION
#     if "manual" in text:
#         return "Policies"

#     # ✅ 2. EVENT DETECTION (FIXED - CONTEXT AWARE)
#     if (
#         re.search(r"(orientation workshop|workshop on|seminar on|training on|conference on)", text)
#         and re.search(r"(date|venue|time|schedule)", text)
#     ):
#         return "News & Events"

#     # # ✅ 3. OFFICIAL ISSUANCES
#     # if re.search(r"(special order|office special order|so no\.?\s*\d+)", text):
#     #     return "Official Issuances"
    
#     # ✅ 3. OFFICIAL ISSUANCES (FIXED - HEADER ONLY)
#     header = text[:300]

#     if re.search(r"(special order|office special order|so no\.?\s*\d+)", header):
#         return "Official Issuances"

#     if re.search(r"\b(memorandum|circular|resolution)\s*(no\.|#)", header):
#         return "Official Issuances"

#     if re.search(r"\b(memorandum|circular|resolution)\s*(no\.|#)", text):
#         return "Official Issuances"

#     # ✅ 4. FORM / CERTIFICATION
#     if re.search(r"(certification form|annex\s*[a-z]|do hereby certify|signature)", text):
#         return "Administrative"

#     # ✅ 5. EVALUATION / RATING
#     if re.search(r"(evaluation|rating|score|criteria|final rating|bidder)", text):
#         return "Administrative"

#     # -------------------------------
#     # 1. KEYWORD SCORING
#     # -------------------------------
#     for category, words in CATEGORY_KEYWORDS.items():
#         for w in words:
#             if w in text:
#                 scores[category] += 2

#     # -------------------------------
#     # 2. STRONG PATTERN MATCHING
#     # -------------------------------
#     for category, patterns in STRONG_PATTERNS.items():
#         for pattern in patterns:
#             if re.search(pattern, text):
#                 scores[category] += 15

#     # -------------------------------
#     # 3. STRUCTURAL SIGNALS
#     # -------------------------------
#     if "manual" in text:
#         scores["Policies"] += 25

#     if "prescribing" in text:
#         scores["Policies"] += 20

#     if "effectivity" in text:
#         scores["Official Issuances"] += 10

#     if "abstract" in text and "research" in text:
#         scores["Research"] += 10

#     # -------------------------------
#     # 4. SAFE NER SIGNALS
#     # -------------------------------
#     for ent in doc.ents:
#         if ent.label_ == "DATE":
#             scores["Official Issuances"] += 1

#     # -------------------------------
#     # 5. POLICY OVERRIDE (PROTECTED)
#     # -------------------------------
#     if (
#         scores["Policies"] >= 30
#         and not re.search(r"(workshop|orientation|seminar|training|conference)", text)
#         and (
#             "policy" in text
#             or "guidelines" in text
#             or "procedures" in text
#             or "prescribing" in text
#         )
#     ):
#         return "Policies"

#     # -------------------------------
#     # 6. CLEAN ADMIN NOISE
#     # -------------------------------
#     if scores["Administrative"] < 5:
#         scores["Administrative"] = 0

#     # -------------------------------
#     # 7. FINAL DECISION
#     # -------------------------------
#     sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)
#     top_score = sorted_scores[0][1]

#     if top_score < 3:
#         return "General"

#     top_candidates = [cat for cat, score in sorted_scores if score >= top_score - 2]

#     for category in PRIORITY_ORDER:
#         if category in top_candidates:
#             return category

#     return sorted_scores[0][0]


import spacy
import re

nlp = spacy.load("en_core_web_sm")


# -------------------------------
# 🧠 TITLE EXTRACTION
# -------------------------------
# def extract_title(text: str):
#     lines = text.split("\n")
#     lines = [l.strip() for l in lines if l.strip()]

#     for line in lines[:10]:
#         if len(line) < 5:
#             continue
#         if line.isupper() or len(line.split()) <= 15:
#             return line.lower()

#     return lines[0].lower() if lines else ""

def extract_title(text: str):
    lines = text.split("\n")
    lines = [l.strip() for l in lines if l.strip()]

    TITLE_KEYWORDS = [
        "plan", "manual", "report", "guidelines",
        "policy", "framework", "proposal",
        "continuity", "implementation"
    ]

    for line in lines[:15]:  # expand scan range
        clean_line = line.lower()

        # ❌ Skip organization names
        if re.search(r"(college|university|department|office)", clean_line):
            continue

        # ✅ Prefer meaningful titles
        if any(k in clean_line for k in TITLE_KEYWORDS):
            return clean_line

        # fallback candidate
        if 5 < len(clean_line.split()) <= 15:
            return clean_line

    return lines[0].lower() if lines else ""


def classify_document(text: str):
    if not text or len(text.strip()) < 50:
        return "General"

    text = text.lower()
    doc = nlp(text)

    # 🔥 Extract title
    title = extract_title(text)

    # -------------------------------
    # CATEGORY DEFINITIONS
    # -------------------------------
    scores = {
        "Administrative": 0,
        "Academics": 0,
        "Research": 0,
        "Policies": 0,
        "Official Issuances": 0,
        "News & Events": 0,
    }

    CATEGORY_KEYWORDS = {
        "Administrative": [
            "office", "administrative", "committee", "meeting",
            "attendance", "secretariat", "endorsement",
            "form", "certification", "certify", "annex", "signature",
            "evaluation", "rating", "score", "criteria", "bidder"
        ],
        "Academics": [
            "student", "faculty", "curriculum", "course",
            "syllabus", "lecture", "midterm", "finals"
        ],
        "Research": [
            "research", "study", "methodology", "abstract",
            "publication", "innovation", "terminal report"
        ],
        "Policies": [
            "policy", "policies", "guidelines", "procedures",
            "provision", "manual", "compliance"
        ],
        "Official Issuances": [
            "memorandum", "circular", "resolution",
            "special order", "directive", "moa", "agreement"
        ],
        "News & Events": [
            "event", "activity", "workshop", "seminar",
            "training", "orientation", "conference"
        ]
    }

    STRONG_PATTERNS = {
        "Policies": [
            r"policies,\s*guidelines\s*and\s*procedures",
            r"accounting manual",
            r"repealing clause",
        ],
        "Official Issuances": [
            r"\bcircular\s*no\.",
            r"\bmemorandum\s*no\.",
            r"\bresolution\s*no\.",
            r"memorandum of agreement",
            r"effectivity",
        ],
        "Research": [
            r"terminal report",
            r"narrative report"
        ]
    }

    PRIORITY_ORDER = [
        "Policies",
        "Official Issuances",
        "Research",
        "Academics",
        "Administrative",
        "News & Events"
    ]

    # -------------------------------
    # 🔥 0. TITLE-BASED INTENT DETECTION
    # -------------------------------

    if "manual" in title:
        return "Policies"

    if re.search(r"(plan|framework|guidelines|policy)", title):
        return "Policies"

    if re.search(r"(workshop|seminar|training|conference|orientation)", title):
        return "News & Events"

    if re.search(r"(memorandum|circular|resolution|special order)", title):
        return "Official Issuances"

    if re.search(r"(form|certification)", title):
        return "Administrative"

    if re.search(r"(evaluation|rating|score)", title):
        return "Administrative"

    # -------------------------------
    # 🔥 1. HARD RULES
    # -------------------------------

    if "manual" in text:
        return "Policies"

    # Event (context-aware)
    if (
        re.search(r"(orientation workshop|workshop on|seminar on|training on|conference on)", text)
        and re.search(r"(date|venue|time|schedule)", text)
    ):
        return "News & Events"

    # Issuances (HEADER ONLY)
    header = text[:300]

    if re.search(r"(special order|office special order|so no\.?\s*\d+)", header):
        return "Official Issuances"

    if re.search(r"\b(memorandum|circular|resolution)\s*(no\.|#)", header):
        return "Official Issuances"

    # Form
    if re.search(r"(certification form|annex\s*[a-z]|do hereby certify|signature)", text):
        return "Administrative"

    # Evaluation
    if re.search(r"(evaluation|rating|score|criteria|final rating|bidder)", text):
        return "Administrative"

    # -------------------------------
    # 2. KEYWORD SCORING
    # -------------------------------
    for category, words in CATEGORY_KEYWORDS.items():
        for w in words:
            if w in text:
                scores[category] += 2

    # -------------------------------
    # 3. STRONG PATTERN MATCHING
    # -------------------------------
    for category, patterns in STRONG_PATTERNS.items():
        for pattern in patterns:
            if re.search(pattern, text):
                scores[category] += 15

    # -------------------------------
    # 4. STRUCTURAL SIGNALS
    # -------------------------------
    if "manual" in text:
        scores["Policies"] += 25

    if "prescribing" in text:
        scores["Policies"] += 20

    if "effectivity" in text:
        scores["Official Issuances"] += 10

    if "abstract" in text and "research" in text:
        scores["Research"] += 10

    # -------------------------------
    # 5. SAFE NER SIGNALS
    # -------------------------------
    for ent in doc.ents:
        if ent.label_ == "DATE":
            scores["Official Issuances"] += 1

    # -------------------------------
    # 6. POLICY OVERRIDE (PROTECTED)
    # -------------------------------
    if (
        scores["Policies"] >= 30
        and not re.search(r"(workshop|orientation|seminar|training|conference)", text)
        and (
            "policy" in text
            or "guidelines" in text
            or "procedures" in text
            or "prescribing" in text
        )
    ):
        return "Policies"

    # -------------------------------
    # 7. CLEAN ADMIN NOISE
    # -------------------------------
    if scores["Administrative"] < 5:
        scores["Administrative"] = 0

    # -------------------------------
    # 8. FINAL DECISION
    # -------------------------------
    sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    top_score = sorted_scores[0][1]

    if top_score < 3:
        return "General"

    top_candidates = [cat for cat, score in sorted_scores if score >= top_score - 2]

    for category in PRIORITY_ORDER:
        if category in top_candidates:
            return category

    return sorted_scores[0][0]


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
