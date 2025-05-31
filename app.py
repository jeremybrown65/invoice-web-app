import streamlit as st
import fitz  # PyMuPDF
import pandas as pd
import re
import os

st.set_page_config(page_title="Invoice Processor", layout="wide")
st.title("📄 Batch Invoice Extractor")

def extract_invoice_data(text, filename):
    invoice_number = os.path.splitext(os.path.basename(filename))[0].split(" - ")[0].split()[-1]
    
    # Try matching date formats like MM/DD/YY or MM/DD/YYYY
    date_match = re.search(r"Invoice Date\s+(\d{2}/\d{2}/\d{2,4})", text, re.IGNORECASE)
    invoice_date = date_match.group(1) if date_match else "Not found"

    # Job name from filename after ' - '
    job_name = os.path.splitext(filename)[0].split(" - ")[-1]

    # Total amount from "Total Amount" or "Amount Due"
    total_match = re.search(r"(Total Amount|Amount Due)\s+\$?([\d,]+\.\d{2})", text, re.IGNORECASE)
    total = total_match.group(2) if total_match else "Not found"

    return {
        "Invoice Number": invoice_number,
        "Invoice Date": invoice_date,
        "Job Name": job_name,
        "Total": total
    }

uploaded_files = st.file_uploader("Upload one or more invoice PDFs", type="pdf", accept_multiple_files=True)

if uploaded_files:
    extracted_data = []

    for uploaded_file in uploaded_files:
        if uploaded_file.type == "application/pdf":
            try:
                # Extract text from PDF
                file_bytes = uploaded_file.read()
                doc = fitz.open(stream=file_bytes, filetype="pdf")
                text = ""
                for page in doc:
                    text += page.get_text("text")
                doc.close()

                # Show raw extracted text for debug
                with st.expander(f"📄 Raw text from: {uploaded_file.name}", expanded=False):
                    st.text_area("Extracted Text", text if text.strip() else "[No text found]", height=300)

                # Extract invoice data
                data = extract_invoice_data(text, uploaded_file.name)
                extracted_data.append(data)

            except Exception as e:
                st.error(f"Error processing {uploaded_file.name}: {e}")

    if extracted_data:
        df = pd.DataFrame(extracted_data)
        st.success("✅ Invoices processed successfully!")
        st.dataframe(df)

        # Download link for Excel file
        output_excel = "invoice_data.xlsx"
        df.to_excel(output_excel, index=False)

        with open(output_excel, "rb") as f:
            st.download_button(
                label="📥 Download Excel File",
                data=f,
                file_name="invoice_data.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
