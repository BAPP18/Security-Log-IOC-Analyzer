import os

import docx
import pandas as pd
import PyPDF2

ALLOWED_EXTENSIONS = {"txt", "log", "csv", "xlsx", "pdf", "docx"}

MAX_TEXT_LINES = 200_000
MAX_TABULAR_ROWS = 100_000
MAX_PDF_PAGES = 500
MAX_DOCX_PARAGRAPHS = 100_000
MAX_CELL_CHARS = 4_000


def allowed_file(filename):
    return (
        bool(filename)
        and "." in filename
        and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS
    )


def get_file_type(filename):
    return filename.rsplit(".", 1)[1].lower() if "." in filename else ""


def parse_file(filepath, filename):
    file_type = get_file_type(filename)

    parsers = {
        "txt": parse_text_file,
        "log": parse_text_file,
        "csv": parse_csv_file,
        "xlsx": parse_xlsx_file,
        "pdf": parse_pdf_file,
        "docx": parse_docx_file,
    }

    parser = parsers.get(file_type)
    if not parser:
        raise ValueError(f"Unsupported file type: {file_type or 'unknown'}")

    result = parser(filepath)
    return {
        "content_lines": result["lines"],
        "file_info": result["info"],
        "file_type": file_type,
    }


def _row_to_line(values):
    return ",".join(str(value)[:MAX_CELL_CHARS] for value in values)


def parse_text_file(filepath):
    lines = []
    truncated = False

    with open(filepath, "r", encoding="utf-8", errors="replace") as handle:
        for line_number, line in enumerate(handle, 1):
            if line_number > MAX_TEXT_LINES:
                truncated = True
                break
            lines.append(line.rstrip("\r\n"))

    info = {
        "filename": os.path.basename(filepath),
        "file_size": os.path.getsize(filepath),
        "parsed_lines": len(lines),
        "truncated": truncated,
    }
    return {"lines": lines, "info": info}


def parse_csv_file(filepath):
    frame = pd.read_csv(
        filepath,
        nrows=MAX_TABULAR_ROWS + 1,
        dtype=str,
        keep_default_na=False,
        on_bad_lines="skip",
    )
    truncated = len(frame) > MAX_TABULAR_ROWS
    frame = frame.head(MAX_TABULAR_ROWS)

    lines = [_row_to_line(row.values) for _, row in frame.iterrows()]
    info = {
        "filename": os.path.basename(filepath),
        "parsed_rows": len(frame),
        "total_columns": len(frame.columns),
        "column_names": list(frame.columns),
        "truncated": truncated,
    }
    return {"lines": lines, "info": info}


def parse_xlsx_file(filepath):
    workbook = pd.ExcelFile(filepath)
    if not workbook.sheet_names:
        return {
            "lines": [],
            "info": {
                "filename": os.path.basename(filepath),
                "sheet_name": None,
                "parsed_rows": 0,
                "total_columns": 0,
                "truncated": False,
            },
        }

    first_sheet_name = workbook.sheet_names[0]
    frame = pd.read_excel(
        workbook,
        sheet_name=first_sheet_name,
        nrows=MAX_TABULAR_ROWS + 1,
        dtype=str,
        keep_default_na=False,
    )
    truncated = len(frame) > MAX_TABULAR_ROWS
    frame = frame.head(MAX_TABULAR_ROWS)

    lines = [_row_to_line(row.values) for _, row in frame.iterrows()]
    info = {
        "filename": os.path.basename(filepath),
        "sheet_name": first_sheet_name,
        "parsed_rows": len(frame),
        "total_columns": len(frame.columns),
        "truncated": truncated,
    }
    return {"lines": lines, "info": info}


def parse_pdf_file(filepath):
    lines = []

    with open(filepath, "rb") as handle:
        reader = PyPDF2.PdfReader(handle)
        total_pages = len(reader.pages)
        parsed_pages = min(total_pages, MAX_PDF_PAGES)

        for page_number in range(parsed_pages):
            text = reader.pages[page_number].extract_text() or ""
            for line in text.splitlines():
                cleaned = line.strip()
                if cleaned:
                    lines.append(cleaned[:MAX_CELL_CHARS])

    info = {
        "filename": os.path.basename(filepath),
        "total_pages": total_pages,
        "parsed_pages": parsed_pages,
        "truncated": total_pages > parsed_pages,
    }
    return {"lines": lines, "info": info}


def parse_docx_file(filepath):
    document = docx.Document(filepath)
    paragraphs = [
        paragraph.text[:MAX_CELL_CHARS]
        for paragraph in document.paragraphs
        if paragraph.text.strip()
    ]

    truncated = len(paragraphs) > MAX_DOCX_PARAGRAPHS
    paragraphs = paragraphs[:MAX_DOCX_PARAGRAPHS]

    info = {
        "filename": os.path.basename(filepath),
        "parsed_paragraphs": len(paragraphs),
        "truncated": truncated,
    }
    return {"lines": paragraphs, "info": info}
