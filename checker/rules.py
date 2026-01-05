import re
from .common_mistakes import *
from checker.exclude_words import *

class Rule:
    name = "Base rule"
    enabled = True

    def check(self, line_no: int, text: str):
        """
        Trả về list lỗi hoặc dict {suspects: []}
        """
        return []
    
class ExtraSpaceRule(Rule):
    name = "Khoảng trắng thừa"

    def check(self, line_no, text):
        errors = []
        if re.search(r"\s{2,}", text):
            errors.append("Có nhiều hơn 1 khoảng trắng liên tiếp")
        return errors
    
class PunctuationRule(Rule):
    name = "Dấu câu"

    def check(self, line_no, text):
        errors = []

        if not text.strip():
            return errors

        # 1️⃣ Khoảng trắng sai trước dấu câu (không áp dụng cho ...)
        if re.search(r"\s+[,.!?;:]", text):
            errors.append("Khoảng trắng sai trước dấu câu")

        # 2️⃣ Lặp dấu câu – loại trừ '...'
        # Bắt ,,  ..  !!  ??  ;;  ::  nhưng KHÔNG bắt ...
        if re.search(r"(,{2,}|\.(?!\.\.)\.{2,}|[!?;:]{2,})", text):
            errors.append("Lặp dấu câu")

        return errors

class CapitalizeRule(Rule):
    name = "Viết hoa đầu câu"

    def check(self, line_no, text):
        if text and text[0].islower():
            return ["Không viết hoa chữ cái đầu câu"]
        return []


class CommonMistakeRule(Rule):
    name = "Lỗi chính tả & hành chính thường gặp"

    def check(self, line_no, text):
        errors = []
        lower = text.lower()
        for wrong, correct in COMMON_MISTAKES.items():
            if wrong in lower:
                errors.append(f"Sai chính tả: '{wrong}' → '{correct}'")
        return errors


class DuplicateWordRule(Rule):
    name = "Lặp từ"

    def check(self, line_no, text):
        errors = []
        words = text.lower().split()
        for i in range(len(words) - 1):
            if words[i] == words[i + 1]:
                errors.append(f"Lặp từ '{words[i]}'")
        return errors

class RepeatedPhraseRule(Rule):
    name = "Lặp cụm từ"

    def check(self, line_no, text):
        errors = []
        words = text.lower().split()
        for i in range(len(words) - 2):
            if words[i] == words[i+1]:
                errors.append(f"Lặp từ '{words[i]}'")
            if words[i:i+2] == words[i+2:i+4]:
                phrase = " ".join(words[i:i+2])
                errors.append(f"Lặp cụm từ '{phrase}'")
        return errors

class NumberFormatRule(Rule):
    name = "Định dạng số & ngày tháng"
    severity = "warning"

    def check(self, line_no, text):
        errors = []

        # ==================================================
        # 1. SỐ BẮT ĐẦU BẰNG 0 (≥ 3 chữ số) – LOẠI TRỪ SỐ TIỀN / SỐ LƯỢNG
        # ==================================================
        for m in re.finditer(r"\b0\d{2,}\b", text):
            number = m.group()

            # ❌ BỎ QUA nếu là số có phân tách hàng nghìn
            # Ví dụ: 1.058, 72.000, 1.245.060
            if re.search(r"\d{1,3}([.,]\d{3})+", text):
                continue

            errors.append(
                f"Số '{number}' có số 0 đứng trước không hợp lệ"
            )

        # ==================================================
        # 2. NGÀY / THÁNG / NĂM (dd/mm/yyyy)
        # ==================================================
        date_pattern = r"\b(\d{1,2})/(\d{1,2})/(\d{4})\b"

        for match in re.finditer(date_pattern, text):
            day_str, month_str, year_str = match.groups()
            date_str = match.group()

            day = int(day_str)
            month = int(month_str)

            if not (1 <= day <= 31):
                errors.append(f"Ngày không hợp lệ: '{date_str}'")
                continue

            if not (1 <= month <= 12):
                errors.append(f"Tháng không hợp lệ: '{date_str}'")
                continue

            if len(day_str) != 2:
                errors.append(
                    f"Ngày phải ghi đủ 2 chữ số (vd: 01): '{date_str}'"
                )

            if month in (1, 2) and len(month_str) != 2:
                errors.append(
                    f"Tháng {month} phải ghi dạng 0{month}: '{date_str}'"
                )

            if month >= 3 and month_str.startswith("0"):
                errors.append(
                    f"Tháng {month} không được có số 0 phía trước: '{date_str}'"
                )

        return errors


class CapitalAbbreviationRule(Rule):
    name = "Viết hoa cơ quan nhà nước"
    auto_fix = True

    def check(self, line_no, text):
        errors = []
        for wrong, correct in UPPERCASE_MISTAKES.items():
            pattern = r'\b' + wrong + r'\b'
            if re.search(pattern, text):
                errors.append(f"Nên viết '{correct}' thay cho '{wrong}'")
        return errors

class LegalBasisDashRule(Rule):
    name = "Thể thức 'Căn cứ'"

    def check(self, line_no, text):
        errors = []

        # Bắt các dạng gạch đầu dòng trước "Căn cứ"
        pattern = r"^\s*[–—-]\s*Căn cứ\b"

        if re.search(pattern, text):
            errors.append("Không dùng gạch đầu dòng trước từ 'Căn cứ'")

        return errors


class LineEndValidPunctuationRule(Rule):
    name = "Ký tự kết thúc dòng"

    def check(self, line_no, text):
        errors = []

        text = text.rstrip()

        if not text:
            return errors  # bỏ qua dòng trống

        # Các ký tự KHÔNG được phép kết thúc dòng
        forbidden_pattern = r"[,\-–—@#$%&*/\\|~]$"

        if re.search(forbidden_pattern, text):
            errors.append(
                "Dòng không được kết thúc bằng dấu ',' hoặc ký tự đặc biệt"
            )

        return errors






class RepeatedCharRule:
    name = "Lặp ký tự bất thường"

    def check(self, line_no, text):
        errors = []
        if not text.strip():
            return errors

        # tìm các ký tự lặp
        pattern = r"([A-Za-zÀ-ỹ])\1+"

        for match in re.finditer(pattern, text):
            start, end = match.span()
            word = match.group()

            # mở rộng ra cả cụm từ chứa ký tự lặp
            left = re.search(r"[A-Za-zÀ-ỹ&/.\-]+$", text[:start])
            right = re.search(r"^[A-Za-zÀ-ỹ&/.\-]+", text[end:])
            full_word = (
                (left.group() if left else "") +
                word +
                (right.group() if right else "")
            )

            # bỏ qua nếu thuộc danh sách loại trừ
            if is_excluded(full_word):
                continue

            errors.append(f"Từ '{full_word}' có ký tự lặp bất thường")

        return errors
