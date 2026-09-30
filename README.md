# 🤖 AI-Powered Candidate Ranking System

<p align="center">
  <img src="https://img.shields.io/badge/AI-Recruitment%20Intelligence-6366f1?style=for-the-badge&logo=openai&logoColor=white" />
  <img src="https://img.shields.io/badge/NLP-Semantic%20Matching-8b5cf6?style=for-the-badge" />
  <img src="https://img.shields.io/badge/Python-Flask-3776ab?style=for-the-badge&logo=python&logoColor=white" />
  <img src="https://img.shields.io/badge/ML-Sentence--BERT-ff6f00?style=for-the-badge" />
  <img src="https://img.shields.io/badge/UI-Glassmorphism-ec4899?style=for-the-badge" />
</p>

<p align="center">
  <strong>An AI-powered recruitment-support platform that analyzes resumes, compares candidate profiles with job requirements, calculates explainable fit scores, and provides actionable recruitment insights.</strong>
</p>

<p align="center">
  <a href="#-project-overview">Overview</a> •
  <a href="#-core-features">Features</a> •
  <a href="#-ai-pipeline">AI Pipeline</a> •
  <a href="#-analytics-dashboard">Analytics</a> •
  <a href="#-technology-stack">Tech Stack</a> •
  <a href="#-quick-start">Run Locally</a>
</p>

---

# 🚀 Project Overview

**AI-Powered Candidate Ranking System** is an independently developed recruitment-support application designed to help recruiters analyze and compare candidate resumes against a job description.

The system combines:

* 🧠 Semantic matching
* 📄 Resume and job-description parsing
* 🎯 Multi-dimensional candidate scoring
* 📊 Recruitment analytics
* 🔍 Skill-gap analysis
* 📈 Candidate potential indicators
* ⚖️ Bias auditing
* 💬 Recruiter assistance
* 🧩 Explainable candidate evaluation
* 📑 Recruitment reporting
* ⭐ Candidate shortlisting
* 🔗 Candidate similarity analysis

Instead of relying only on exact keyword matching, the application combines explicit skill evidence with semantic similarity, experience, project relevance, education, certifications, and behavioral signals.

> **Development Note:** The application code, interface, scoring workflow, and project-specific modules were independently developed. Third-party libraries and the pre-trained embedding model are used as dependencies and are credited in the technology and attribution sections.

---

# 🌟 What the System Does

The platform follows a complete recruitment-analysis workflow:

```text
             JOB DESCRIPTION
                    │
                    ▼
          ┌──────────────────┐
          │ Document Parsing │
          └────────┬─────────┘
                   │
                   ▼
          ┌──────────────────┐
          │ Resume Parsing   │
          └────────┬─────────┘
                   │
        ┌──────────┼───────────┐
        ▼          ▼           ▼
     Skills    Experience   Behavioral
        │          │           │
        └──────────┼───────────┘
                   ▼
         Semantic Embeddings
                   │
                   ▼
        7-Dimension Scoring
                   │
                   ▼
          Ranking Engine
                   │
       ┌───────────┼────────────┐
       ▼           ▼            ▼
   Analytics    Skill Gaps   Potential
       │           │            │
       ├───────────┼────────────┤
       ▼           ▼            ▼
     Bias      Interview      AI
    Audit      Questions    Summaries
       │           │            │
       └───────────┼────────────┘
                   ▼
        Recruiter Assistant
                   │
                   ▼
        Reports / Export
```

---

# 💎 Core Features

## 🧠 1. Semantic Candidate Matching

The system uses **Sentence-BERT embeddings** to compare the meaning of job requirements and candidate information.

This allows the system to go beyond simple exact keyword matching.

### Example

```text
Job Requirement
"Experience developing scalable backend applications"

Candidate Resume
"Built and deployed production-ready REST APIs
using Python, Flask and PostgreSQL"
```

The semantic matching layer can identify meaningful relationships between related concepts even when the wording differs.

---

# 🎯 2. Seven-Dimensional Candidate Scoring

Candidates are evaluated using seven weighted dimensions.

| Dimension           | Weight | What It Measures                     |
| ------------------- | -----: | ------------------------------------ |
| Skill Match         |    35% | Keyword and semantic skill alignment |
| Experience          |    20% | Experience relevance and duration    |
| Project Relevance   |    15% | Relevance and depth of projects      |
| Semantic Similarity |    15% | Meaning-level JD/resume similarity   |
| Education           |     5% | Degree-level alignment               |
| Certifications      |     5% | Certification relevance              |
| Behavioral          |     5% | Leadership, impact, publications     |

