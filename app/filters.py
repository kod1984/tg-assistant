import re

def normalize(text: str) -> str:
    return text.lower().strip()

def match_keywords(text: str, keywords: list[str]) -> list[str]:
    text = normalize(text)

    found = []
    for kw in keywords:
        pattern = rf"(?<!\w){re.escape(kw.lower())}(?!\w)"
        if re.search(pattern, text):
            found.append(kw)

    return found