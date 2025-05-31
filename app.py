import streamlit as st
import fitz  # PyMuPDF
import re
import pandas as pd
import os
from io import BytesIO

st.title("📄 Invoice Processor Web App")

uploaded_files = st.file_uploader("Upload PDF invoices", type="pdf", accept_multiple_files=True)

def extract_invoice_data(text, filename):
    lines = text.splitlines()
    combined_lines = []
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        if line in ["Invoice No.", "Invoice Date", "Amount Due", "Total Amount", "Due Date"]:
            for j in range(1, 3):
                if i + j < len(lines) and lines[i + j].strip():
                    combined_lines.append(f"{line} {lines[i + j].strip()}")
                    i += j
                    break
            else:
                combined_lines.append(line)
        else:
            combined_lines.append(line)
        i += 1

    combined_text = "\n".join(combined_lines)

    invoice_number_match = re.search(r"Invoice No\.?\s+(\S+)", combined_text, re.IGNORECASE)
    invoice_date_match = re.search(r"Invoice Date\s+(\d{1,2}/\d{1,2}/\d{2,4})", combined_text, re.IGNORECASE)
    total_amount_match = re.search(r"(Total Amount|Amount Due)\s+\$?([\d,]+\.\d{2})", combined_text, re.IGNORECASE)

    invoice_number = invoice_number_match.group(1) if invoice_number_match else ''
    invoice_date = invoice_date_match.group(1) if invoice_date_match else ''
    total_amount = total_amount_match.group(2) if total_amount_match else ''

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
