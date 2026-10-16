"""Small deterministic paragraph language heuristics, without network calls."""
from __future__ import annotations

import re
import unicodedata

LANGUAGES = ("fr", "en", "ja", "zh", "ko")
FR = set("le la les et de un une des que qui dans pour avec sur par pas ne ce se son sa ses mon ma mes nous vous ils elles est".split())
EN = set("the and of to a an in for with on by not is this that his her their my your we you they are be have has from as".split())
ZH = set("的一是不了人我在有他这为之大来以个中上们到说国和地也子时道出而要于就下得可你年生自会那后能对着事其里所去行过家十用发天如然作方成者多日都三小二无同经法当起与好看学")
JA = set("日一国会人年大十二本中長出三時行見月分後前生五間上東四今金九入学高円子外八六下来気小七山話女北午百書先名川千水半男西電校語土木聞食車何南万毎白天母火右読友左休父雨")


def detect(paragraph: str, fallback: str = "fr", forced: str = "auto") -> str:
    """Detect FR/EN/JA/ZH/KO, retaining fallback for ambiguous short text."""
    if forced in LANGUAGES:
        return forced
    text = unicodedata.normalize("NFKC", paragraph)
    letters = [c for c in text if c.isalpha()]
    if not letters:
        return fallback
    if sum(0xAC00 <= ord(c) <= 0xD7AF or 0x1100 <= ord(c) <= 0x11FF
           or 0x3130 <= ord(c) <= 0x318F for c in letters) / len(letters) >= .3:
        return "ko"
    if any(0x3040 <= ord(c) <= 0x30FF for c in letters):
        return "ja"
    han = [c for c in letters if 0x3400 <= ord(c) <= 0x9FFF
           or 0x20000 <= ord(c) <= 0x3134F]
    if han:
        if len(han) < 50:
            return fallback if fallback in ("ja", "zh") else "zh"
        return "ja" if sum(c in JA for c in han) > sum(c in ZH for c in han) else "zh"
    words = re.findall(r"[^\W\d_]+", text.casefold())
    fr, en = sum(w in FR for w in words), sum(w in EN for w in words)
    if re.search("[àâçéèêëîïôûùœ]", text, re.I) and not re.search("[äöüßñ¿]", text, re.I):
        return "fr"
    if fr + en < 10:
        return fallback
    return "fr" if fr > en else "en" if en > fr else fallback
