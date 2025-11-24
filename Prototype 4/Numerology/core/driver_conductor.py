# core/driver_conductor.py
"""
Driver–Conductor lookup (81 combos).
Provides:
  - DATA: dict[(driver, conductor)] = {stars_raw, rating_clean, meaning_raw, meaning_clean}
  - get_dc_analysis(driver, conductor)
  - get_phase_analysis(mulank, bhagyank)
"""

from typing import Tuple, Dict, Any, List
import re

HALF_STAR = "⯨"
FULL_STAR = "★"

def _stars_to_rating(star_str: str):
    """Convert star string like '★★★⯨' -> 3.5 (float). Return None if unknown/invalid."""
    if not star_str:
        return None
    s = str(star_str).strip()
    if s == "(?)" or "?" in s:
        return None
    # count full and half stars
    full = s.count(FULL_STAR)
    half = s.count(HALF_STAR)
    return float(full + 0.5 * half)

def _clean_meaning_raw(s: str) -> str:
    if not s:
        return ""
    # normalize whitespace
    s = s.replace("\n", " ").replace("\r", " ")
    s = re.sub(r"\s+", " ", s)
    # replace slashes with semicolon separators for consistent splitting
    s = s.replace("/", ";")
    s = s.replace(",", ";")
    # strip stray braces
    s = re.sub(r"[{}\"]", "", s)
    return s.strip().strip("; ")

def _meaning_to_keywords(s: str) -> List[str]:
    """Split meaning_raw into Title Case keywords, deduplicated, preserve multi-word phrases."""
    if not s:
        return []
    parts = [p.strip() for p in re.split(r";+", s) if p.strip()]
    keywords = []
    for p in parts:
        # remove parentheses content
        p_clean = re.sub(r"\(.*?\)", "", p).strip()
        if not p_clean:
            continue
        # Normalize whitespace, title-case
        kw = " ".join(word.capitalize() for word in re.split(r"\s+", p_clean))
        if kw and kw not in keywords:
            keywords.append(kw)
    return keywords

