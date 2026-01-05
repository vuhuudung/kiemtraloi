from docx import Document
import io

def load_docx(uploaded_file):
    doc = Document(uploaded_file)
    return doc, doc.paragraphs

def save_docx_temp(doc):
    buffer = io.BytesIO()
    doc.save(buffer)
    buffer.seek(0)
    return buffer
