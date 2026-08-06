SYSTEM_PROMPT = "You are a disaster damage assessment assistant. Classify the visible physical infrastructure and utility damage using the image and the accompanying social media post. Return only the requested structured output."


def user_prompt(tweet_text: str) -> str:
    return f'''Accompanying social media text:\n{tweet_text}\n\nClassify the visible damage severity into exactly one of:\n- little_or_no_damage\n- mild_damage\n- severe_damage\n\nReturn valid JSON:\n{{\n  "damage_severity": "little_or_no_damage | mild_damage | severe_damage",\n  "confidence": 0.0,\n  "short_rationale": "brief evidence-based explanation"\n}}'''


def retry_prompt(tweet_text: str) -> str:
    return user_prompt(tweet_text) + "\nReturn JSON only, with no Markdown fences or additional text."

