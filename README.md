# 🔍 LinkedIn Candidate Finder

This app automates the process of finding qualified candidates on LinkedIn Talent Solutions using a Job Description PDF and AI agents.

It parses job descriptions, applies location filters, extracts profiles, compares candidate skills, calculates match scores, and saves results to an Excel template.

Built with **Streamlit**, **LangChain**, **Bedrock Claude**, and the **Browser-Use** agent framework.

---

## 🚀 Features

- 📄 Upload a Job Description (PDF)
- 🌍 Filter candidates by country or location
- 🧠 Uses AI to read the JD and search LinkedIn
- 🧬 Compares candidate skills to JD requirements
- 📊 Calculates match scores (0–100%)
- 📁 Saves results to Excel for easy review
- 🖼️ Preview results in table or card view
- 📥 Downloadable Excel file per JD

---

## ⚙️ Requirements

- Python 3.11+
- `playwright` (installed separately)
- AWS access to Bedrock Claude 3

---

## 📦 Installation

### 1. Clone the Repository
```bash
git clone https://github.com/EncoraDigital/COE-GenAI-Demo-TAOperator.git
cd LinkedIn-Candidate-Finder
```

### 2. Set Up Virtual Environment
```bash
python -m venv venv
source venv/bin/activate  # or .\venv\Scripts\activate on Windows
```

### 3. Install Python Dependencies
```bash
pip install -r requirements.txt
```

### 4. Install Playwright Browsers
```bash
playwright install
```

### 5. Set Up Environment Variables
Copy the example `.env` file and configure it:
```bash
cp .env.example .env  # macOS/Linux
copy .env.example .env  # Windows
```
Then, open the `.env` file and update your AWS credentials and Bedrock model settings:
```
AWS_ACCESS_KEY_ID=your_key
AWS_SECRET_ACCESS_KEY=your_secret
AWS_REGION=us-east-1
```

---

## 🧠 Usage (Streamlit)

### 1. Launch the app
```bash
streamlit run app.py
```

### 2. Upload a Job Description
- Upload a `.pdf` describing the job (e.g. `Senior_Azure_SRE.pdf`)
- Select the JD from the dropdown list

### 3. Select Candidate Locations
- Choose one or more countries (e.g. `Costa Rica`, `Mexico`, `Peru`, `Argentina`)
- Add custom cities or locations manually

### 4. Run the Agent
Click 🚀 **Run Agent** and watch it search LinkedIn!

### 5. Review the Results
- View candidates as a **📊 table** or **📇 card view**
- Download results as an `.xlsx` file (based on the JD name)

---

## 📝 Customization

### **Update the Excel Template**
- Modify `Template.xlsx` to match your preferred format. Ensure the following cells are used:
  - **Date**: `B3`
  - **Job Title**: `B5`
  - **Candidate Table**: `A11:E26`

### **Adjust the Prompt**
- Edit the `TASK_TEMPLATE` variable in the file `agent_runner.py` to change the search criteria, skill comparison, or match score calculation.

---

## 📁 File Structure

```
LinkedIn-Candidate-Finder/
├── app.py                  # Main Streamlit app
├── actions.py              # JD reader, Excel saving, status updates
├── agent_runner.py         # Threaded agent execution
├── config.py               # Paths, shared status, task templates
├── file_manager.py         # Output path + Excel loaders
├── utils.py                # Helper utils (job title, parsing, etc)
├── Template.xlsx           # Excel result template
├── requirements.txt        # Dependencies
├── .env                    # Environment variables
├── /JDs/                   # Job description PDFs
├── /output/                # Generated Excel result files
└── README.md               
```

---

## 🧪 Troubleshooting

| Problem | Fix |
|--------|------|
| Excel not generated | Ensure at least one candidate is found |
| Can't click LinkedIn filters | Make sure you're logged into a LinkedIn recruiter account |
| Playwright error | Run `playwright install` |
| Claude model fails | Check if your AWS Bedrock access is valid |

---