# -------------------------------
# DATA (81 combos)
# This data is built from the parsed user-provided blocks.
# -------------------------------
DATA_RAW = {
    # Number 1
    (1,1): {"stars": "★★★★", "meaning": "Fortunes Favourite"},
    (1,2): {"stars": "★★★★", "meaning": "Best For Navy; Water; Moon"},
    (1,3): {"stars": "★★★" + HALF_STAR, "meaning": "Best For Occult"},
    (1,4): {"stars": "★★★", "meaning": "Politics; Sun King; Rahu Influence"},
    (1,5): {"stars": "★★★★", "meaning": "Banking And Finance"},
    (1,6): {"stars": "★★★" + HALF_STAR, "meaning": "Luxury; Glamour"},
    (1,7): {"stars": "★★★", "meaning": "Best For Occult; Education; Research"},
    (1,8): {"stars": "(?)", "meaning": "Struggle; Marriage Issues; Police; Politics"},
    (1,9): {"stars": "★★★★★", "meaning": "Super Successful"},

    # Number 2
    (2,1): {"stars": "★★★" + HALF_STAR, "meaning": "Successful"},
    (2,2): {"stars": "★★", "meaning": "Best For Water Related Work; Navy; Sweets; Cold Drink"},
    (2,3): {"stars": "★★" + HALF_STAR, "meaning": "Occult Education; Healer; Teacher"},
    (2,4): {"stars": "★" + HALF_STAR, "meaning": "Struggle; Depression"},
    (2,5): {"stars": "★★★", "meaning": "Best For Property; Real Estate; Finance; MBA; Banking"},
    (2,6): {"stars": "★★" + HALF_STAR, "meaning": "Best For Sweets; Water Moon Influence; Celebration Venus Influence"},
    (2,7): {"stars": "★★" + HALF_STAR, "meaning": "Teaching; Occult"},
    (2,8): {"stars": "(?)", "meaning": "Unknown Or Unpredictable Combination"},
    (2,9): {"stars": "★", "meaning": "Struggle; Health Issues; Marriage Problems"},

    # Number 3
    (3,1): {"stars": "★★★" + HALF_STAR, "meaning": "Occult; Education; Healer; Doctor; Administrative Job"},
    (3,2): {"stars": "★★" + HALF_STAR, "meaning": "Water Related Work; Navy Work"},
    (3,3): {"stars": "★★★", "meaning": "Best For Education; Occult"},
    (3,4): {"stars": "★★", "meaning": "Good For Sales And Marketing"},
    (3,5): {"stars": "★★★", "meaning": "Excellent Communication; Anchoring; News; Reading; Acting; Teaching; Banking"},
    (3,6): {"stars": "(?)", "meaning": "Struggle; Health Issues; Marriage Issues; Anti-Combination"},
    (3,7): {"stars": "★★★★", "meaning": "Best For Education; Occult; Healing; Teaching"},
    (3,8): {"stars": "★★", "meaning": "Lawyer; Printing; Sales"},
    (3,9): {"stars": "★★★★", "meaning": "Education; Occult; Army; Administrative; Doctor"},

    # Number 4
    (4,1): {"stars": "★★★" + HALF_STAR, "meaning": "Politics"},
    (4,2): {"stars": "★★", "meaning": "Depression; Struggle"},
    (4,3): {"stars": "★★" + HALF_STAR, "meaning": "Sales And Marketing; Occult Education"},
    (4,4): {"stars": "★" + HALF_STAR, "meaning": "Best For Law; Struggle"},
    (4,5): {"stars": "★★★", "meaning": "Banking; Event Management"},
    (4,6): {"stars": "★★★", "meaning": "Media; Luxury; Glamour"},
    (4,7): {"stars": "★★★★", "meaning": "Successful; Best In Occult"},
    (4,8): {"stars": "★", "meaning": "Struggle; Excellent For Law"},
    (4,9): {"stars": "★", "meaning": "Struggle; Health Problems; Surgeries; Accidents"},

    # Number 5
    (5,1): {"stars": "★★★★", "meaning": "Successful; Finance; Loan; Property; Balanced Life"},
    (5,2): {"stars": "★★★" + HALF_STAR, "meaning": "Property"},
    (5,3): {"stars": "★★★", "meaning": "Successful"},
    (5,4): {"stars": "★★★", "meaning": "Successful"},
    (5,5): {"stars": "★★★★", "meaning": "Communication; Occult; Overall Successful; Sales And Marketing; Very Successful; Romantic; May Be Lazy"},
    (5,6): {"stars": "★★★★" + HALF_STAR, "meaning": "Life Is Successful"},
    (5,7): {"stars": "★★★", "meaning": "Occult"},
    (5,8): {"stars": "★★★", "meaning": "Property"},
    (5,9): {"stars": "★★★", "meaning": "Occult; Banking; Property; Successful"},

    # Number 6
    (6,1): {"stars": "★★★" + HALF_STAR, "meaning": "Media; Luxury; Glamour"},
    (6,2): {"stars": "★★", "meaning": "Sweet Shop; Health Issues; Marriage Issues; Successful; Media"},
    (6,3): {"stars": "(?)", "meaning": "Uncertain Or Negative Combination"},
    (6,4): {"stars": "★★★", "meaning": "Sweet Shop; Health Issues; Marriage Issues; Successful; Media"},
    (6,5): {"stars": "★★★★" + HALF_STAR, "meaning": "Super Successful"},
    (6,6): {"stars": "★★★★", "meaning": "Super Successful; Media; Film Industry; Tour And Travel"},
    (6,7): {"stars": "★★★" + HALF_STAR, "meaning": "Successful; Sports; Romantic"},
    (6,8): {"stars": "★★★", "meaning": "Best For Law"},
    (6,9): {"stars": "★★★", "meaning": "Successful; Marriage Problems; Scandals; Controversies"},

    # Number 7
    (7,1): {"stars": "★★★", "meaning": "Successful"},
    (7,2): {"stars": "★★", "meaning": "Best In Occult; Intuitive; Occult"},
    (7,3): {"stars": "★★★", "meaning": "Teaching; Healing; Occult"},
    (7,4): {"stars": "★★★", "meaning": "Successful"},
    (7,5): {"stars": "★★★", "meaning": "Occult"},
    (7,6): {"stars": "★★★★", "meaning": "Sports"},
    (7,7): {"stars": "★", "meaning": "Disappointment In Life; Marriage Life In Danger"},
    (7,8): {"stars": "★", "meaning": "Occult"},
    (7,9): {"stars": "★", "meaning": "Teaching; Occult"},

    # Number 8
    (8,1): {"stars": "(?)", "meaning": "Marriage Problems; Struggle; Saturn Represents Physical Efforts"},
    (8,2): {"stars": "(?)", "meaning": "Uncertain Or Negative Combination; Saturn Represents Physical Efforts"},
    (8,3): {"stars": "★★", "meaning": "Health Issues; Struggle; Law; Printing; Best For Law; Sales And Marketing; Struggle In Life"},
    (8,4): {"stars": "★", "meaning": "Health Issues; Struggle"},
    (8,5): {"stars": "★★★", "meaning": "Real Estate; Property"},
    (8,6): {"stars": "★★★", "meaning": "Best For Law"},
    (8,7): {"stars": "★★", "meaning": "Occult; Struggle But Good In Sports; Army"},
    (8,8): {"stars": "★", "meaning": "Occult; Struggle But Good In Sports; Army"},
    (8,9): {"stars": "★", "meaning": "Occult; Struggle But Good In Sports; Army"},

    # Number 9
    (9,1): {"stars": "★★★★", "meaning": "Successful; Army Is Best"},
    (9,2): {"stars": "★", "meaning": "Struggle; Marriage Problems"},
    (9,3): {"stars": "★★" + HALF_STAR, "meaning": "Occult; Healing"},
    (9,4): {"stars": "★" + HALF_STAR, "meaning": "Struggle; Surgeries; Health Issues"},
    (9,5): {"stars": "★★★", "meaning": "Successful"},
    (9,6): {"stars": "★★", "meaning": "Scandals; Controversies; Occult; Teaching; Army; Police; Marriage Problems"},
    (9,7): {"stars": "★", "meaning": "Scandals; Controversies; Occult; Teaching; Army; Police; Marriage Problems"},
    (9,8): {"stars": "★★", "meaning": "Scandals; Controversies; Occult; Teaching; Army; Police; Marriage Problems"},
    (9,9): {"stars": "★", "meaning": "Scandals; Controversies; Occult; Teaching; Army; Police; Marriage Problems"},
}

