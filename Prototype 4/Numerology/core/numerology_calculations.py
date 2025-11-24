# core/numerology_calculations.py
def digit_sum(n):
    return sum(int(i) for i in str(n))

def reduce_to_single_digit(n):
    while n > 9:
        n = digit_sum(n)
    return n

def compute_mulank(dob):
    """Birth Number — reduce day only"""
    return reduce_to_single_digit(dob.day)

def compute_bhagyank(dob):
    """Destiny Number — sum of full date"""
    total = digit_sum(dob.day) + digit_sum(dob.month) + digit_sum(dob.year)
    return reduce_to_single_digit(total)

def compute_name_number(name):
    """Chaldean name sum and reduction"""
    mapping = {
        'A':1,'I':1,'J':1,'Q':1,'Y':1,
        'B':2,'K':2,'R':2,
        'C':3,'G':3,'L':3,'S':3,
        'D':4,'M':4,'T':4,
        'E':5,'H':5,'N':5,'X':5,
        'U':6,'V':6,'W':6,
        'O':7,'Z':7,
        'F':8,'P':8
    }
    total = sum(mapping.get(ch.upper(), 0) for ch in name if ch.isalpha())
    reduced = reduce_to_single_digit(total)
    return total, reduced

def compute_angel_number(dob, gender):
    """Compute Angel Number"""
    year_sum = reduce_to_single_digit(digit_sum(dob.year))
    if gender.lower() == "male":
        result = 11 - year_sum
    elif gender.lower() == "female":
        result = year_sum + 4
    else:
        result = year_sum
    return reduce_to_single_digit(abs(result))

def calculate_all(name, dob, gender):
    """Combine all numerology calculations"""
    mulank = compute_mulank(dob)
    bhagyank = compute_bhagyank(dob)
    name_total, name_reduced = compute_name_number(name)
    angel_number = compute_angel_number(dob, gender)

    return {
        "Mulank": mulank,
        "Bhagyank": bhagyank,
        "Name Total": name_total,
        "Name Number": name_reduced,
        "Angel Number": angel_number
    }

