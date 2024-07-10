import streamlit as st
import os
import json
import tempfile
from marker.convert import convert_single_pdf
from marker.models import load_all_models
from transformers import AutoTokenizer, AutoModelForCausalLM
import torch
from pdf2image import convert_from_bytes
from datetime import datetime
import re
import asyncio
from concurrent.futures import ThreadPoolExecutor
import warnings

# Initialize Streamlit page
st.set_page_config(page_title="Extractor de Facturas", page_icon="📄", layout="wide")

# Initialize models
@st.cache_resource
def load_models():
    marker_models = load_all_models()
    
    # Try to enable Flash Attention
    try:
        from transformers import AutoConfig
        config = AutoConfig.from_pretrained("numind/NuExtract")
        config.use_flash_attention_2 = True
        model = AutoModelForCausalLM.from_pretrained("numind/NuExtract", config=config)
    except Exception as e:
        print(f"Failed to enable Flash Attention: {e}")
        print("Falling back to default attention mechanism.")
        model = AutoModelForCausalLM.from_pretrained("numind/NuExtract")
    
    tokenizer = AutoTokenizer.from_pretrained("numind/NuExtract")
    
    return marker_models, tokenizer, model

# Suppress the warning
warnings.filterwarnings("ignore", message="You are not running the flash-attention implementation, expect numerical differences")

marker_models, tokenizer, nuextract_model = load_models()

def extract_text_from_pdf(pdf_file):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
        tmp_file.write(pdf_file.getvalue())
        tmp_file_path = tmp_file.name
    full_text, doc_images, out_meta = convert_single_pdf(tmp_file_path, marker_models)
    os.unlink(tmp_file_path)
    return full_text

async def extract_invoice_data(markdown_text):
    schema = """{
        "Invoice": {
            "Number": "",
            "Issuer": "",
            "IssuerVAT": "",
            "Date": "",
            "DueDate": "",
            "IssuerAddress": "",
            "IssuerEmail": "",
            "RecipientName": "",
            "RecipientEmail": "",
            "RecipientVAT": "",
            "TotalExcludingTax": "",
            "VATTotal": "",
            "TotalAmount": "",
            "Currency": ""
        }
    }"""
    inputs = tokenizer(f"<|input|>\n### Template:\n{schema}\n### Text:\n{markdown_text}\n<|output|>\n", return_tensors="pt")
    output = nuextract_model.generate(**inputs, max_new_tokens=1000)
    extracted_data = tokenizer.decode(output[0], skip_special_tokens=True).split("<|output|>")[1]
    return json.loads(extracted_data)["Invoice"]

def save_to_jsonl(data, filename):
    with open(filename, 'a') as f:
        json.dump(data, f)
        f.write('\n')

def get_pdf_preview(pdf_file):
    return convert_from_bytes(pdf_file.getvalue(), first_page=1, last_page=1)[0]

def get_default_filename():
    now = datetime.now()
    year = now.year
    month = now.month
    quarter = (month - 1) // 3 + 1
    if quarter == 1:
        year -= 1
        quarter = 4
    else:
        quarter -= 1
    return f"{year}-T{quarter}-Facturas.jsonl"

def separate_currency(value):
    match = re.match(r'^([^\d]*)(\d*[.,]?\d*)([^\d]*)$', value)
    if match:
        currency = match.group(1) or match.group(3)
        number = match.group(2)
        return number.strip(), currency.strip()
    return value, ''

# Initialize session state
if 'screen' not in st.session_state:
    st.session_state.screen = 'upload'
if 'markdown_texts' not in st.session_state:
    st.session_state.markdown_texts = []
if 'processed_pdfs' not in st.session_state:
    st.session_state.processed_pdfs = []
if 'current_pdf_index' not in st.session_state:
    st.session_state.current_pdf_index = 0
if 'output_filename' not in st.session_state:
    st.session_state.output_filename = get_default_filename()
if 'processing_complete' not in st.session_state:
    st.session_state.processing_complete = False

def extract_markdown_from_pdfs(pdf_files):
    with ThreadPoolExecutor() as executor:
        markdown_texts = list(executor.map(extract_text_from_pdf, pdf_files))
    return markdown_texts

async def process_pdf(pdf_file, markdown_text):
    pdf_preview = get_pdf_preview(pdf_file)
    extracted_data = await extract_invoice_data(markdown_text)
    return {
        'markdown_text': markdown_text,
        'pdf_preview': pdf_preview,
        'extracted_data': extracted_data,
        'original_file': pdf_file
    }

async def process_remaining_pdfs():
    for i in range(1, len(st.session_state.markdown_texts)):
        processed_pdf = await process_pdf(st.session_state.uploaded_files[i], st.session_state.markdown_texts[i])
        st.session_state.processed_pdfs.append(processed_pdf)

