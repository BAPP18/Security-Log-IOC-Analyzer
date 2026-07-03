import os
import csv
import io
import pandas as pd
import PyPDF2
import docx
from werkzeug.utils import secure_filename

ALLOWED_EXTENSIONS = {'txt', 'log', 'csv', 'xlsx', 'pdf', 'docx'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_file_type(filename):
    return filename.rsplit('.', 1)[1].lower() if '.' in filename else ''

def parse_file(filepath, filename):
    file_type = get_file_type(filename)
    content_lines = []
    file_info = {}

    if file_type in ('txt', 'log'):
        result = parse_text_file(filepath)
        content_lines = result['lines']
        file_info = result['info']

    elif file_type == 'csv':
        result = parse_csv_file(filepath)
        content_lines = result['lines']
        file_info = result['info']

    elif file_type == 'xlsx':
        result = parse_xlsx_file(filepath)
        content_lines = result['lines']
        file_info = result['info']

    elif file_type == 'pdf':
        result = parse_pdf_file(filepath)
        content_lines = result['lines']
        file_info = result['info']

    elif file_type == 'docx':
        result = parse_docx_file(filepath)
        content_lines = result['lines']
        file_info = result['info']

    return {
        'content_lines': content_lines,
        'file_info': file_info,
        'file_type': file_type
    }

def parse_text_file(filepath):
    lines = []
    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
        for line in f:
            lines.append(line.rstrip('\n'))
    file_info = {
        'filename': os.path.basename(filepath),
        'file_size': os.path.getsize(filepath),
        'total_lines': len(lines)
    }
    return {'lines': lines, 'info': file_info}

def parse_csv_file(filepath):
    lines = []
    df = pd.read_csv(filepath)
    for _, row in df.iterrows():
        line_parts = [str(val) for val in row.values]
        lines.append(','.join(line_parts))
    file_info = {
        'filename': os.path.basename(filepath),
        'total_rows': len(df),
        'total_columns': len(df.columns),
        'column_names': list(df.columns)
    }
    return {'lines': lines, 'info': file_info}

def parse_xlsx_file(filepath):
    lines = []
    df = pd.read_excel(filepath, sheet_name=None)
    first_sheet_name = list(df.keys())[0]
    first_sheet = df[first_sheet_name]
    for _, row in first_sheet.iterrows():
        line_parts = [str(val) for val in row.values]
        lines.append(','.join(line_parts))
    file_info = {
        'filename': os.path.basename(filepath),
        'sheet_name': first_sheet_name,
        'total_rows': len(first_sheet),
        'total_columns': len(first_sheet.columns)
    }
    return {'lines': lines, 'info': file_info}

def parse_pdf_file(filepath):
    lines = []
    with open(filepath, 'rb') as f:
        reader = PyPDF2.PdfReader(f)
        for page_num in range(len(reader.pages)):
            page = reader.pages[page_num]
            text = page.extract_text()
            if text:
                for line in text.split('\n'):
                    if line.strip():
                        lines.append(line.strip())
    file_info = {
        'filename': os.path.basename(filepath),
        'total_pages': len(reader.pages)
    }
    return {'lines': lines, 'info': file_info}

def parse_docx_file(filepath):
    lines = []
    doc = docx.Document(filepath)
    paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
    lines = paragraphs
    file_info = {
        'filename': os.path.basename(filepath),
        'total_paragraphs': len(paragraphs)
    }
    return {'lines': lines, 'info': file_info}
