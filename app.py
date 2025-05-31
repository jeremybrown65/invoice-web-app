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

        # Extract invoice number from filename
        invoice_number_match = re.search(r"INV\d+", file.name)
        invoice_number = invoice_number_match.group() if invoice_number_match else ""

                # Extract invoice date (line above "Net 30")
        invoice_date = ""
        for i, line in enumerate(lines):
            if "Net 30" in line and i > 0:
                date_match = re.search(r"\d{2}/\d{2}/\d{2}", lines[i - 1])
                if date_match:
                    invoice_date = date_match.group(0)
                    break

        # Extract total amount (from line or line after)
        total_amount = ""
        for i, line in enumerate(lines):
            if "Total Amount" in line or "Amount Due" in line:
                amount_match = re.search(r"\$?(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)", line)
                if amount_match:
                    total_amount = amount_match.group(1)
                    break
                elif i + 1 < len(lines):
                    next_line_match = re.search(r"\$?(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)", lines[i + 1])
                    if next_line_match:
                        total_amount = next_line_match.group(1)
                        break


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