# Build final DATA with computed fields
DATA: Dict[Tuple[int,int], Dict[str, Any]] = {}

for key, val in DATA_RAW.items():
    stars_raw = val.get("stars")
    meaning_raw = _clean_meaning_raw(val.get("meaning", ""))
    rating = _stars_to_rating(stars_raw)
    keywords = _meaning_to_keywords(meaning_raw)
    DATA[key] = {
        "driver": key[0],
        "conductor": key[1],
        "stars_raw": stars_raw if stars_raw and stars_raw != "(?)" else None if stars_raw == "(?)" else stars_raw,
        "rating_clean": rating,
        "meaning_raw": meaning_raw,
        "meaning_clean": keywords,
    }

# Ensure all 81 combos exist (fill missing)
for d in range(1, 10):
    for c in range(1, 10):
        if (d,c) not in DATA:
            DATA[(d,c)] = {
                "driver": d,
                "conductor": c,
                "stars_raw": None,
                "rating_clean": None,
                "meaning_raw": "",
                "meaning_clean": []
            }

# Public API
def get_dc_analysis(driver: int, conductor: int) -> Dict[str, Any]:
    k = (int(driver), int(conductor))
    return DATA.get(k, {
        "driver": int(driver),
        "conductor": int(conductor),
        "stars_raw": None,
        "rating_clean": None,
        "meaning_raw": "",
        "meaning_clean": []
    })

def get_phase_analysis(mulank: int, bhagyank: int) -> Dict[str, Dict[str, Any]]:
    return {
        "0-40": get_dc_analysis(mulank, bhagyank),
        "40-80": get_dc_analysis(bhagyank, mulank)
    }

# For quick debug / display
if __name__ == "__main__":
    # simple print sample
    for k in [(5,1), (1,9), (3,6), (8,1)]:
        e = get_dc_analysis(*k)
        print(k, e)
