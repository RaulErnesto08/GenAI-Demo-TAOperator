import openpyxl
from datetime import datetime
from pathlib import Path
from config import TEMPLATE_PATH, OUTPUT_DIR

def get_output_path_from_jd(jd_filename: str) -> Path:
    """Returns the Excel output path based on JD filename"""
    name = jd_filename.replace(".pdf", "")
    return OUTPUT_DIR / f"Find_{name}.xlsx"

def load_candidate_data(path: Path):
    wb = openpyxl.load_workbook(path)
    sheet = wb.active
    data = []
    for row in sheet.iter_rows(min_row=11, max_col=6, max_row=26, values_only=True):
        if row[0] is None:
            continue
        data.append({
            "Name": row[0],
            "Match Score": row[1],
            "Matched Skills": row[2],
            "Non-Matched Skills": row[3],
            "Location": row[4],
            "Profile URL": row[5],
        })
    return data
