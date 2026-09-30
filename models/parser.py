"""Document Parser - extracts structured info from resumes and job descriptions.
Enhanced with behavioral signals, leadership indicators, and impact scoring.
"""

import re
import os
import logging

logger = logging.getLogger(__name__)

SKILLS_DATABASE = {
    'languages': ['python', 'java', 'javascript', 'typescript', 'c++', 'c#', 'ruby', 'go', 'rust', 'swift', 'kotlin', 'php', 'scala', 'r', 'matlab', 'sql', 'bash', 'jax'],
    'frontend': ['react', 'angular', 'vue', 'next.js', 'nuxt', 'html', 'css', 'sass', 'bootstrap', 'tailwind', 'jquery', 'd3.js', 'redux', 'webpack'],
    'backend': ['node.js', 'express', 'django', 'flask', 'fastapi', 'spring', 'spring boot', 'asp.net', 'laravel', 'rails', 'gin', 'echo'],
    'databases': ['mysql', 'postgresql', 'mongodb', 'redis', 'elasticsearch', 'cassandra', 'dynamodb', 'oracle', 'sql server', 'mariadb', 'neo4j', 'sqlite'],
    'cloud': ['aws', 'azure', 'gcp', 'docker', 'kubernetes', 'terraform', 'ansible', 'jenkins', 'gitlab ci', 'github actions', 'circleci'],
    'data_science': ['machine learning', 'deep learning', 'nlp', 'computer vision', 'data science', 'data analysis', 'tensorflow', 'pytorch', 'scikit-learn', 'pandas', 'numpy', 'spark', 'hadoop', 'kafka', 'airflow', 'tableau', 'power bi'],
    'mobile': ['flutter', 'react native', 'android', 'ios', 'xamarin', 'ionic'],
    'devops': ['devops', 'ci/cd', 'git', 'linux', 'unix', 'prometheus', 'grafana', 'datadog', 'splunk', 'elk stack'],
    'ai': ['artificial intelligence', 'generative ai', 'llm', 'gpt', 'bert', 'transformers', 'rag', 'langchain', 'openai', 'claude'],
    'misc': ['agile', 'scrum', 'kanban', 'jira', 'confluence', 'figma', 'sketch', 'photoshop', 'excel', 'etl', 'microservices', 'rest api', 'graphql', 'serverless']
}

SOFT_SKILLS = [
    'communication', 'leadership', 'teamwork', 'problem solving', 'critical thinking',
    'creativity', 'adaptability', 'time management', 'attention to detail', 'collaboration',
    'mentoring', 'coaching', 'negotiation', 'presentation', 'public speaking',
    'interpersonal', 'emotional intelligence', 'conflict resolution', 'decision making',
    'strategic thinking', 'innovation', 'proactive', 'results-oriented'
]

CERT_KEYWORDS = [
    'certified', 'certification', 'certificate', 'aws certified', 'google certified',
    'microsoft certified', 'pmp', 'cissp', 'ckad', 'comptia', 'oracle certified',
    'tensorflow developer', 'kubernetes administrator', 'professional data engineer'
]

EXPERIENCE_REGEX = re.compile(r'(\d+)\+?\s*(?:years?|yrs?)\s*(?:of\s+)?(?:experience|exp)', re.IGNORECASE)

# Patterns for behavioral signals
LEADERSHIP_INDICATORS = [
    r'lead\s+(?:a\s+)?team', r'led\s+(?:a\s+)?team', r'manag(?:e|ed|ing)\s+(?:a\s+)?team',
    r'mentor(?:ed|ing)?', r'coach(?:ed|ing)?', r'head\s+of', r'director\s+of',
    r'team\s+lead', r'technical\s+lead', r'architect(?:ed|ing|ure)?',
    r'oversaw', r'responsible\s+for\s+(?:a\s+)?team'
]

IMPACT_INDICATORS = [
    r'reduc(?:ed|ing)\s+(?:by\s+)?\d+%', r'increas(?:ed|ing)\s+(?:by\s+)?\d+%',
    r'improv(?:ed|ing)\s+(?:by\s+)?\d+%', r'\d+%\s+(?:reduction|increase|improvement)',
    r'serv(?:ing|ed)\s+\d+[kMbB+]\s*', r'handl(?:ing|ed)\s+\d+[kMbB+]\s*',
    r'process(?:ed|ing)\s+\d+[kMbB+]\s*', r'\d+[kMbB+]\s+users',
    r'\d+[kMbB+]\s+customers', r'\d+[kMbB+]\s+requests',
    r'cost\s+(?:saving|reduction)', r'\d+x\s+(?:faster|improvement)'
]

