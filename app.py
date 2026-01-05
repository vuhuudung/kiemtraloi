import streamlit as st
from openai import OpenAI
from checker.checker import *
from checker.rules import *
from checker.ai.openai_word_checker import *
from utils.docx_utils import load_docx, save_docx_temp

st.set_page_config(page_title="AI Sửa văn bản hành chính", layout="wide")

st.subheader("📝 Kiểm tra lỗi chính tả văn bản từ file docx")


uploaded = st.file_uploader("Tải file DOCX", type=["docx"])



use_ai = st.checkbox(
    "🤖 Bật AI xác nhận lỗi gõ",
    value=False
)

ai_mode = None
openai_api_key = None

if use_ai:
    ai_mode = st.radio(
        "Chọn AI",
        ["Ollama (Offline)", "OpenAI (Online)"]
    )

    if ai_mode == "OpenAI (Online)":
        openai_api_key = st.text_input(
            "🔑 OpenAI API Key",
            type="password",
            placeholder="sk-..."
        )



if uploaded:
    doc, paragraphs = load_docx(uploaded)

    if st.button("🔍 Chạy kiểm tra"):

        rules = [           
            ExtraSpaceRule(),
            PunctuationRule(),
            CapitalizeRule(),
            CommonMistakeRule(),
            DuplicateWordRule(),
            RepeatedPhraseRule(),
            NumberFormatRule(),
            CapitalAbbreviationRule(),
            LegalBasisDashRule(),
            LineEndValidPunctuationRule(),
            RepeatedCharRule()

        ]
        ai_word_checker = None
        
        if use_ai:

            if ai_mode == "Ollama (Offline)":
                from checker.ai.ollama_word_checker import OllamaWordChecker

                ai_word_checker = OllamaWordChecker(
                    model="llama3",
                    enabled=True
                )

            elif ai_mode == "OpenAI (Online)":

                if not openai_api_key:
                    st.warning("⚠️ Vui lòng nhập OpenAI API Key")
                else:

                    client = OpenAI(api_key=openai_api_key)
                    

                    ai_word_checker = OpenAIWordChecker(
                        client=client,
                        enabled=True
                    )
                    
        


        checker = SpellChecker(
            rules=rules,
            ai_word_checker=ai_word_checker  # None / OpenAI / Ollama
        )

        data = [(i, p.text) for i, p in enumerate(paragraphs)]
        results = checker.check(data)

        st.session_state["results"] = results
        st.success(f"✅ Phát hiện {len(results)} đoạn văn có lỗi")

    



if "results" in st.session_state and st.session_state["results"]:
    results = st.session_state["results"]

    # reset selected nếu cần
    if "selected" not in st.session_state:
        st.session_state["selected"] = 0
    if st.session_state["selected"] >= len(results):
        st.session_state["selected"] = 0
    col1, col2 = st.columns([3, 7])

    PAGE_SIZE = 20

    if "page" not in st.session_state:
        st.session_state["page"] = 0

    with col1:
        results = st.session_state["results"]
        total = len(results)

        start = st.session_state["page"] * PAGE_SIZE
        end = min(start + PAGE_SIZE, total)

        page_indexes = list(range(start, end))

        selected = st.radio(
            f"Danh sách lỗi ({start + 1}–{end}/{total})",
            page_indexes,
            format_func=lambda i: f"Đoạn {results[i]['line'] + 1}"
        )

        col_prev, col_next = st.columns(2)

        with col_prev:
            if st.button("⬅ Trang trước", disabled=st.session_state["page"] == 0):
                st.session_state["page"] -= 1
                st.rerun()

        with col_next:
            if st.button(
                "Trang sau ➡",
                disabled=end >= total
            ):
                st.session_state["page"] += 1
                st.rerun()


    with col2:
        r = st.session_state["results"][selected]
        st.markdown("**Đoạn văn gốc**")
        st.write(r["text"])

        st.markdown("**Lỗi phát hiện**")
        st.write(r["errors"])

        # ⭐ HIỂN THỊ RIÊNG AIWordChecker
        if r.get("ai_word_errors"):
            st.markdown("**🤖 Lỗi gõ phát hiện bởi AI**")
            for item in r["ai_word_errors"]:
                st.write(
                    f"- ❌ **{item['word']}** → gợi ý: **{item['suggestion']}**"
                )
