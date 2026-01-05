import re
# ===== 1. TỪ VIẾT TẮT CỐ ĐỊNH =====
EXACT_EXCLUDES = {
    "PCCC", "PCTT", "UBND", "HĐND", "BNN", "CCCD", "QLNN", "NNMT", "ATTP",
    "MTTQ", "TTXH", "SNN", "CCHC", "NN&MT", "NN&PTNT", "NNMT", "NNPTNT",
    "Viettel",
    "TTg", "TTr", "TNHH", "II", "III", "II.", "III.", "II/", "III/"
}

def is_excluded(word: str) -> bool:
    # bỏ qua từ chứa bất kỳ chuỗi nào trong EXACT_EXCLUDES
    for ex in EXACT_EXCLUDES:
        if ex in word:
            return True
    # bỏ qua từ viết hoa toàn bộ
    if word.isupper():
        return True
    # bỏ qua các từ dạng 20/CT-TTg, 12/BC-ĐT...
    if re.match(r"\d+[/\-][A-Za-zÀ-ỹ0-9&\-]+", word):
        return True
    return False