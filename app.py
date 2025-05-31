import streamlit as st
import fitz  # PyMuPDF

st.title("PDF Text Extractor Debug Test")

uploaded_files = st.file_uploader("Upload PDF(s)", type="pdf", accept_multiple_files=True)

if uploaded_files:
    for uploaded_file in uploaded_files:
        file_bytes = uploaded_file.read()
        doc = fitz.open(stream=file_bytes, filetype="pdf")
        text = ""
        for page in doc:
            text += page.get_text("text")
        doc.close()

        st.write(f"### {uploaded_file.name}")
        st.text_area("Raw Text", text if text.strip() else "[No text found]", height=400)
