import re
from typing import List
from src.core.interfaces.normalizer import TextNormalizerInterface
from src.domain.nlp.dictionary import LexiconManager

UNITS = ["", "một", "hai", "ba", "bốn", "năm", "sáu", "bảy", "tám", "chín"]

def read_three_digits(n: int, is_first: bool = False) -> str:
    h = n // 100
    t = (n % 100) // 10
    u = n % 10
    
    res = []
    if h > 0:
        res.append(f"{UNITS[h]} trăm")
    elif not is_first:
        res.append("không trăm")
    
    if t == 0:
        if u > 0 and (h > 0 or not is_first):
            res.append("không trăm" if h == 0 and not is_first else "lẻ")
            res.append(UNITS[u])
        elif u > 0:
            res.append(UNITS[u])
    elif t == 1:
        res.append("mười")
        if u == 1:
            res.append("một")
        elif u == 5:
            res.append("lăm")
        elif u > 0:
            res.append(UNITS[u])
    else:
        res.append(f"{UNITS[t]} mươi")
        if u == 1:
            res.append("mốt")
        elif u == 4:
            res.append("tư")
        elif u == 5:
            res.append("lăm")
        elif u > 0:
            res.append(UNITS[u])

    return " ".join(res).strip()

def number_to_vietnamese(number_str: str) -> str:
    clean_num = re.sub(r'[^\d]', '', number_str)
    if not clean_num:
        return number_str
    
    num = int(clean_num)
    if num == 0:
        return "không"

    units = ["", "nghìn", "triệu", "tỷ"]
    groups = []
    
    temp = num
    while temp > 0:
        groups.append(temp % 1000)
        temp //= 1000

    parts = []
    for i in range(len(groups) - 1, -1, -1):
        g = groups[i]
        if g == 0:
            continue
        g_text = read_three_digits(g, is_first=(i == len(groups) - 1))
        unit = units[i % 4]
        if unit:
            parts.append(f"{g_text} {unit}")
        else:
            parts.append(g_text)
            
    return " ".join(parts).strip()

ROMAN_MAP = {
    "XXI": "hai mươi mốt",
    "XX": "hai mươi",
    "XIX": "mười chín",
    "XVIII": "mười tám",
    "XVII": "mười bảy",
    "XVI": "mười sáu",
    "XV": "mười lăm",
    "XIV": "mười bốn",
    "XIII": "mười ba",
    "XII": "mười hai",
    "XI": "mười một",
    "X": "mười",
    "IX": "chín",
    "VIII": "tám",
    "VII": "bảy",
    "VI": "sáu",
    "V": "năm",
    "IV": "bốn",
    "III": "ba",
    "II": "hai",
    "I": "một"
}

class VietnameseTextNormalizer(TextNormalizerInterface):
    """Complete rule-based Vietnamese NLP Normalizer."""

    def __init__(self, lexicon_mgr: LexiconManager = None):
        self.lexicon_mgr = lexicon_mgr or LexiconManager()

    def normalize(self, text: str) -> str:
        if not text:
            return ""

        # 1. Expand Abbreviations
        text = self.lexicon_mgr.replace_abbreviations(text)

        # 2. Normalize Dates (e.g. 20/07/2026 or 20-07-2026)
        def replace_date(match):
            day, month, year = match.group(1), match.group(2), match.group(3)
            d_str = number_to_vietnamese(day)
            m_str = number_to_vietnamese(month)
            y_str = number_to_vietnamese(year)
            return f"ngày {d_str} tháng {m_str} năm {y_str}"
        text = re.sub(r'\b(\d{1,2})[/-](\d{1,2})[/-](\d{4})\b', replace_date, text)

        # 3. Normalize Times (e.g. 09:30 or 14:05:30)
        def replace_time(match):
            h, m = match.group(1), match.group(2)
            h_str = number_to_vietnamese(h)
            m_str = number_to_vietnamese(m)
            return f"{h_str} giờ {m_str} phút"
        text = re.sub(r'\b(\d{1,2}):(\d{2})\b', replace_time, text)

        # 4. Normalize Currency (e.g. 100.000đ, 100.000 VNĐ, $50)
        def replace_vnd(match):
            amount = match.group(1).replace('.', '').replace(',', '')
            return f"{number_to_vietnamese(amount)} đồng"
        text = re.sub(r'(\d+(?:\.\d{3})+|\d+)\s*(?:đ|VNĐ|vnd)\b', replace_vnd, text, flags=re.IGNORECASE)

        def replace_usd(match):
            amount = match.group(1).replace('.', '').replace(',', '')
            return f"{number_to_vietnamese(amount)} đô la"
        text = re.sub(r'\$\s*(\d+)', replace_usd, text)

        # 5. Normalize Measurements & Units (e.g. 50km, 25°C, 10m)
        text = re.sub(r'(\d+)\s*°C\b', lambda m: f"{number_to_vietnamese(m.group(1))} độ C", text)
        text = re.sub(r'(\d+)\s*km\b', lambda m: f"{number_to_vietnamese(m.group(1))} ki lô mét", text, flags=re.IGNORECASE)
        text = re.sub(r'(\d+)\s*m\b', lambda m: f"{number_to_vietnamese(m.group(1))} mét", text, flags=re.IGNORECASE)
        text = re.sub(r'(\d+)\s*cm\b', lambda m: f"{number_to_vietnamese(m.group(1))} xen ti mét", text, flags=re.IGNORECASE)
        text = re.sub(r'(\d+)\s*kg\b', lambda m: f"{number_to_vietnamese(m.group(1))} ki lô gam", text, flags=re.IGNORECASE)
        text = re.sub(r'(\d+)\s*%\b', lambda m: f"{number_to_vietnamese(m.group(1))} phần trăm", text)

        # 6. Normalize Phone Numbers (e.g., 0912345678 or 0912.345.678)
        def replace_phone(match):
            raw_phone = re.sub(r'[^\d]', '', match.group(0))
            return " ".join([number_to_vietnamese(digit) for digit in raw_phone])
        text = re.sub(r'\b0\d{2,3}[.\s]?\d{3}[.\s]?\d{3,4}\b', replace_phone, text)

        # 7. Normalize Roman Numerals (e.g. Thế kỷ XXI)
        for r_num, r_val in ROMAN_MAP.items():
            pattern = r'\b' + r_num + r'\b'
            text = re.sub(pattern, r_val, text)

        # 8. Normalize Remaining Standalone Numbers
        def replace_num(match):
            num_str = match.group(0).replace('.', '').replace(',', '')
            return number_to_vietnamese(num_str)
        text = re.sub(r'\b\d+\b', replace_num, text)

        # 9. Foreign words & symbols replacement
        text = self.lexicon_mgr.replace_foreign_words(text)
        text = self.lexicon_mgr.replace_symbols(text)

        # 10. Clean extra whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        return text
