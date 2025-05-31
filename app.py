import streamlit as st

# --- Simple password login ---
def check_password():
    def password_entered():
        if st.session_state["password"] == st.secrets["password"]:
            st.session_state["authenticated"] = True
            del st.session_state["password"]
        else:
            st.session_state["authenticated"] = False

    if "authenticated" not in st.session_state:
        st.text_input("Enter password:", type="password", on_change=password_entered, key="password")
        return False
    elif not st.session_state["authenticated"]:
        st.text_input("Enter password:", type="password", on_change=password_entered, key="password")
        st.error("Incorrect password.")
        return False
    else:
        return True

if not check_password():
    st.stop()

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

        lines = combined_text.splitlines()

        # Extract invoice number from filename
        invoice_number_match = re.search(r"INV\d+", file.name)
        invoice_number = invoice_number_match.group() if invoice_number_match else ""

        # Extract invoice date: line above "Net 30"
        invoice_date = ""
        for i, line in enumerate(lines):
            if "Net 30" in line and i > 0:
                date_match = re.search(r"\d{2}/\d{2}/\d{2}", lines[i - 1])
                if date_match:
                    invoice_date = date_match.group()
                break

        # Extract total amount: last amount before "Remit Information"
        total_amount = ""
        if "Remit Information" in combined_text:
            section = combined_text.split("Remit Information")[0]
            matches = re.findall(r"\$?(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)", section)
            if matches:
                total_amount = matches[-1]

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
