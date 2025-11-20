# core/chaldean_mapping.py
CHAldEAN_MAP = {
    'A': 1, 'B': 2, 'C': 3, 'D': 4, 'E': 5, 'F': 8, 'G': 3, 'H': 5,
    'I': 1, 'J': 1, 'K': 2, 'L': 3, 'M': 4, 'N': 5, 'O': 7, 'P': 8,
    'Q': 1, 'R': 2, 'S': 3, 'T': 4, 'U': 6, 'V': 6, 'W': 6, 'X': 5,
    'Y': 1, 'Z': 7
}

def name_to_chaldean_number(name: str):
    """
    Convert name to total + reduced number.
    Returns (total_sum, reduced_digit)
    """
    total = 0
    for ch in name.upper():
        if ch in CHAldEAN_MAP:
            total += CHAldEAN_MAP[ch]
    reduced = total
    while reduced > 9 and reduced not in (11, 22, 33):
        reduced = sum(int(d) for d in str(reduced))
    return total, reduced
