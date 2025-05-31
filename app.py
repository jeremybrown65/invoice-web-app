import streamlit as st
import fitz  # PyMuPDF
import re
import pandas as pd
import os
from io import BytesIO

st.title("📄 Invoice Processor Web App")

uploaded_files = st.file_uploader("Upload PDF invoices", type="pdf", accept_multiple_files=True)

def extract_invoice_data(text, filename):
    import re
    import os

    # Flatten and clean the text
    lines = text.splitlines()
    normalized_text = "\n".join([line.strip() for line in lines if line.strip()])

    # Match fields that might be on the same line or next line
    invoice_number = re.search(r"Invoice No\.?\s*:?[\s\n]+(\S+)", normalized_text, re.IGNORECASE)
    invoice_date = re.search(r"Invoice Date\s*:?[\s\n]+(\d{1,2}/\d{1,2}/\d{2,4})", normalized_text, re.IGNORECASE)
    total_amount = re.search(r"(Total Amount|Amount Due)\s*:?[\s\n]+\$?([\d,]+\.\d{2})", normalized_text, re.IGNORECASE)

    invoice_number = invoice_number.group(1).strip() if invoice_number else ''
    invoice_date = invoice_date.group(1).strip() if invoice_date else ''
    total_amount = total_amount.group(2).strip() if total_amount else ''

    # Extract job name from file name
    job_match = re.search(r"Invoice-\S+\s*-\s*(.+)\.pdf", filename, re.IGNORECASE)
    job_name = job_match.group(1).strip() if job_match else os.path.splitext(filename)[0]

    return {
        "Invoice Number": invoice_number,
        "Invoice Date": invoice_date,
        "Job Name": job_name,
        "Total Amount": total_amount
    }


if uploaded_files:
    extracted_data = []

    for file in uploaded_files:
        pdf_bytes = file.read()
        doc = fitz.open(stream=pdf_bytes, filetype="pdf")
        full_text = "".join([page.get_text() for page in doc])
        data = extract_invoice_data(full_text, file.name)
        extracted_data.append(data)

    df = pd.DataFrame(extracted_data)
    st.success("✅ Invoices processed successfully!")
    st.dataframe(df)

    output = BytesIO()
    df.to_excel(output, index=False, engine='openpyxl')

    st.download_button(
        label="📥 Download Excel",
        data=output.getvalue(),
        file_name="invoice_data.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