Profile completeness is also calculated separately and is **not included in the final weighted score**.

### Scoring Architecture

```text
                    CANDIDATE
                       │
       ┌───────────────┼────────────────┐
       ▼               ▼                ▼
    Skills         Experience        Projects
      35%              20%              15%
       │               │                │
       └───────────────┼────────────────┘
                       │
             Semantic Similarity
                       │
                      15%
                       │
          ┌────────────┼────────────┐
          ▼            ▼            ▼
     Education    Certifications  Behavioral
        5%              5%             5%
          │            │            │
          └────────────┼────────────┘
                       ▼
                 FINAL FIT SCORE
```

---

# 🔍 3. Explainable Candidate Rankings

The system does not only return a numerical score.

Each candidate can receive an interpretable breakdown covering:

```text
Candidate
│
├── Skill Match
│   ├── Required Skills ✓
│   ├── Preferred Skills ✓
│   └── Missing Skills △
│
├── Experience
│   └── Parsed Experience
│
├── Project Relevance
│   └── Relevance Analysis
│
├── Semantic Similarity
│   └── JD / Resume Similarity
│
├── Education
│   └── Degree Alignment
│
├── Certifications
│   └── Relevant Certifications
│
└── Behavioral Signals
    ├── Leadership
    ├── Impact
    ├── Publications
    └── Presentations
```

This provides recruiters with more context than a ranking number alone.

---

# 🧠 4. Intelligent Resume & JD Parsing

The NLP parsing layer extracts structured information from uploaded documents.

### Extracted Information

* Technical skills
* Experience
* Education
* Certifications
* Projects
* Behavioral signals
* Leadership indicators
* Impact indicators
* Publications
* Presentations

The system contains a technical skill extraction layer covering **200+ technical skills across multiple categories**.

### Supported Documents

```text
PDF
DOCX
TXT
```

---

# 📈 5. Candidate Potential Indicators

The system provides additional heuristic indicators based on candidate profile information.

Potential analysis can use signals such as:

* Profile information
* Project depth
* Technical breadth
* Career-path indicators
* Learning-related indicators
* Other extracted profile signals

The potential indicator is presented as an **additional recruitment-support metric**, separate from the main weighted fit score.

---

# 🔎 6. Skill Gap Analysis

The system identifies missing skills between the candidate profile and job requirements.

### Example

```text
Required Skills

✓ Python
✓ SQL
✓ REST API
✗ Docker
✗ Kubernetes
```

### Preferred Skills

```text
✓ Git
✓ AWS
△ React
✗ Terraform
```

The system can also provide learning recommendations for identified gaps.

---

# 🎤 7. Interview Question Generator

The application can generate tailored interview questions based on candidate and role information.

Question categories include:

* Technical
* Projects
* Experience
* Behavioral
* Problem solving
* Role-specific skills
* Scenario-based questions
* Difficulty-based questions

### Example

```text
Candidate Skill
      │
      ▼
     Docker
      │
      ▼
Interview Question

"Explain how you would containerize
and deploy a backend API using Docker."
```

The source implementation provides **8 categories of tailored questions with difficulty levels**.

---

# ⚖️ 8. Bias Audit & Anonymization

The system provides a separate bias-audit report using text masking for selected personal indicators.

### Indicators Checked

| Indicator           | Audit Treatment |
| ------------------- | --------------- |
| Names               | Text masking    |
| Email addresses     | Text masking    |
| Phone numbers       | Text masking    |
| Addresses           | Text masking    |
| Gender pronouns     | Text masking    |
| Age indicators      | Text masking    |
| Photo-related terms | Text masking    |

```text
Candidate Resume
       │
       ▼
Personal Indicator Detection
       │
       ▼
Text Masking
       │
       ▼
Bias Audit Report
       │
       ▼
Recruiter Review
```

### Important Implementation Limitation

The current implementation performs the bias audit **after candidate ranking** and does not rerun the ranking using anonymized resume text.

Therefore, the feature **does not guarantee that rankings are free from bias**.

Masking is pattern-based and may not identify every personal indicator or indirect source of bias. Human review and organizational hiring policies remain important.

---

