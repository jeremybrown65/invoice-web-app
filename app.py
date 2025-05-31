import streamlit as st
import fitz  # PyMuPDF
import re
import pandas as pd
from io import BytesIO

def extract_invoice_data(text, filename):
    # Normalize text: join label lines with following value lines
    lines = text.splitlines()
    combined = []
    skip = False
    for i in range(len(lines) - 1):
        if skip:
            skip = False
            continue
        if re.match(r"^(Invoice No\.?|Invoice Date|Amount Due|Total Amount|Due Date)$", lines[i].strip(), re.IGNORECASE):
            combined.append(lines[i] + " " + lines[i+1])
            skip = True
        else:
            combined.append(lines[i])
    combined_text = "\n".join(combined)

    # Extract values
    invoice_number = re.search(r"Invoice No\.?\s+(\S+)", combined_text, re.IGNORECASE)
    invoice_date = re.search(r"Invoice Date\s+(\d{1,2}/\d{1,2}/\d{2,4})", combined_text, re.IGNORECASE)
    total_amount = re.search(r"(Total Amount|Amount Due)\s+\$?([\d,]+\.\d{2})", combined_text, re.IGNORECASE)

    invoice_number = invoice_number.group(1) if invoice_number else ''
    invoice_date = invoice_date.group(1) if invoice_date else ''
    total_amount = total_amount.group(2) if total_amount else ''

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
