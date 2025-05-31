import streamlit as st
import fitz  # PyMuPDF
import re
import pandas as pd
import os
from io import BytesIO

# Title
st.title("📄 Invoice Processor Web App")

# Uploaded files
uploaded_files = st.file_uploader("Upload PDF invoices", type="pdf", accept_multiple_files=True)

def extract_invoice_data(text, filename):
    # Normalize text: join label lines with nearby value lines (even if separated by blank lines)
    lines = text.splitlines()
    combined_lines = []
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        if line in ["Invoice No.", "Invoice Date", "Amount Due", "Total Amount", "Due Date"]:
            # Look ahead up to 2 lines for a non-empty value
            for j in range(1, 3):
                if i + j < len(lines) and lines[i + j].strip():
                    combined_lines.append(f"{line} {lines[i + j].strip()}")
                    i += j  # Skip value line
                    break
            else:
                combined_lines.append(line)
        else:
            combined_lines.append(line)
        i += 1

    combined_text = "\n".join(combined_lines)

    # Extract fields
    invoice_number = re.search(r"Invoice No\.?\s+(\S+)", combined_text, re.I