# 🤖 9. Recruiter Assistant

The application includes a natural-language recruiter assistant that can answer questions about the current candidate results.

### Example Questions

```text
"Show top 5 candidates"

"Candidates with Python and AWS skills"

"Who lacks Kubernetes experience?"

"Compare Sneha and Karan"

"Tell me about Divya"

"Which candidates best match this role, and why?"

"What's the average candidate score?"

"What skills are most common?"

"Show me a summary of all candidates"
```

### Assistant Architecture

```text
Recruiter Question
       │
       ▼
Natural Language Query
       │
       ▼
Candidate Results
       │
       ▼
Recruitment Context
       │
       ▼
Structured Response
```

---

# 📊 Analytics Dashboard

The system includes an advanced recruitment analytics dashboard.

## 📌 Score Distribution

Visualizes candidate score tiers.

```text
Excellent  █████████████████
Good       ███████████
Moderate   ███████
Low        ███
```

Score categories are configurable around:

```text
Excellent     80%+
Good          60–80%
Moderate      40–60%
Low           <40%
```

---

## 🧩 Skill Coverage

Shows the distribution of skills across the candidate pool.

```text
Python        █████████████████
SQL           ███████████████
Java          ███████████
AWS           █████████
Docker        ██████
Kubernetes    ████
```

---

## 💼 Experience Distribution

The dashboard can visualize experience levels:

```text
Senior
Mid
Junior
Entry
```

The configured ranges are:

```text
Senior        7+ years
Mid           3–6 years
Junior        1–2 years
Entry         <1 year
```

---

# 📈 Potential vs Fit

The analytics dashboard can compare candidate fit scores with potential indicators.

```text
FIT
│
│          ●
│       ●
│   ●        ●
│
│ ●
└──────────────────── POTENTIAL
```

This gives recruiters another way to inspect differences between current role fit and profile-based potential indicators.

---

# ☁️ Skills Word Cloud

The system provides a visual representation of skill frequency across the candidate pool.

```text
          PYTHON

    SQL          JAVA

        REACT

 AWS          DOCKER

      JAVASCRIPT
```

Frequently occurring skills become easier to identify across the candidate dataset.

---

# ⚙️ Custom Scoring Weights

The application provides interactive controls for adjusting scoring dimensions.

```text
Skill Match          ███████████████ 35%
Experience           ████████        20%
Project Relevance    ██████          15%
Semantic Similarity  ██████          15%
Education            ██               5%
Certifications       ██               5%
Behavioral           ██               5%
```

The configured weights can be adjusted through the dashboard and used for candidate-score recalculation.

---

# ⭐ Candidate Shortlisting

The application includes a dedicated candidate shortlisting workflow.

### Features

* ⭐ Star/unstar candidates
* 💾 Persistent browser storage
* 📌 Dedicated shortlist tab
* 🔢 Live shortlist counter
* 📤 Export shortlisted candidates
* ☑️ Multi-select candidates
* ⚡ Bulk operations

Shortlist information is persisted using:

```javascript
localStorage
```

---

# 🔍 Advanced Search, Filtering & Sorting

The dashboard provides multiple ways to explore candidate results.

## Search

Candidates can be searched by name and through the candidate results interface.

## Score Filtering

```text
Excellent     80%+
Good          60–80%
Moderate      40–60%
Low           <40%
```

## Experience Filtering

```text
Senior        7+ years
Mid           3–6 years
Junior        1–2 years
Entry         <1 year
```

## Shortlist Filtering

```text
All
Shortlisted Only
Not Shortlisted
```

## Sorting

Candidate table columns support:

```text
Ascending
    ↓
Descending
```

The filtering system operates on the actual candidate data rather than relying on DOM parsing.

---

# ⚡ Batch Operations

Multiple candidates can be selected for bulk actions.

```text
☑ Candidate A
☑ Candidate B
☑ Candidate C
☐ Candidate D
```

The dynamic bulk-action bar can provide operations such as:

```text
┌────────────────────────────────────┐
│ 3 Candidates Selected              │
│                                    │
│ ⭐ Shortlist                       │
│ 📤 Export                          │
│ 🔎 Compare                         │
└────────────────────────────────────┘
```

---

# 🔗 Candidate Similarity Matrix

The similarity matrix provides a visual representation of skill overlap between candidates.

