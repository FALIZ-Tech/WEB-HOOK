import openai
from config import OPENAI_API_KEY, LLM_MODEL, MAX_TOKENS

def generate_llm_response(system_prompt: str, history: list, current_message: str) -> str:
    if not OPENAI_API_KEY:
        return "Configuration error: OpenAI API key missing. Please contact support."

    try:
        client = openai.OpenAI(api_key=OPENAI_API_KEY)
        messages = [{"role": "system", "content": system_prompt}]

        for turn in history:
            if turn.get("user_msg"):
                messages.append({"role": "user", "content": turn["user_msg"]})
            if turn.get("bot_resp"):
                messages.append({"role": "assistant", "content": turn["bot_resp"]})

        messages.append({"role": "user", "content": current_message})

        completion = client.chat.completions.create(
            model=LLM_MODEL,
            messages=messages,
            temperature=0.65,
            max_tokens=MAX_TOKENS,
            top_p=0.85
        )
        text = completion.choices[0].message.content.strip()
        return text if text else "Could you please give me a little more detail so I can help you properly?"
    except openai.APIError as e:
        print(f"[LLM] OpenAI API Error: {e}")
        return "I'm experiencing high demand right now. Please try again in a moment."
    except Exception as e:
        print(f"[LLM] Unexpected error: {e}")
        return "Sorry, a temporary issue occurred. Please try sending your message again shortly."
