# checker/ollama_offline.py
import ollama  # pip install ollama

class OllamaRewriter:
    def __init__(self, model: str = "llama3", enabled: bool = True):
        self.model = model
        self.enabled = enabled

    def rewrite(self, text: str, errors: list[str]) -> str:
        if not self.enabled:
            return None

        prompt = f"""
Bạn là chuyên gia tiếng Việt.
Hãy sửa đoạn văn sau:
{text}
Các lỗi đã phát hiện:
{errors}
Trả về văn bản đã sửa.
"""
        try:
            # Gọi Ollama offline trực tiếp
            response = ollama.chat(model=self.model, messages=[{"role": "user", "content": prompt}])
            return response.get("content", "").strip()
        except Exception as e:
            return None




class OllamaWordChecker:
    def __init__(self, model: str = "llama3", enabled: bool = True):
        self.model = model
        self.enabled = enabled

    def check_words(self, words: list[str], context: str) -> dict:
        """
        words   : danh sách từ nghi ngờ
        context : câu gốc
        return  : dict {word: {"status": "đúng"/"sai", "suggestion": ""}}
        """
        if not self.enabled or not words:
            return {}

        prompt = f"""
Bạn là chuyên gia tiếng Việt.
Trong câu: "{context}"
Hãy kiểm tra các từ sau có phải là lỗi gõ không:
{', '.join(words)}

Trả về JSON hợp lệ dạng:
{{
  "từ_1": {{ "status": "đúng" | "sai", "suggestion": "từ đúng nếu sai, rỗng nếu đúng" }},
  ...
}}
Chỉ trả JSON, không giải thích.
"""

        try:
            response = ollama.chat(model=self.model, messages=[{"role": "user", "content": prompt}])
            content = response.get("content", "").strip()

            # Xử lý nếu AI trả ```json ... ```
            if content.startswith("```"):
                content = content.strip("`").replace("json", "").strip()

            import json
            return json.loads(content)
        except Exception as e:
            return {"_error": str(e)}