```text
             A       B       C       D
        ┌──────────────────────────────
A       │ 100%    82%     54%     31%
B       │ 82%    100%     61%     42%
C       │ 54%     61%    100%     73%
D       │ 31%     42%     73%    100%
```

The matrix can help identify:

* Similar candidate profiles
* Highly overlapping skills
* Unique candidate profiles
* Candidate clusters

---

# 📑 Recruitment Reports & Export

The application supports recruitment reporting and result export.

### Report Information

Reports can include:

* Candidate rankings
* Score breakdowns
* Analytics
* Skill gaps
* Candidate summaries
* Recruitment insights
* Comparative information

### Export Formats

```text
JSON
CSV
PDF / Print-to-PDF
```

---

# 🎨 Premium User Interface

The frontend uses a modern **glassmorphism-inspired recruitment dashboard**.

### Design Elements

* Frosted glass cards
* Micro-interactions
* Soft borders
* Blur effects
* Animated components
* Responsive layouts
* KPI cards
* Interactive charts
* Modal interfaces

---

# ✨ Motion & Interaction

The interface includes:

* Animated statistics
* Count-up statistics
* Particle background
* Hover effects
* Skeleton loading
* Modal animations
* Dynamic progress indicators
* Smooth theme transitions

---

# 🌙 Dark / Light Theme

Users can switch between:

```text
☀️ Light Mode
🌙 Dark Mode
```

Theme preference is persisted using browser storage.

---

# 📱 Responsive Design

The dashboard is designed for:

```text
Desktop
   │
   ├── Full Dashboard
   │
Tablet
   │
   └── Adaptive Layout
   │
Mobile
   │
   └── Responsive Interface
```

---

# ⌨️ Power User Keyboard Shortcuts

| Shortcut           | Action                  |
| ------------------ | ----------------------- |
| `Ctrl + Enter`     | Run analysis            |
| `Ctrl + 1–6`       | Switch dashboard tabs   |
| `Ctrl + Shift + T` | Toggle dark/light theme |
| `Esc`              | Close modal             |
| `/`                | Focus search input      |

---

# 🧭 Complete Application Workflow

```text
┌────────────────────────┐
│ Upload Job Description │
└───────────┬────────────┘
            ▼
┌────────────────────────┐
│ Upload Candidate       │
│ Resumes                │
└───────────┬────────────┘
            ▼
┌────────────────────────┐
│ NLP Document Parsing   │
└───────────┬────────────┘
            ▼
┌────────────────────────┐
│ Skill Extraction       │
└───────────┬────────────┘
            ▼
┌────────────────────────┐
│ Experience Analysis    │
└───────────┬────────────┘
            ▼
┌────────────────────────┐
│ Semantic Embeddings    │
└───────────┬────────────┘
            ▼
┌────────────────────────┐
│ 7-Dimension Scoring    │
└───────────┬────────────┘
            ▼
┌────────────────────────┐
│ Candidate Ranking      │
└───────────┬────────────┘
            │
     ┌──────┼─────────┐
     ▼      ▼         ▼
 Analytics  Gaps   Potential
     │      │         │
     └──────┼─────────┘
            ▼
     Candidate Details
            │
     ┌──────┼──────────────┐
     ▼      ▼              ▼
  Copilot  Bias Audit   Interview
                       Questions
     │      │              │
     └──────┼──────────────┘
            ▼
      Reports / Export
```

---

# 📡 API Architecture

The Flask backend exposes **14 primary API routes**.

| Method | Endpoint                           | Purpose                       |
| ------ | ---------------------------------- | ----------------------------- |
| `GET`  | `/api/health`                      | Health check and model status |
| `POST` | `/api/analyze`                     | Analyze JD and resumes        |
| `POST` | `/api/analyze-sample`              | Run sample analysis           |
| `POST` | `/api/copilot`                     | Recruiter assistant query     |
| `POST` | `/api/copilot/clear`               | Clear assistant history       |
| `POST` | `/api/compare`                     | Compare candidates            |
| `GET`  | `/api/analytics`                   | Recruitment analytics         |
| `GET`  | `/api/skill-gaps/<index>`          | Candidate skill gaps          |
| `GET`  | `/api/interview-questions/<index>` | Interview questions           |
| `GET`  | `/api/potential/<index>`           | Candidate potential           |
| `GET`  | `/api/bias-report/<index>`         | Bias-audit report             |
| `GET`  | `/api/candidate-summary/<index>`   | Candidate summary             |
| `GET`  | `/api/export`                      | JSON/CSV export               |
| `GET`  | `/api/download`                    | Ranked candidate CSV          |

