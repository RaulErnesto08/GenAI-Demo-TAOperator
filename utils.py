def extract_job_title(filename: str) -> str:
    """Convert 'Some_Title.pdf' -> 'Some Title'"""
    return filename.replace(".pdf", "").replace("_", " ").title()

def normalize_filename(name: str) -> str:
    """Convert 'Some Job Title.pdf' -> 'Some_Job_Title.pdf'"""
    return name.replace(" ", "_")
