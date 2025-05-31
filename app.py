import streamlit as st
import fitz  # PyMuPDF
import pandas as pd
import re
import os
from io import BytesIO

st.title("📄 Invoice Processor")

uploaded_files = st.file_uploader("Upload Invoice PDFs", type="pdf", accept_multiple_files=True)

if uploaded_files:
    extracted_data = []

    for file in uploaded_files:
        file_bytes = file.read()
        pdf = fitz.open(stream=file_bytes, filetype="pdf")

        combined_text = ""
        for page in pdf:
            combined_text += page.get_text()

        # Show raw text for debugging
        with st.expander(f"Raw text from {file.name}"):
            st.text(combined_text)

        # Extract invoice number from filename
        invoice_number_match = re.search(r"INV\d+", file.name)
        invoice_number = invoice_number_match.group() if invoice_number_match else ""

                # Extract invoice date by finding "Invoice Date" followed by a date nearby
        invoice_date = ""
        invoice_date_pattern = re.search(r"Invoice Date\s*[\r\n]+[\s]*([0-9]{2}/[0-9]{2}/[0-9]{2})", combined_text, re.IGNORECASE)
        if invoice_date_pattern:
            invoice_date = invoice_date_pattern.group(1)

        # Extract total amount by finding last match of Total Amount or Amount Due followed by money
        total_amount = ""
        total_matches = re.findall(r"(?:Total Amount|Amount Due)[^\d$]*(\$?\d{1,3}(?:,\d{3})*(?:\.\d{2})?)", combined_text, re.IGNORECASE)
        if total_matches:
            total_amount = total_matches[-1].replace("$", "")


        # Extract job name from file name (after the invoice number)
        job_name = file.name.split("-")[-1].replace(".pdf", "").strip()

        extracted_data.append({
            "Invoice Number": invoice_number,
            "Invoice Date": invoice_date,
            "Job Name": job_name,
            "Total Amount": total_amount
        })

    df = pd.DataFrame(extracted_data)
    st.subheader("Extracted Invoice Data")
    st.dataframe(df)

    # Download link
    def convert_df(df):
        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='Invoices')
        return output.getvalue()

    excel_data = convert_df(df)
    st.download_button("📥 Download Excel", data=excel_data, file_name="invoice_data.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
