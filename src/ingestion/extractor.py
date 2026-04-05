import os
import pandas as pd
from pypdf import PdfReader
from loguru import logger

class ExtractionError(Exception):
    pass

class FileNotSupportedError(Exception):
    pass

def extract_from_file(file_path: str) -> str:
    """Extracts raw text from .pdf, .txt, or .csv files."""
    if not os.path.exists(file_path):
        raise ExtractionError(f"File not found: {file_path}")

    _, ext = os.path.splitext(file_path.lower())

    try:
        if ext == ".txt":
            return _extract_txt(file_path)
        elif ext == ".pdf":
            return _extract_pdf(file_path)
        elif ext == ".csv":
            return _extract_csv(file_path)
        else:
            raise FileNotSupportedError(f"Unsupported file type: {ext}")

    except FileNotSupportedError:
        # Re-raise known domain exceptions without wrapping
        raise
    except Exception as e:
        logger.error(f"Error extracting text from {file_path}: {e}")
        raise ExtractionError(f"Failed to extract text: {e}")

def _extract_txt(file_path: str) -> str:
    with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
        return f.read()

def _extract_pdf(file_path: str) -> str:
    reader = PdfReader(file_path)
    text = []
    for page in reader.pages:
        content = page.extract_text()
        if content:
            text.append(content)
    return "\n".join(text)

def _extract_csv(file_path: str) -> str:
    # Use pandas to read the CSV and convert it to a structured string
    df = pd.read_csv(file_path)
    # Convert dataframe to a format suitable for LLMs
    return df.to_string(index=False)
