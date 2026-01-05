import json
import re
from openai import OpenAI


class OpenAIWordChecker:
    def __init__(
        self,
        client: OpenAI,
        model: str = "gpt-4o-mini",
        enabled: bool = True
    ):
        self.client = client
        self.model = model
        self.enabled = enabled

    # ==========================
    # TEST KẾT NỐI OPENAI
    # ==========================
    def test_connection(self) -> bool:
        try:
            self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": "OK"}],
                temperature=0
            )
            return True
        except Exception:
            return False

    # ==========================
    # KIỂM TRA TỪ NGHI NGỜ
    # ==========================
    def check_words(self, words: list[str], context: str) -> dict:
        """
        words   : danh sách từ nghi ngờ
        context : câu gốc
        return  : dict {word: {"status": "đúng/sai", "suggestion": ""}}
        """

        if not self.enabled or not words:
            return {}

        prompt = f"""
Bạn là bộ kiểm tra lỗi CHÍNH TẢ TIẾNG VIỆT dùng trong VĂN BẢN HÀNH CHÍNH.

Câu gốc:
"{context}"

Danh sách từ cần kiểm tra:
{", ".join(words)}

NHIỆM VỤ:
- Kiểm tra TỪNG TỪ RIÊNG LẺ
- KHÔNG suy đoán theo ngữ cảnh
- Từ bị lặp ký tự (Cônng, Thựcc, kkhi) → SAI
- Từ thừa hoặc thiếu ký tự → SAI
- Từ đúng chính tả → ĐÚNG
- Viết hoa cơ quan (UBND, HĐND) → ĐÚNG

CHỈ TRẢ JSON HỢP LỆ – KHÔNG GIẢI THÍCH – KHÔNG THÊM CHỮ.

ĐỊNH DẠNG BẮT BUỘC:
{{
  "từ": {{
    "status": "đúng" | "sai",
    "suggestion": "từ đúng nếu sai, rỗng nếu đúng"
  }}
}}

VÍ DỤ:
{{
  "Cônng": {{ "status": "sai", "suggestion": "Công" }},
  "Thựcc": {{ "status": "sai", "suggestion": "Thực" }},
  "UBND": {{ "status": "đúng", "suggestion": "" }}
}}
"""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0
            )

            content = response.choices[0].message.content.strip()

            # 🔥 LẤY JSON ĐẦU TIÊN (CHỐNG AI NÓI LINH TINH)
            match = re.search(r"\{[\s\S]*\}", content)
            if not match:
                raise ValueError("AI không trả về JSON hợp lệ")

            return json.loads(match.group())

        except Exception as e:
            return {
                "_error": {
                    "status": "error",
                    "suggestion": str(e)
                }
            }
