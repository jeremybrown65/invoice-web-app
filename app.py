import streamlit as st
import pytesseract
from pdf2image import convert_from_bytes
from PIL import Image
import io
import re
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="Invoice Batch Processor", layout="wide")
st.title("📄 Batch Invoice Processor")

uploaded_files = st.file_uploader("Upload Invoice PDFs", type="pdf", accept_multiple_files=True)

data = []

def extract_text_from_pdf(pdf_bytes):
    images = convert_from_bytes(pdf_bytes)  # Remove page limit
    full_text = ""
    for img in images:
        full_text += pytesseract.image_to_string(img)
    return full_text


def extract_fields(text, filename):
    invoice_number = re.search(r'Invoice\s*(No\.?|#)?\s*([A-Z0-9\-]+)', text, re.IGNORECASE)
    date_match = re.search(r'Invoice\s*Date\s*[:\-]?\s*([0-9/]{6,})', text, re.IGNORECASE)
    total_match = re.search(r'Total\s*Amount\s*\$?\s*([\d,]+\.\d{2})', text, re.IGNORECASE)

    job_name = filename.split(" - ", 1)[1].rsplit(".pdf", 1)[0] if " - " in filename else filename.replace(".pdf", "")

    return {
        "Invoice Number": invoice_number.group(2) if invoice_number else "",
        "Invoice Date": date_match.group(1) if date_match else "",
        "Job Name": job_name,
        "Total": total_match.group(1) if total_match else ""
    }

if uploaded_files:
    for file in uploaded_files:
        text = extract_text_from_pdf(file.read())
        fields = extract_fields(text, file.name)
        data.append(fields)

    df = pd.DataFrame(data)
    st.dataframe(df)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output = io.BytesIO()
    df.to_excel(output, index=False, engine='openpyxl')
    st.download_button(
        label="📥 Download Excel File",
        data=output.getvalue(),
        file_name=f"invoice_data_{timestamp}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