---

# 🧠 AI Engine Architecture

## 1. Document Parsing

The parsing engine processes job descriptions and resumes.

```text
PDF / DOCX / TXT
       │
       ▼
Document Extraction
       │
       ▼
Structured Candidate Data
       │
       ├── Skills
       ├── Experience
       ├── Education
       ├── Certifications
       ├── Projects
       └── Behavioral Signals
```

---

## 2. Semantic Embedding Engine

### Model

```text
all-MiniLM-L6-v2
```

### Embedding Size

```text
384 dimensions
```

### Processing

```text
Job Description
       │
       ▼
Text Representation
       │
       ▼
384-Dimensional Embedding
       │
       │
Candidate Resume
       │
       ▼
384-Dimensional Embedding
       │
       ▼
Similarity Calculation
```

The system also includes a **TF-IDF fallback** if the Sentence-Transformer model cannot be loaded.

---

# 🧮 Hybrid Scoring Architecture

The scoring engine combines multiple sources of evidence.

```text
                    FINAL SCORE
                         │
        ┌────────────────┼─────────────────┐
        ▼                ▼                 ▼
   Skill Match       Experience        Projects
      35%               20%               15%
        │                │                 │
        └────────────────┼─────────────────┘
                         │
                  Semantic Similarity
                         15%
                         │
              ┌──────────┴──────────┐
              ▼                     ▼
         Education             Certifications
            5%                      5%
              │                     │
              └──────────┬──────────┘
                         ▼
                    Behavioral
                        5%
```

The implementation combines keyword matching, semantic similarity, experience scoring, project relevance, education, certifications, and behavioral signals.

---

# 🧩 Enrichment Layer

After the core scoring process, the system provides additional candidate intelligence.

```text
             RANKING ENGINE
                   │
        ┌──────────┼──────────┐
        ▼          ▼          ▼
    Skill Gaps  Potential   Interview
                           Questions
        │          │          │
        └──────────┼──────────┘
                   ▼
              Bias Audit
                   │
                   ▼
             AI Summaries
```

### Enrichment Modules

* Skill-gap analysis
* Candidate potential indicators
* Interview question generation
* Bias audit
* Candidate summaries

---

# 📁 Project Architecture

```text
candidate-ranking-system/
│
├── app.py
├── requirements.txt
├── test_backend.py
├── TASK_PLAN.md
├── README.md
│
├── models/
│   ├── __init__.py
│   ├── embedding_model.py
│   ├── parser.py
│   ├── scorer.py
│   ├── ranking_engine.py
│   ├── skill_gap_analyzer.py
│   ├── interview_generator.py
│   ├── bias_evaluator.py
│   └── copilot.py
│
├── frontend/
│   ├── index.html
│   ├── script.js
│   └── style.css
│
├── data/
│   ├── jobs/
│   ├── resumes/
│   ├── outputs/
│   └── uploads/
│
├── scripts/
│   └── rank_candidates.py
│
├── reports/
│
└── docs/
```

The project structure includes the Flask application, modular AI components, frontend interface, sample data, generated outputs, scripts, reports, and documentation.

---

# 🛠️ Technology Stack

## Backend

| Technology | Purpose                      |
| ---------- | ---------------------------- |
| Python 3   | Core programming language    |
| Flask      | Web server and REST API      |
| Flask-CORS | Cross-origin request support |

## AI / NLP

| Technology            | Purpose                     |
| --------------------- | --------------------------- |
| Sentence Transformers | Semantic embeddings         |
| `all-MiniLM-L6-v2`    | Pre-trained embedding model |
| scikit-learn          | ML and vector processing    |
| NumPy                 | Numerical processing        |
| Pandas                | Data processing             |

## Document Processing

| Technology  | Purpose        |
| ----------- | -------------- |
| PyPDF2      | PDF parsing    |
| pdfplumber  | PDF extraction |
| python-docx | DOCX parsing   |

## Frontend

| Technology       | Purpose               |
| ---------------- | --------------------- |
| HTML5            | Application structure |
| CSS3             | Glassmorphism UI      |
| JavaScript ES6   | Frontend logic        |
| Chart.js 4.4     | Data visualization    |
| Font Awesome 6.5 | Icons                 |
| Inter            | Interface typography  |

