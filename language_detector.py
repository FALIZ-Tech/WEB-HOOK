import re
from langdetect import detect, detect_langs, DetectorFactory, LangDetectException

DetectorFactory.seed = 42

def detect_language(text: str):
    """Returns (lang_code, confidence). Falls back safely."""
    if not text or len(text.strip()) < 3:
        return 'en', 1.0

    clean = re.sub(r'https?://\S+|www\.\S+|\d{3,}', '', text).strip()
    if len(clean) < 3:
        return 'en', 0.6

    try:
        langs = detect_langs(clean)
        if langs:
            top = langs[0]
            return top.lang, float(top.prob)
        return detect(clean), 0.75
    except LangDetectException:
        return 'en', 0.45
    except Exception:
        return 'en', 0.5
