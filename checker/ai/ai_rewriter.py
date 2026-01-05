from prompt_templates import SYSTEM_PROMPT, USER_PROMPT_TEMPLATE

class AIRewriter:
    def __init__(self, client, model="gpt-4o-mini", enabled=True):
        self.client = client
        self.model = model
        self.enabled = enabled

    def rewrite(self, text, errors):
        if not self.enabled or not errors:
            return None

        prompt = USER_PROMPT_TEMPLATE.format(
            text=text.strip(),
            errors="\n".join(f"- {e}" for e in errors)
        )

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.2
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            return f"[AI lỗi: {e}]"