## Storage

```text
Browser LocalStorage
        │
        ├── Candidate Shortlist
        │
        └── Theme Preference
```

---

# 🚀 Quick Start

## Prerequisites

Make sure you have:

```text
Python 3.8+
pip
Modern Web Browser
```

---

## 1️⃣ Clone the Repository

```bash
git clone https://github.com/kala3013/candidate-ranking-system.git
```

---

## 2️⃣ Enter the Project

```bash
cd candidate-ranking-system
```

---

## 3️⃣ Install Dependencies

```bash
pip install -r requirements.txt
```

---

## 4️⃣ Start the Application

```bash
python app.py
```

The Flask server starts at:

```text
http://localhost:5000
```

---

## 5️⃣ Open the Dashboard

Open:

```text
http://localhost:5000
```

---

# 🎯 Try Sample Analysis

The application provides built-in sample data for quickly testing the complete workflow.

```text
Launch Dashboard
       ↓
Try with Sample Data
       ↓
AI Processing
       ↓
Candidate Ranking
       ↓
Analytics Dashboard
       ↓
Candidate Details
```

The sample workflow allows the application to be tested without preparing external resume files.

---

# 📤 Analyze Your Own Candidates

## Step 1 — Upload Job Description

Supported formats:

```text
PDF
DOCX
TXT
```

You can also paste the job-description text directly.

## Step 2 — Upload Resumes

Upload one or multiple candidate resumes.

```text
PDF
DOCX
TXT
```

## Step 3 — Start Analysis

Click:

```text
🚀 Analyze & Rank Candidates
```

## Step 4 — Explore Results

```text
Rankings
   ↓
Candidate Details
   ↓
Skill Gaps
   ↓
Potential
   ↓
Analytics
   ↓
Interview Questions
   ↓
Bias Audit
   ↓
Recruiter Assistant
   ↓
Reports / Export
```

---

# 📊 Operational Profile

| Item            | Details                                                                   |
| --------------- | ------------------------------------------------------------------------- |
| Embedding Model | `all-MiniLM-L6-v2`                                                        |
| Embedding Size  | 384 dimensions                                                            |
| Supported Files | PDF / DOCX / TXT                                                          |
| Maximum Upload  | 50 MB total                                                               |
| Analysis Time   | Depends on hardware, model initialization, file size, and candidate count |

---

# 🧩 AI Module Map

```text
01 ─ Document Parser
02 ─ Skill Extraction
03 ─ Experience Analyzer
04 ─ Semantic Embedding Engine
05 ─ Hybrid Scoring Engine
06 ─ Ranking Engine
07 ─ Skill Gap Analyzer
08 ─ Candidate Potential Engine
09 ─ Interview Generator
10 ─ Bias Evaluator
11 ─ Recruiter Assistant
```

These modules operate as an integrated recruitment-support pipeline.

---

# 📋 Feature Matrix

| Capability                     | Status |
| ------------------------------ | :----: |
| Resume Parsing                 |    ✅   |
| Job Description Parsing        |    ✅   |
| Semantic Matching              |    ✅   |
| Skill Extraction               |    ✅   |
| Experience Analysis            |    ✅   |
| Project Relevance              |    ✅   |
| Multi-dimensional Scoring      |    ✅   |
| Candidate Ranking              |    ✅   |
| Explainable Results            |    ✅   |
| Bias Audit                     |    ✅   |
| Skill Gap Analysis             |    ✅   |
| Candidate Potential Indicators |    ✅   |
| Interview Questions            |    ✅   |
| Recruiter Assistant            |    ✅   |
| Analytics Dashboard            |    ✅   |
| Candidate Comparison           |    ✅   |
| Similarity Matrix              |    ✅   |
| Candidate Shortlisting         |    ✅   |
| Batch Operations               |    ✅   |
| JSON Export                    |    ✅   |
| CSV Export                     |    ✅   |
| PDF / Print Report             |    ✅   |
| Dark / Light Theme             |    ✅   |
| Keyboard Shortcuts             |    ✅   |
| Responsive UI                  |    ✅   |

---

# 🔐 Privacy & Data Handling

The core workflow is designed to operate locally.

```text
Candidate Files
      │
      ▼
Local Flask Application
      │
      ▼
Local NLP / ML Processing
      │
      ▼
Local Candidate Results
```

