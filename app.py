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

    # Normalize text
    lines = text.splitlines()
    clean_lines = [line.strip() for line in lines if line.strip()]
    full_text = "\n".join(clean_lines)

    # Invoice number from filename
    invoice_match = re.search(r"Invoice-([\w\-]+)", filename)
    invoice_number = invoice_match.group(1).strip() if invoice_match else ''

    # Job name from filename
    job_match = re.search(r"Invoice-[\w\-]+\s*-\s*(.+)\.pdf", filename)
    job_name = job_match.group(1).strip() if job_match else os.path.splitext(filename)[0]

    # Invoice date from text
    invoice_date_match = re.search(r"Invoice Date\s+(\d{2}/\d{2}/\d{2,4})", full_text, re.IGNORECASE)
    invoice_date = invoice_date_match.group(1).strip() if invoice_date_match else ''

    # Total amount from text
    total_amount_match = re.search(r"(Total Amount|Amount Due)\s+\$?([\d,]+\.\d{2})", full_text, re.IGNORECASE)
    total_amount = total_amount_match.group(2).strip() if total_amount_match else ''

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
