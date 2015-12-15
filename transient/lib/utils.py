def decimal_to_string(dec):
    s = str(dec)
    return s.rstrip('0').rstrip('.') if '.' in s else s