The application supports local document processing and uses the local Flask application for the core workflow.

For production use with real candidate information, additional security measures should be implemented, including:

* Authentication
* Authorization
* Encryption
* Secure file storage
* Access control
* Data retention policies
* Privacy compliance
* Audit logging

---

# ⚠️ Responsible Use

This application is a **recruitment decision-support tool**, not an autonomous hiring system.

Recruiters remain responsible for:

* Reviewing candidate information
* Validating system-generated results
* Considering relevant evidence
* Conducting interviews
* Applying organizational hiring policies
* Making final hiring decisions

The bias-audit feature is also not a guarantee of fairness because the current implementation performs auditing after ranking and relies on pattern-based masking.

---

# 🧪 Testing

Backend verification can be performed using:

```bash
python test_backend.py
```

Testing can be used to verify:

```text
API Availability
       ↓
Model Loading
       ↓
Candidate Processing
       ↓
Ranking Calculations
       ↓
Export Functions
       ↓
Endpoint Responses
```

---

# 📸 Dashboard Showcase

Add your actual screenshots here to make the GitHub repository more visually impressive.

## 🏠 Main Dashboard

```text
[ Add dashboard screenshot here ]
```

## 🏆 Candidate Rankings

```text
[ Add rankings screenshot here ]
```

## 📊 Analytics Dashboard

```text
[ Add analytics screenshot here ]
```

## 🤖 Recruiter Assistant

```text
[ Add assistant screenshot here ]
```

## ⚖️ Bias Audit

```text
[ Add bias-audit screenshot here ]
```

## 🔗 Candidate Similarity

```text
[ Add similarity-matrix screenshot here ]
```

## 📱 Responsive Interface

```text
[ Add mobile screenshot here ]
```

---

# 🎬 Recommended Demo Flow

For a project demonstration, use this sequence:

```text
1. Open Dashboard
       ↓
2. Toggle Dark / Light Theme
       ↓
3. Upload Job Description
       ↓
4. Upload Multiple Resumes
       ↓
5. Run Analysis
       ↓
6. Show Candidate Rankings
       ↓
7. Open Candidate Details
       ↓
8. Show Skill Gap Analysis
       ↓
9. Show Potential Indicators
       ↓
10. Open Analytics
       ↓
11. Compare Candidates
       ↓
12. Add Candidates to Shortlist
       ↓
13. Use Recruiter Assistant
       ↓
14. Generate Recruitment Report
       ↓
15. Export Results
```

This demonstrates the complete end-to-end workflow.

---

# 🔮 Future Roadmap

Potential future improvements include:

## 🤖 Advanced AI

* LLM-powered candidate explanations
* Retrieval-Augmented Generation
* Role-specific semantic models
* Multilingual resume analysis
* Advanced career trajectory analysis
* Improved contextual skill extraction

## 👥 Recruitment Workflow

* Recruiter authentication
* Candidate portals
* Interview scheduling
* Interview feedback management
* Recruitment pipeline management
* Recruiter workspaces

## 📊 Analytics

* Historical recruitment analytics
* Recruitment funnel visualization
* Team-level dashboards
* Advanced skill analytics
* Historical candidate comparison
* Recruitment trend analysis

## ☁️ Infrastructure

* Docker deployment
* PostgreSQL integration
* Redis caching
* Cloud deployment
* CI/CD pipelines
* Production monitoring

## 🔐 Enterprise Security

* Role-based access control
* Encryption
* Secure file storage
* Audit logging
* Data retention controls
* Authentication and authorization

---

# 🏗️ Architecture at a Glance

```text
              AI CANDIDATE RANKING SYSTEM
                         │
             ┌───────────┴───────────┐
             │                       │
         FRONTEND                 BACKEND
             │                       │
       HTML / CSS / JS            Flask API
             │                       │
             └───────────┬───────────┘
                         │
                   AI PROCESSING
                         │
        ┌────────────────┼────────────────┐
        ▼                ▼                ▼
     Parsing         Embeddings        Scoring
        │                │                │
        └────────────────┼────────────────┘
                         ▼
                  Ranking Engine
                         │
        ┌────────────────┼────────────────┐
        ▼                ▼                ▼
    Analytics        Skill Gaps        Potential
        │                │                │
        └────────────────┼────────────────┘
                         ▼
              Interview Questions
                         │
                         ▼
                    Bias Audit
                         │
                         ▼
               Recruiter Assistant
                         │
                         ▼
                 Reports & Export
```

