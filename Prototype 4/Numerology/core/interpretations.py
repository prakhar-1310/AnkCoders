# core/interpretations.py
# Placeholder short interpretations (expandable). This module provides sample text that could be displayed in the report.
INTERPRETATIONS = {
    1: "Leader, independent, origination.",
    2: "Cooperative, diplomatic, intuitive.",
    3: "Creative, communicative, optimistic.",
    4: "Practical, disciplined, grounded.",
    5: "Adventurous, freedom-loving, adaptable.",
    6: "Responsible, nurturing, harmonious.",
    7: "Introspective, analytical, spiritual.",
    8: "Ambitious, material success, authority.",
    9: "Compassionate, humanitarian, wise."
}

def get_interpretation(num: int) -> str:
    return INTERPRETATIONS.get(num, "")