def upload_screen():
    st.title("Extractor de Facturas - Subir PDFs")
    uploaded_files = st.file_uploader("Elige facturas en PDF", type="pdf", accept_multiple_files=True)
    
    st.session_state.output_filename = st.text_input("Nombre del archivo de salida", value=st.session_state.output_filename)
    
    if uploaded_files:
        if st.button("Procesar PDFs"):
            with st.spinner("Extrayendo texto de los PDFs..."):
                st.session_state.uploaded_files = uploaded_files
                st.session_state.markdown_texts = extract_markdown_from_pdfs(uploaded_files)
            
            with st.spinner("Procesando el primer PDF..."):
                first_processed = asyncio.run(process_pdf(uploaded_files[0], st.session_state.markdown_texts[0]))
                st.session_state.processed_pdfs = [first_processed]
            
            st.session_state.current_pdf_index = 0
            st.session_state.processing_complete = False
            st.session_state.screen = 'review'
            st.rerun()

def review_screen():
    st.title("Extractor de Facturas - Revisar Datos")
    
    # Process remaining PDFs in the background
    if len(st.session_state.processed_pdfs) < len(st.session_state.markdown_texts):
        asyncio.run(process_remaining_pdfs())
    
    if not st.session_state.processed_pdfs:
        st.warning("No hay PDFs para procesar. Por favor, sube PDFs.")
        if st.button("Subir PDFs"):
            st.session_state.screen = 'upload'
            st.rerun()
        return

    current_pdf = st.session_state.processed_pdfs[st.session_state.current_pdf_index]

    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Vista Previa del PDF")
        st.image(current_pdf['pdf_preview'], use_column_width=True)
    
    with col2:
        st.subheader("Datos Extraídos de la Factura")
        edited_data = {}
        field_translations = {
            "Number": "Número",
            "Issuer": "Emisor",
            "IssuerVAT": "CIF/NIF del Emisor",
            "Date": "Fecha",
            "DueDate": "Fecha de Vencimiento",
            "IssuerAddress": "Dirección del Emisor",
            "IssuerEmail": "Correo del Emisor",
            "RecipientName": "Nombre del Destinatario",
            "RecipientEmail": "Correo del Destinatario",
            "RecipientVAT": "NIF/CIF del Destinatario",
            "TotalExcludingTax": "Total Sin Impuestos",
            "VATTotal": "Total IVA",
            "TotalAmount": "Importe Total",
            "Currency": "Moneda"
        }
        for key, value in current_pdf['extracted_data'].items():
            if key in ['TotalExcludingTax', 'VATTotal', 'TotalAmount']:
                number, currency = separate_currency(value)
                edited_data[key] = st.text_input(f"{field_translations[key]} (Número)", number)
                if 'Currency' not in edited_data:
                    edited_data['Currency'] = st.text_input("Moneda", currency)
            else:
                edited_data[key] = st.text_input(field_translations[key], value)
        
        col1, col2 = st.columns(2)
        with col1:
            if st.session_state.current_pdf_index < len(st.session_state.processed_pdfs) - 1:
                if st.button("Guardar y Siguiente"):
                    save_to_jsonl(edited_data, st.session_state.output_filename)
                    st.success(f"Datos guardados en {st.session_state.output_filename}")
                    st.session_state.current_pdf_index += 1
                    st.rerun()
            else:
                if st.button("Guardar"):
                    save_to_jsonl(edited_data, st.session_state.output_filename)
                    st.success(f"Datos guardados en {st.session_state.output_filename}")
                    st.session_state.processing_complete = True
        
        with col2:
            if st.session_state.current_pdf_index < len(st.session_state.processed_pdfs) - 1:
                if st.button("Saltar"):
                    st.session_state.current_pdf_index += 1
                    st.rerun()

    remaining = len(st.session_state.markdown_texts) - st.session_state.current_pdf_index - 1
    st.info(f"PDFs restantes por procesar: {remaining}")

    if st.session_state.processing_complete:
        st.success("¡Todos los PDFs han sido procesados!")
        if st.button("Comenzar de Nuevo"):
            st.session_state.screen = 'upload'
            st.session_state.current_pdf_index = 0
            st.session_state.processed_pdfs = []
            st.session_state.markdown_texts = []
            st.session_state.processing_complete = False
            st.rerun()

    # Download link for the invoices file
    if os.path.exists(st.session_state.output_filename):
        with open(st.session_state.output_filename, "rb") as file:
            st.download_button(
                label="Descargar Archivo de Facturas",
                data=file,
                file_name=st.session_state.output_filename,
                mime="application/json"
            )

# Main app logic
if st.session_state.screen == 'upload':
    upload_screen()
elif st.session_state.screen == 'review':
    review_screen()