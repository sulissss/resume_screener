import docx2txt
import PyPDF2
from pdf2image import convert_from_path
import pytesseract
import subprocess
import os


def extract_text_from_pdf(file_path):
    text = ""
    with open(file_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        for page in reader.pages:
            text += page.extract_text()
    return text


def ocr_pdfs(file_path):
    pages = convert_from_path(file_path, 300)
    # If you want to extract text from all pages:
    full_text = ""
    for page in pages:
        full_text += pytesseract.image_to_string(page)

    full_text.replace('\n', ' ')
    return full_text


def extract_text_from_docx(file_path):
    return docx2txt.process(file_path)


def convert_doc_to_docx(input_path):
    output_path = input_path.replace(".doc", ".docx")
    try:
        subprocess.run(['soffice', '--headless', '--convert-to', 'docx', input_path, '--outdir', os.path.dirname(output_path)], check=True)
    except FileNotFoundError:
        raise FileNotFoundError("LibreOffice (soffice) not found. Please install LibreOffice to use this function.")
    return output_path


def extract_text_from_doc(file_path):
    # Convert .doc to .docx
    docx_path = convert_doc_to_docx(file_path)
    # Extract text from the converted .docx file
    text = extract_text_from_docx(docx_path)
    # Remove the temporary .docx file
    os.remove(docx_path)
    return text


def extract_text_from_txt(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        return file.read()


def parse_resume(file_path):
    if file_path.endswith('.pdf'):
        return ocr_pdfs(file_path)
    elif file_path.endswith('.docx'):
        return extract_text_from_docx(file_path)
    elif file_path.endswith('.doc'):
        return extract_text_from_doc(file_path)
    elif file_path.endswith('.txt'):
        return extract_text_from_txt(file_path)
    else:
        return ""