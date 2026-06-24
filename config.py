import os

# ====================== LANGUAGE CONFIG ======================
SUPPORTED_LANGUAGES = ['en', 'es', 'fr', 'pt']
DEFAULT_LANGUAGE = 'en'
CONFIDENCE_THRESHOLD = 0.70          # below this we trust stored preference
MAX_HISTORY_TURNS = 8
MAX_TOKENS = 450

LANG_NAMES = {
    'en': 'English',
    'es': 'Spanish',
    'fr': 'French',
    'pt': 'Portuguese'
}

def get_lang_name(code: str) -> str:
    return LANG_NAMES.get(code, code.upper())

# ====================== ENVIRONMENT VARIABLES ======================
VERIFY_TOKEN = os.getenv('WHATSAPP_VERIFY_TOKEN', 'CHANGE_ME_VERIFY_TOKEN')
ACCESS_TOKEN = os.getenv('WHATSAPP_ACCESS_TOKEN', '')
PHONE_NUMBER_ID = os.getenv('WHATSAPP_PHONE_NUMBER_ID', '')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', '')
LLM_MODEL = os.getenv('LLM_MODEL', 'gpt-4o-mini')
DB_PATH = os.getenv('DB_PATH', 'conversations.db')

# Safety check (will be printed on startup)
if not all([ACCESS_TOKEN, PHONE_NUMBER_ID, OPENAI_API_KEY]):
    print("WARNING: One or more critical environment variables are missing!")
