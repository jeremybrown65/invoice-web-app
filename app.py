import streamlit as st
import fitz  # PyMuPDF
import pandas as pd
import re
from io import BytesIO

st.set_page_config(page_title="Invoice Extractor", layout="centered")
st.title("📄 Invoice Data Extractor")

uploaded_files = st.file_uploader(
    "Upload one or more PDF invoices", type="pdf", accept_multiple_files=True
)

def extract_invoice_data(text, filename):
    # Clean and normalize text
    lines = text.splitlines()
    clean_lines = [line.strip() for line in lines if line.strip()]
    full_text = "\n".join(clean_lines)

    # Extract invoice number from filename
    invoice_match = re.search(r"Invoice-([\w\-]+)", filename)
    invoice_number = invoice_match.group(1).strip() if invoice_match else ''

    # Extract job name from filename
    job_match = re.search(r"Invoice-[\w\-]+\s*-\s*(.+)\.pdf", filename)
    job_name = job_match.group(1).strip() if job_match else filename.rsplit('.', 1)[0]

    # Extract invoice date from text
    invoice_date_match = re.search(r"Invoice Date\s+(\d{2}/\d{2}/\d{2,4})", full_text, re.IGNORECASE)
    invoice_date = invoice_date_match.group(1).strip() if invoice_date_match else ''

    # Extract total amount from text
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

    for uploaded_file in uploaded_files:
        if uploaded_file.type == "application/pdf":
            file_bytes = uploaded_file.read()
            doc = fitz.open(stream=file_bytes, filetype="pdf")
            text = ""
            for page in doc:
                text += page.get_text()
            doc.close()

            # ✅ Show raw extracted text
with st.expander(f"📄 Raw text from: {uploaded_file.name}"):
    st.text(text)


            # Extract and store data
            data = extract_invoice_data(text, uploaded_file.name)
            extracted_data.append(data)

    # Display DataFrame
    if extracted_data:
        df = pd.DataFrame(extracted_data)
        st.success("✅ Invoices processed successfully.")
        st.dataframe(df)

        # Excel download button
        output = BytesIO()
        df.to_excel(output, index=False, engine='openpyxl')
        st.download_button(
            label="📥 Download Excel File",
            data=output.getvalue(),
            file_name="invoice_data.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
