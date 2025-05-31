import streamlit as st
import fitz  # PyMuPDF
import re
import pandas as pd
from io import BytesIO

def extract_invoice_data(text, filename):
    # Extract invoice number using a broader pattern
    invoice_number_match = re.search(r"(Invoice\s+No\.?|Invoice\s+#?)\s*[:\-]?\s*(\S+)", text, re.IGNORECASE)
    invoice_number = invoice_number_match.group(2) if invoice_number_match else ''

    # Extract invoice date using multiple formats
    date_match = re.search(r"(Invoice\s+Date)\s*[:\-]?\s*(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})", text, re.IGNORECASE)
    invoice_date = date_match.group(2) if date_match else ''

    # Extract total using various labels
    total_match = re.search(r"(Total\s+Amount|Amount\s+Due)\s*[:\-]?\s*\$?([\d,]+\.\d{2})", text, re.IGNORECASE)
    total_amount = total_match.group(2) if total_match else ''

    # Extract job name from file name
    job_match = re.search(r"Invoice-\S+\s*-\s*(.+)\.pdf", filename, re.IGNORECASE)
    job_name = job_match.group(1).strip() if job_match else ''

    return {
        "Invoice Number": invoice_number,
        "Invoice Date": invoice_date,
        "Job Name": job_name,
        "Total Amount": total_amount
    }


def process_pdf(uploaded_file):
    doc = fitz.open(stream=uploaded_file.read(), filetype="pdf")
    text = ""
    for page in doc:
        text += page.get_text()
    return text

st.title("📄 Invoice Scanner (Streamlit Web App)")

uploaded_files = st.file_uploader("Upload one or more invoice PDFs", type="pdf", accept_multiple_files=True)

if uploaded_files:
    all_data = []

    for file in uploaded_files:
        text = process_pdf(file)

        # 🔍 Show raw extracted text for debugging
        st.text_area(f"Extracted Text from {file.name}", text, height=300)

        data = extract_invoice_data(text, file.name)
        all_data.append(data)

    df = pd.DataFrame(all_data)
    st.dataframe(df)

    # Offer download of Excel
    buffer = BytesIO()
    df.to_excel(buffer, index=False, engine='openpyxl')
    st.download_button(
        label="📥 Download Excel File",
        data=buffer.getvalue(),
        file_name="invoice_data.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
