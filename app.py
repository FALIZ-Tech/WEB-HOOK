from flask import Flask, request, jsonify
from config import (
    VERIFY_TOKEN, DEFAULT_LANGUAGE, SUPPORTED_LANGUAGES,
    CONFIDENCE_THRESHOLD, MAX_HISTORY_TURNS, get_lang_name
)
from database import (
    init_db, get_user_by_phone, create_user, update_user_lang,
    add_conversation, get_history, log_language_detection
)
from language_detector import detect_language
from prompt_engine import build_system_prompt
from llm_handler import generate_llm_response
from whatsapp_utils import send_whatsapp_message, parse_incoming_whatsapp

app = Flask(__name__)
init_db()

def process_message(from_phone: str, text: str):
    try:
        user = get_user_by_phone(from_phone)
        is_new = user is None
        if is_new:
            user_id = create_user(from_phone)
            user = get_user_by_phone(from_phone)
        else:
            user_id = user["id"]

        detected_lang, confidence = detect_language(text)

        if confidence < CONFIDENCE_THRESHOLD:
            effective_lang = user["user_language_preference"] if user and user["user_language_preference"] else DEFAULT_LANGUAGE
        else:
            effective_lang = detected_lang

        is_supported = effective_lang in SUPPORTED_LANGUAGES
        log_language_detection(from_phone, detected_lang, confidence, is_supported)

        if is_supported:
            response_lang = effective_lang
            if is_new or not user.get("user_language_preference"):
                update_user_lang(user_id, response_lang)
        else:
            response_lang = DEFAULT_LANGUAGE
            if is_new or not user.get("user_language_preference"):
                update_user_lang(user_id, DEFAULT_LANGUAGE)

        history = get_history(user_id, MAX_HISTORY_TURNS)
        recent_langs = [h.get("detected_language", "") for h in history] + [detected_lang]

        system_prompt = build_system_prompt(
            user_pref=user.get("user_language_preference") if user else None,
            current_lang=response_lang,
            recent_langs=recent_langs
        )

        bot_response = generate_llm_response(system_prompt, history, text)

        if not is_supported:
            lang_name = get_lang_name(detected_lang)
            supported = ", ".join([get_lang_name(l) for l in SUPPORTED_LANGUAGES])
            intro = f"I detected you're writing in {lang_name}. I currently support {supported}. I'll respond in English for now — just reply in any supported language and I'll switch!"
            bot_response = f"{intro}\n\n{bot_response}"

        add_conversation(user_id, text, bot_response, detected_lang)
        send_whatsapp_message(from_phone, bot_response)
        return bot_response

    except Exception as e:
        print(f"[PROCESS] Critical error for {from_phone}: {e}")
        err = "Sorry, something went wrong on our side. Please try again in a moment."
        send_whatsapp_message(from_phone, err)
        return err

@app.route("/webhook", methods=["GET", "POST"])
def webhook():
    if request.method == "GET":
        mode = request.args.get("hub.mode")
        token = request.args.get("hub.verify_token")
        challenge = request.args.get("hub.challenge", "")
        if mode == "subscribe" and token == VERIFY_TOKEN:
            return challenge, 200
        return "Verification failed", 403

    # POST
    try:
        payload = request.get_json(silent=True) or {}
        messages = parse_incoming_whatsapp(payload)
        for phone, text in messages:
            if phone and text:
                process_message(phone, text)
        return jsonify({"status": "ok"}), 200
    except Exception as e:
        print(f"[WEBHOOK] Error: {e}")
        return jsonify({"status": "error"}), 500

@app.route("/")
def health():
    return "Faliz Multilingual WhatsApp Bot is running perfectly."

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
