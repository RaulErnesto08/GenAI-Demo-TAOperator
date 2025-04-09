import asyncio
import logging

from browser_use import Agent, Browser, BrowserConfig
from langchain_aws import ChatBedrockConverse
from config import shared_status
from utils import extract_job_title
from config import controller

TASK_TEMPLATE = """
You are an expert LinkedIn candidate finder.

You will find and analyze candidates for a job described in this PDF: {jd_path}

🔹 Step 1: Read the Job Description
- Use the `read_jd` action to extract text from the file at `{jd_path}`
- Then, call `update_status` with "✅ JD Loaded - Navigating to LinkedIn"

🔹 Step 2: Open LinkedIn Talent Solutions
- Navigate to https://www.linkedin.com/talent/home (type and press enter if needed)
- Wait for page to load
- Then, call `update_status` with "🔍 Starting LinkedIn candidate search"

🔹 Step 3: Search for candidates
- Start a new search based on the job description contents
- Use a relevant job title (e.g., from filename or PDF text)
- Type the job title in the search box and start the search

🔹 Step 4: Apply location filters
- Call `update_status` with "🌍 Applying location filters"
- Click on "+ Candidate geographic locations"
- For each of the following locations, do the following:
{filters}
    - Type the country name in the input
    - You will see a list of suggestions, click on the first one to select it (You MUST click it to apply the filter)
    - Make sure to select the country from the list, not just type it in
    - Do not proceed until the location filter is applied
    - Wait for the results to update before continuing to the next country

🔹 Step 5: Analyze candidates
- Scroll the page to load more candidates when needed
- Call `update_status` with "🔍 Analyzing candidates"
- For each candidate:
    - Click to open the profile
    - Extract: name, profile URL, location, and skills
    - Match their skills against the JD requirements
    - Calculate a match score from 0–100%
    - Call `update_status` with "💾 Saving results for [name]"
    - Call `save_candidates` with all data

- After saving, return to the list view and repeat for next candidate
- Stop after 25 steps or when enough candidates are saved
- It's okay if not all candidates are analyzed due to step or time limits. The task is considered **successful** as long as some qualified candidates have been evaluated and saved.

Do not skip location filters. Only analyze candidates *after* filters are applied.
"""

logger = logging.getLogger(__name__)

def get_browser():
    return Browser(
        config=BrowserConfig(
            headless=False,
            chrome_instance_path="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
        )
    )

def get_agent(jd_path: str, countries: list, browser):
    filters = "\n".join(f"- {c}" for c in countries)
    task = TASK_TEMPLATE.format(jd_path=jd_path, filters=filters)

    return Agent(
        task=task,
        llm=ChatBedrockConverse(model_id="anthropic.claude-3-5-sonnet-20240620-v1:0", temperature=0.0),
        browser=browser,
        controller=controller,
    )

def run_agent_background(jd_path, countries, selected_jd_filename):
    try:
        job_title = extract_job_title(selected_jd_filename)
        logger.info(f"🧠 Background agent start: JD={jd_path}, Countries={countries}, Job={job_title}")
        browser = get_browser()
        agent = get_agent(jd_path, countries, browser)
        asyncio.run(agent.run(max_steps=25))
        asyncio.run(browser.close())
        shared_status.set("__DONE__")
    except Exception as e:
        logger.error("❌ Background agent failed", exc_info=True)
        shared_status.set(f"__ERROR__: {str(e)}")