---

# 💡 Engineering Highlights

This project demonstrates practical experience in:

* 🐍 Python development
* 🌐 Flask REST API development
* 🧠 Natural Language Processing
* 🤖 Semantic embeddings
* 📊 Multi-dimensional scoring
* 📄 Document parsing
* 🎯 Candidate ranking
* ⚖️ Bias auditing
* 🔍 Explainable candidate analysis
* 📈 Data visualization
* 🎨 Modern frontend development
* 💾 Browser persistence
* 📤 Data export
* 🧩 Modular architecture
* 🔌 API-driven application design
* 📱 Responsive web development

---

# 🏆 Project Highlights

```text
┌──────────────────────────────────────────────┐
│                                              │
│        🤖 AI CANDIDATE RANKING SYSTEM        │
│                                              │
│       Intelligent Recruitment Support        │
│                                              │
│   🧠 Semantic Matching                       │
│   🎯 Multi-Dimensional Scoring              │
│   🔍 Explainable Rankings                   │
│   📊 Recruitment Analytics                  │
│   ⚖️ Bias Audit                             │
│   📈 Candidate Potential                    │
│   🧩 Skill Gap Analysis                     │
│   🎤 Interview Questions                    │
│   🤖 Recruiter Assistant                    │
│   ⭐ Candidate Shortlisting                 │
│   🔗 Similarity Matrix                      │
│   📑 Recruitment Reports                    │
│   🎨 Premium Dashboard                      │
│                                              │
└──────────────────────────────────────────────┘
```

---

# 👨‍💻 Developer

<p align="center">

### Kalanidhi M C

**Computer Science Engineering Student | Software Developer | AI & Full Stack Enthusiast**

</p>

<p align="center">

<a href="https://github.com/kala3013">
<img src="https://img.shields.io/badge/GitHub-kala3013-181717?style=for-the-badge&logo=github&logoColor=white" />
</a>

<a href="mailto:kalanidhimurugan@gmail.com">
<img src="https://img.shields.io/badge/Email-kalanidhimurugan%40gmail.com-EA4335?style=for-the-badge&logo=gmail&logoColor=white" />
</a>

</p>

---

# 📫 Connect

<p align="center">

<a href="mailto:kalanidhimurugan@gmail.com">
<img src="https://img.shields.io/badge/Email-kalanidhimurugan%40gmail.com-EA4335?style=for-the-badge&logo=gmail&logoColor=white" />
</a>

<a href="https://github.com/kala3013">
<img src="https://img.shields.io/badge/GitHub-kala3013-181717?style=for-the-badge&logo=github&logoColor=white" />
</a>

</p>

---

# ⭐ Support

If you find this project useful or interesting:

⭐ Star the repository
🍴 Fork the project
🐛 Report issues
💡 Suggest improvements
🤝 Contribute

---

# 📜 Dependencies & Attribution

The application code, interface, scoring workflow, and project-specific modules were independently developed.

The project uses open-source third-party libraries and a pre-trained embedding model, including:

```text
Flask
Flask-CORS
Sentence Transformers
all-MiniLM-L6-v2
PyPDF2
pdfplumber
python-docx
Pandas
NumPy
scikit-learn
Chart.js
Font Awesome
```

These dependencies are used as supporting technologies and are **not claimed as original work**.

---

# 📌 System Summary

```text
Job Description
      +
Candidate Resumes
      │
      ▼
Document Parsing
      │
      ▼
Skill & Experience Extraction
      │
      ▼
Semantic Embeddings
      │
      ▼
7-Dimensional Scoring
      │
      ▼
Candidate Ranking
      │
      ├── Analytics
      ├── Skill Gaps
      ├── Potential Indicators
      ├── Interview Questions
      ├── Bias Audit
      ├── Candidate Summaries
      ├── Candidate Comparison
      ├── Similarity Matrix
      └── Recruiter Assistant
             │
             ▼
      Reports & Exports
```

---

<p align="center">

### 🤖 AI-Powered Candidate Ranking System

**Understand Candidates. Compare Evidence. Support Better Recruitment Decisions.**

</p>

<p align="center">

Built independently with Python, Flask, NLP, semantic embeddings, and modern web technologies.

</p>
