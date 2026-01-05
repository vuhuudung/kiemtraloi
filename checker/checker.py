import streamlit as st
import re


class SpellChecker:
    def __init__(self, rules, ai_word_checker=None):
        self.rules = rules
        self.ai_word_checker = ai_word_checker

    def check(self, paragraphs):
        """
        paragraphs: list[(line_no, text)]
        return: list[dict]
        """
        results = []

        for line_no, text in paragraphs:
            item = {
                "line": line_no,
                "text": text,
                "errors": [],
                "suspects": [],
                "ai_word_errors": []
            }

            # ===== 1. RULE-BASED =====
            for rule in self.rules:
                if not getattr(rule, "enabled", True):
                    continue

                res = rule.check(line_no, text)

                if isinstance(res, dict) and "suspects" in res:
                    item["suspects"].extend(res["suspects"])
                elif isinstance(res, list):
                    item["errors"].extend(res)

            # fallback suspects cho AI
            if not item["suspects"]:
                item["suspects"] = re.findall(r"\b[^\W\d_]{4,}\b", text)

            item["suspects"] = list(set(item["suspects"]))

            # ===== 2. AI-BASED (NẾU CÓ) =====
            if self.ai_word_checker and item["suspects"]:
                ai_result = self.ai_word_checker.check_words(
                    words=item["suspects"],
                    context=text
                )

                for word, info in ai_result.items():
                    if isinstance(info, dict) and info.get("status") == "sai":
                        item["ai_word_errors"].append({
                            "word": word,
                            "suggestion": info.get("suggestion", "")
                        })
                        item["errors"].append(
                            f"Từ '{word}' nghi lỗi gõ → gợi ý: {info.get('suggestion','')}"
                        )

            # ===== 3. LỌC CUỐI =====
            if item["errors"]:
                results.append(item)

        return results