PUBLICATION_INDICATORS = [
    r'publish(?:ed|ing)?', r'research\s+paper', r'conference',
    r'neurips', r'icml', r'iclr', r'acl', r'cvpr', r'kdd', r'www'
]

PRESENTATION_INDICATORS = [
    r'present(?:ed|ation|ing)?', r'speaking', r'talk', r'keynote',
    r'conference\s+talk', r'webinar', r'workshop'
]


def extract_skills(text):
    """Extract technical skills from text using keyword matching."""
    text_lower = text.lower()
    found_skills = set()
    for category, skills in SKILLS_DATABASE.items():
        for skill in skills:
            if skill in text_lower:
                found_skills.add(skill)
    return sorted(found_skills)


def extract_soft_skills(text):
    """Extract soft skills from text."""
    text_lower = text.lower()
    found = set()
    for skill in SOFT_SKILLS:
        if skill in text_lower:
            found.add(skill)
    return sorted(found)


def extract_experience(text):
    """Extract years of experience from text."""
    matches = EXPERIENCE_REGEX.findall(text)
    if matches:
        years = [int(m) for m in matches]
        return max(years)
    return 0


def extract_education(text):
    """Extract education information."""
    text_lower = text.lower()
    education = []
    levels = [
        (['ph.d', 'phd', 'doctorate'], 'PhD'),
        (['master', 'm.tech', 'm.sc', 'mba', 'mca', 'm.e.'], "Master's"),
        (['bachelor', 'b.tech', 'b.e.', 'b.sc', 'bca', 'b.a.'], "Bachelor's"),
        (['diploma'], 'Diploma'),
        (['high school', '12th', 'class xii'], 'High School'),
    ]
    for keywords, level in levels:
        for kw in keywords:
            if kw in text_lower:
                education.append(level)
                break
    return list(set(education)) if education else ['Not Specified']


def extract_certifications(text):
    """Extract certification mentions."""
    text_lower = text.lower()
    certs = set()
    for kw in CERT_KEYWORDS:
        if kw in text_lower:
            certs.add(kw)
    return sorted(certs)


def extract_behavioral_signals(text):
    """Extract behavioral signals from resume text.
    
    Analyzes the text for leadership, impact, publication, and presentation signals.
    Returns a dict with counts and evidence.
    """
    signals = {
        'leadership_count': 0,
        'leadership_evidence': [],
        'impact_count': 0,
        'impact_evidence': [],
        'publication_count': 0,
        'publication_evidence': [],
        'presentation_count': 0,
        'presentation_evidence': []
    }
    
    lines = text.split('\n')
    for line in lines:
        line_lower = line.lower().strip()
        if not line_lower or line_lower.startswith(('skills', 'education', 'certifications', 'projects')):
            continue
            
        for pattern in LEADERSHIP_INDICATORS:
            m = re.search(pattern, line_lower)
            if m:
                signals['leadership_count'] += 1
                signals['leadership_evidence'].append(line.strip()[:100])
                break
                
        for pattern in IMPACT_INDICATORS:
            m = re.search(pattern, line_lower)
            if m:
                signals['impact_count'] += 1
                signals['impact_evidence'].append(line.strip()[:100])
                break
                
        for pattern in PUBLICATION_INDICATORS:
            m = re.search(pattern, line_lower)
            if m:
                signals['publication_count'] += 1
                signals['publication_evidence'].append(line.strip()[:100])
                break
                
        for pattern in PRESENTATION_INDICATORS:
            m = re.search(pattern, line_lower)
            if m:
                signals['presentation_count'] += 1
                signals['presentation_evidence'].append(line.strip()[:100])
                break
    
    return signals


def extract_domain(text):
    """Extract industry domain from text."""
    domains = ['healthcare', 'finance', 'banking', 'e-commerce', 'retail', 'education', 'tech', 'saas',
               'manufacturing', 'telecom', 'media', 'gaming', 'logistics', 'real estate', 'energy']
    domain = next((d for d in domains if d in text.lower()), 'General')
    return domain


