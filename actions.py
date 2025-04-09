import logging
import openpyxl
import streamlit as st

from datetime import datetime
from PyPDF2 import PdfReader

from models import Candidate
from utils import extract_job_title
from browser_use import ActionResult
from file_manager import get_output_path_from_jd
from config import controller, TEMPLATE_PATH, get_selected_jd

logger = logging.getLogger(__name__)

@controller.action("Read the Job Description (JD) PDF")
def read_jd(jd_path: str):
    try:
        pdf = PdfReader(jd_path)
        text = "".join(page.extract_text() or "" for page in pdf.pages)
        logger.info(f"✅ Read JD with {len(text)} characters")
        return ActionResult(extracted_content=text, include_in_memory=True)
    except Exception as e:
        return ActionResult(error=f"Failed to read JD PDF: {str(e)}")

@controller.action("Save candidate data to the Excel template", param_model=Candidate)
def save_candidates(candidate: Candidate):
    jd_filename = get_selected_jd()
    output_path = get_output_path_from_jd(jd_filename)

    try:
        logger.info(f"🗂️ Saving candidate data to {output_path}")
        wb = openpyxl.load_workbook(output_path) if output_path.exists() else openpyxl.load_workbook(TEMPLATE_PATH)
        sheet = wb.active
        sheet["B3"] = datetime.today().strftime("%Y-%m-%d")
        sheet["B5"] = extract_job_title(jd_filename)

        for row in range(11, 27):
            if sheet[f"A{row}"].value is None:
                sheet[f"A{row}"] = candidate.name
                sheet[f"B{row}"] = candidate.match_score
                sheet[f"C{row}"] = ", ".join(candidate.matched_skills)
                sheet[f"D{row}"] = ", ".join(candidate.non_matched_skills)
                sheet[f"E{row}"] = candidate.location
                sheet[f"F{row}"] = candidate.profile_url
                break

        wb.save(output_path)
        logger.info(f"✅ Saved candidate {candidate.name} to Excel")
        return ActionResult(extracted_content="Saved candidate")
    except Exception as e:
        logger.error(f"❌ Error saving candidate: {str(e)}")
        return ActionResult(error="Failed to save candidate")

@controller.action("Update the current status in the UI")
def update_status(status: str):
    from config import shared_status
    logger.info(f"🔄 STATUS: {status}")
    shared_status.set(status)
    return ActionResult(success=True)