def parse_job_description(text):
    """Parse a job description text into structured JSON."""
    skills = extract_skills(text)
    soft_skills = extract_soft_skills(text)
    experience = extract_experience(text)

    # Extract responsibilities (lines after key phrases)
    resp_section = re.search(
        r'(?:responsibilities|what you.?ll do|key duties|role)\s*[:\-]?\s*(.*?)(?:\n\n|\Z)',
        text, re.DOTALL | re.IGNORECASE
    )
    responsibilities = resp_section.group(1).strip() if resp_section else ''

    # Extract domain
    domain = extract_domain(text)
    
    # Extract behavioral signals from JD
    behavioral_signals = extract_behavioral_signals(text)

    return {
        'required_skills': skills,
        'preferred_skills': [],
        'soft_skills': soft_skills,
        'experience_required': experience,
        'education_required': extract_education(text),
        'responsibilities': responsibilities,
        'domain': domain,
        'certifications_preferred': extract_certifications(text),
        'behavioral_signals': behavioral_signals,
        'full_text': text
    }


def parse_candidate_profile(text, candidate_id='C000', candidate_name='Unknown'):
    """Parse a candidate resume text into structured JSON profile.
    Enhanced with behavioral signals, leadership, impact, and project depth analysis.
    """
    skills = extract_skills(text)
    soft_skills = extract_soft_skills(text)
    experience_years = extract_experience(text)
    education = extract_education(text)
    certs = extract_certifications(text)
    behavioral_signals = extract_behavioral_signals(text)

    # Extract projects section
    proj_section = re.search(
        r'(?:projects|experience|work\s*history)\s*[:\-]?\s*(.*?)(?:\n\n|\Z)',
        text, re.DOTALL | re.IGNORECASE
    )
    projects_text = proj_section.group(1).strip()[:800] if proj_section else ''
    
    # Count project mentions (bullet points in experience/projects)
    project_count = len(re.findall(r'^\s*[\-\*]\s+.+', text, re.MULTILINE))
    
    # Count specific quantifiable achievements
    quant_achievements = len(re.findall(r'\d+%|\d+x|\d+[kKmMbB]', text))
    
    # Extract company names and roles for tenure analysis
    company_matches = re.findall(
        r'(?:at|@)\s+([A-Z][A-Za-z0-9\s&]+?)(?:\s*\n|\s*\(|\s*\-|\s*\d)', text
    )
    companies = [c.strip() for c in company_matches if len(c.strip()) > 2]
    
    # Compute an overall profile completeness score
    completeness_score = 0
    if skills: completeness_score += 0.20
    if soft_skills: completeness_score += 0.10
    if experience_years > 0: completeness_score += 0.20
    if education and education != ['Not Specified']: completeness_score += 0.15
    if certs: completeness_score += 0.05
    if projects_text: completeness_score += 0.15
    if behavioral_signals['impact_count'] > 0: completeness_score += 0.10
    if behavioral_signals['leadership_count'] > 0: completeness_score += 0.05

    return {
        'candidate_id': candidate_id,
        'candidate_name': candidate_name,
        'technical_skills': skills,
        'soft_skills': soft_skills,
        'education': education,
        'certifications': certs,
        'experience_years': experience_years,
        'projects_summary': projects_text,
        'project_count': project_count,
        'quantifiable_achievements': quant_achievements,
        'companies': companies,
        'behavioral_signals': behavioral_signals,
        'completeness_score': round(completeness_score, 2),
        'full_text': text
    }


def read_file_text(file_path):
    """Read text from PDF, DOCX, or TXT file."""
    ext = os.path.splitext(file_path)[1].lower()
    if ext == '.pdf':
        try:
            import pdfplumber
            with pdfplumber.open(file_path) as pdf:
                return '\n'.join(page.extract_text() or '' for page in pdf.pages)
        except ImportError:
            try:
                from PyPDF2 import PdfReader
                reader = PdfReader(file_path)
                return '\n'.join(page.extract_text() or '' for page in reader.pages)
            except:
                return ''
    elif ext == '.docx':
        try:
            from docx import Document
            doc = Document(file_path)
            return '\n'.join(p.text for p in doc.paragraphs)
        except:
            return ''
    else:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except:
            with open(file_path, 'r', encoding='latin-1') as f:
                return f.read()