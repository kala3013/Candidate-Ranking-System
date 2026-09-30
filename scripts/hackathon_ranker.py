#!/usr/bin/env python3
"""
Hackathon Ranker for INDIA.RUNS Data & AI Challenge
Produces a top-100 CSV submission in the required format.

Constraints: CPU only, ≤5 min runtime, ≤16GB RAM, no network
Strategy: Hybrid scoring with behavioral signals + semantic matching
"""

import os
import sys
import json
import gzip
import time
import argparse
import logging
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np
import pandas as pd

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# AI core skill keywords (from the JD: embeddings, retrieval, ranking, LLMs, search)
AI_CORE_SKILLS = {
    'machine learning', 'deep learning', 'nlp', 'natural language processing',
    'embedding', 'embeddings', 'sentence-transformers', 'sentence transformer',
    'retrieval', 'information retrieval', 'vector search', 'hybrid search',
    'ranking', 'learning to rank', 'ltr', 'reranking', 're-ranking',
    'llm', 'llms', 'large language model', 'gpt', 'bert', 'transformer',
    'transformers', 'fine-tuning', 'finetuning', 'loRA', 'qlora', 'peft',
    'rag', 'retrieval augmented generation', 'langchain',
    'faiss', 'pinecone', 'weaviate', 'qdrant', 'milvus', 'opensearch',
    'elasticsearch', 'vector database', 'vector db',
    'prompt engineering', 'evaluation', 'ndcg', 'mrr', 'map',
    'recommendation system', 'recommender system', 'search',
    'xgboost', 'lightgbm', 'gradient boosting',
    'mlops', 'model deployment', 'ml pipeline',
    'pytorch', 'tensorflow', 'scikit-learn', 'sklearn',
    'hugging face', 'transformers library',
    'mlflow', 'kubeflow',
}

# Disqualifying signals from the JD
CONSULTING_FIRMS = {'tcs', 'infosys', 'wipro', 'accenture', 'cognizant', 'capgemini', 'hcl', 'tech mahindra', 'mindtree', 'l&t infotech', 'lti', 'mphasis', 'hexaware'}
PURE_RESEARCH_ROLES = {'research scientist', 'research intern', 'research assistant', 'postdoc', 'phd candidate'}
CV_SPEECH_ROLES = {'computer vision', 'speech recognition', 'robotics', 'autonomous vehicle', 'self-driving'}
FRAMEWORK_KEYWORDS = {'langchain tutorial', 'how i used', 'building with', 'demo app'}


def load_candidates(filepath):
    """Load candidates from JSONL or JSONL.GZ file."""
    logger.info(f"Loading candidates from {filepath}")
    start = time.time()
    
    candidates = []
    if filepath.endswith('.gz'):
        with gzip.open(filepath, 'rt', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line:
                    candidates.append(json.loads(line))
    else:
        with open(filepath, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line:
                    candidates.append(json.loads(line))
    
    logger.info(f"Loaded {len(candidates)} candidates in {time.time()-start:.1f}s")
    return candidates


def compute_candidate_score(candidate, jd_text, embedding_model=None):
    """
    Compute a comprehensive score for a candidate against the JD.
    Implements the JD's own reasoning about what matters.
    """
    profile = candidate.get('profile', {})
    signals = candidate.get('redrob_signals', {})
    skills_list = candidate.get('skills', [])
    career = candidate.get('career_history', [])
    certs = candidate.get('certifications', [])
    edu = candidate.get('education', [])
    
    score_components = {}
    
    # === 1. EXPERIENCE & TITLE MATCH (20%) ===
    exp_years = profile.get('years_of_experience', 0)
    current_title = (profile.get('current_title', '') or '').lower()
    headline = (profile.get('headline', '') or '').lower()
    current_company = (profile.get('current_company', '') or '').lower()
    
    # Check for disqualifying factors (negative signals)
    consulting_only = all(
        any(f in (r.get('company', '') or '').lower() for f in CONSULTING_FIRMS)
        for r in career
    )
    has_product_experience = any(
        r.get('company_size', '') not in ['10001+'] or
        r.get('industry', '') not in ['IT Services']
        for r in career
        if not any(f in (r.get('company', '') or '').lower() for f in CONSULTING_FIRMS)
    )
    
    # Check for CV/speech only roles
    is_cv_speech = any(kw in headline for kw in ['computer vision', 'speech', 'robotics'])
    has_nlp_ir = any(kw in headline for kw in ['nlp', 'natural language', 'retrieval', 'search', 'recommend', 'ranking', 'llm', 'ai', 'machine learning'])
    
    experience_score = 0
    if 5 <= exp_years <= 12:
        experience_score = 1.0
    elif 4 <= exp_years < 5:
        experience_score = 0.8
    elif 12 < exp_years <= 15:
        experience_score = 0.7
    elif exp_years >= 3:
        experience_score = 0.5
    else:
        experience_score = 0.2
    
    # Title relevance
    title_keywords = ['engineer', 'scientist', 'developer', 'architect', 'researcher', 'ml', 'ai', 'machine learning', 'data']
    title_match = any(kw in current_title for kw in title_keywords)
    title_score = 0.8 if title_match else 0.3
    
    # Company quality signal
    company_is_product = not consulting_only or has_product_experience
    company_score = 1.0 if company_is_product else 0.4
    
    experience_component = (experience_score * 0.5 + title_score * 0.3 + company_score * 0.2)
    score_components['experience'] = experience_component * 0.20
    
    # === 2. SKILL MATCH (30%) ===
    skill_names = set()
    for s in skills_list:
        name = s.get('name', '').lower().strip()
        proficiency = s.get('proficiency', '').lower()
        duration = s.get('duration_months', 0)
        endorsements = s.get('endorsements', 0)
        skill_names.add(name)
    
    # Count AI core skills
    ai_skills_found = set()
    for skill in skill_names:
        skill_lower = skill.lower()
        for core_skill in AI_CORE_SKILLS:
            if core_skill in skill_lower or skill_lower == core_skill:
                ai_skills_found.add(core_skill)
    
    ai_skill_count = len(ai_skills_found)
    
    # Also check profile summary for AI skills
    summary = (profile.get('summary', '') or '').lower()
    for core_skill in AI_CORE_SKILLS:
        if core_skill in summary:
            ai_skills_found.add(core_skill)
    ai_skill_count = len(ai_skills_found)
    
    # Check career descriptions for AI/ML work
    career_ai_signals = 0
    for r in career:
        desc = (r.get('description', '') or '').lower()
        for kw in ['machine learning', 'deep learning', 'nlp', 'ranking', 'recommendation',
                    'embedding', 'retrieval', 'llm', 'search', 'ai model', 'ml model',
                    'tensorflow', 'pytorch', 'training', 'inference', 'vector']:
            if kw in desc:
                career_ai_signals += 1
                break
    
    # Dedicated ML/DS roles
    ml_role_count = 0
    for r in career:
        title = (r.get('title', '') or '').lower()
        if any(kw in title for kw in ['data scientist', 'ml engineer', 'machine learning',
                                        'ai engineer', 'research scientist', 'nlp',
                                        'applied scientist', 'recommendation', 'search']):
            ml_role_count += 1
    
    # Skill depth (proficiency check)
    advanced_ai_skills = sum(1 for s in skills_list if 
                            s.get('name', '').lower() in [k.replace(' ', '') for k in AI_CORE_SKILLS] or
                            any(k in s.get('name', '').lower() for k in ['embedding', 'retrieval', 'ranking', 'nlp', 'llm', 'transformer', 'faiss', 'ml'])
                            and s.get('proficiency', '') in ('advanced', 'expert'))
    
    skill_score = min(ai_skill_count * 0.06 + career_ai_signals * 0.04 + ml_role_count * 0.06 + advanced_ai_skills * 0.04, 1.0)
    score_components['skills'] = skill_score * 0.30
    
    # === 3. BEHAVIORAL SIGNALS (25%) ===
    recruiter_response_rate = signals.get('recruiter_response_rate', 0)
    last_active = signals.get('last_active_date', '')
    open_to_work = signals.get('open_to_work_flag', False)
    saved_by_recruiters = signals.get('saved_by_recruiters_30d', 0)
    profile_views = signals.get('profile_views_received_30d', 0)
    github_score = signals.get('github_activity_score', -1)
    profile_completeness = signals.get('profile_completeness_score', 0)
    notice_period = signals.get('notice_period_days', 90)
    avg_response_time = signals.get('avg_response_time_hours', 100)
    interview_completion = signals.get('interview_completion_rate', 0.5)
    willing_relocate = signals.get('willing_to_relocate', False)
    preferred_work_mode = signals.get('preferred_work_mode', '')
    
    # Responsiveness (high response rate + fast response)
    responsiveness = recruiter_response_rate
    if avg_response_time < 48:
        responsiveness += 0.15
    elif avg_response_time < 120:
        responsiveness += 0.05
    
    # Activity signals
    activity = 0
    if open_to_work:
        activity += 0.15
    if profile_views > 50:
        activity += 0.10
    elif profile_views > 20:
        activity += 0.05
    if saved_by_recruiters > 5:
        activity += 0.15
    elif saved_by_recruiters > 2:
        activity += 0.08
    if github_score > 20:
        activity += 0.10
    elif github_score > 0:
        activity += 0.03
    
    # Profile quality
    quality = profile_completeness / 100.0 * 0.10
    if interview_completion > 0.7:
        quality += 0.05
    
    # Availability
    availability = 0
    if notice_period <= 30:
        availability += 0.10
    elif notice_period <= 60:
        availability += 0.05
    if willing_relocate:
        availability += 0.05
    if preferred_work_mode in ('hybrid', 'flexible'):
        availability += 0.03
    
    behavioral_score = min(responsiveness + activity + quality + availability, 1.0)
    score_components['behavioral'] = behavioral_score * 0.25
    
    # === 4. PROJECT & CAREER DEPTH (15%) ===
    # Number of projects/achievements described
    total_achievements = 0
    description_depth = 0
    for r in career:
        desc = r.get('description', '') or ''
        total_achievements += 1
        description_depth += len(desc.split())
    
    # Impact indicators in descriptions
    impact_words = ['reduced', 'increased', 'improved', 'optimized', 'built', 'designed',
                    'led', 'shipped', 'deployed', 'launched', 'scaled', 'architected']
    impact_count = sum(1 for r in career for w in impact_words if w in (r.get('description', '') or '').lower())
    
    # Career progression signal
    career_progression = 0
    for i in range(1, len(career)):
        prev_title = career[i-1].get('title', '') or ''
        curr_title = career[i].get('title', '') or ''
        # Check if there's progression
        if len(curr_title) > len(prev_title):
            career_progression += 0.05
    
    project_score = min(
        total_achievements * 0.05 + 
        impact_count * 0.08 + 
        min(description_depth / 500, 1.0) * 0.1 +
        career_progression * 0.05,
        1.0
    )
    score_components['project'] = project_score * 0.15
    
    # === 5. EDUCATION (5%) ===
    edu_tiers = {'tier_1': 1.0, 'tier_2': 0.8, 'tier_3': 0.6, 'tier_4': 0.4, 'unknown': 0.3}
    max_tier_score = 0
    has_relevant_field = False
    relevant_fields = {'computer science', 'data science', 'artificial intelligence', 'machine learning',
                       'statistics', 'mathematics', 'information technology', 'computer engineering'}
    
    for e in edu:
        tier = e.get('tier', 'unknown')
        field = (e.get('field_of_study', '') or '').lower()
        max_tier_score = max(max_tier_score, edu_tiers.get(tier, 0.3))
        if any(f in field for f in relevant_fields):
            has_relevant_field = True
    
    edu_score = max_tier_score * (1.2 if has_relevant_field else 0.8)
    edu_score = min(edu_score, 1.0)
    score_components['education'] = edu_score * 0.05
    
    # === 6. CERTIFICATIONS (5%) ===
    cert_score = 0
    if certs:
        cert_names = [c.get('name', '') for c in certs]
        for cn in cert_names:
            cn_lower = cn.lower()
            if any(kw in cn_lower for kw in ['machine learning', 'data engineer', 'cloud', 'aws', 'gcp', 'tensorflow', 'scrum']):
                cert_score += 0.2
        cert_score = min(cert_score, 1.0)
    score_components['certifications'] = cert_score * 0.05
    
    # === FINAL COMPOSITE ===
    final_score = sum(score_components.values())
    
    # Apply disqualifying penalties (no multipliers - keep scores 0-1)
    if consulting_only and not has_product_experience:
        final_score *= 0.3  # Heavy penalty for consulting-only career
    
    if is_cv_speech and not has_nlp_ir:
        final_score *= 0.5  # CV/Speech-only penalty
    
    # No additive multipliers - all scoring is in the weighted components above
    return {
        'final_score': round(final_score, 4),
        'components': score_components,
        'ai_skills': sorted(ai_skills_found),
        'ai_skill_count': ai_skill_count,
        'ml_role_count': ml_role_count,
        'consulting_only': consulting_only,
        'responsive': recruiter_response_rate > 0.5
    }


def generate_reasoning(candidate, result, rank):
    """Generate a specific, honest 1-2 sentence reasoning for this candidate."""
    profile = candidate.get('profile', {})
    signals = candidate.get('redrob_signals', {})
    skills_list = candidate.get('skills', [])
    career = candidate.get('career_history', [])
    
    name = profile.get('anonymized_name', 'Candidate')
    current_title = profile.get('current_title', 'Professional')
    exp = profile.get('years_of_experience', 0)
    ai_count = result['ai_skill_count']
    ml_roles = result['ml_role_count']
    response_rate = signals.get('recruiter_response_rate', 0)
    
    # Build specific reasoning
    parts = []
    
    # Title and experience
    parts.append(f"{current_title} with {exp:.1f}yrs")
    
    # AI skills
    if ai_count > 0:
        parts.append(f"{ai_count} AI/core skills")
    
    # ML role history
    if ml_roles > 0:
        parts.append(f"{ml_roles} applied ML role(s)")
    
    # Behavioral signal
    if response_rate > 0.7:
        parts.append(f"high engagement ({response_rate:.0%} response rate)")
    elif response_rate < 0.2:
        parts.append(f"low engagement ({response_rate:.0%} response)")
    
    # Honest concerns
    concerns = []
    if exp < 4:
        concerns.append(f"below target range ({exp:.0f}yrs)")
    if result['consulting_only']:
        concerns.append("consulting-only background")
    if signals.get('notice_period_days', 0) > 60:
        concerns.append(f"notice period ({signals['notice_period_days']}d)")
    
    reasoning = "; ".join(parts)
    if concerns:
        reasoning += f" | Concerns: {', '.join(concerns)}"
    
    return reasoning[:200]  # Keep it short


def rank_candidates(jd_text, candidate_file, output_file, sample_size=None):
    """Main ranking function."""
    logger.info("="*60)
    logger.info("Starting Candidate Ranking Pipeline")
    logger.info("="*60)
    
    start = time.time()
    
    # Load candidates
    candidates = load_candidates(candidate_file)
    if sample_size:
        candidates = candidates[:sample_size]
        logger.info(f"Using sample of {sample_size} candidates")
    
    total = len(candidates)
    logger.info(f"Ranking {total} candidates against JD...")
    
    # Score each candidate
    results = []
    for i, candidate in enumerate(candidates):
        result = compute_candidate_score(candidate, jd_text)
        results.append({
            'candidate_id': candidate['candidate_id'],
            'candidate': candidate,
            'score': result['final_score'],
            'result': result
        })
        
        if (i+1) % 10000 == 0:
            logger.info(f"  Processed {i+1}/{total} candidates ({time.time()-start:.1f}s)")
    
    # Sort by score descending
    results.sort(key=lambda x: (-x['score'], x['candidate_id']))
    
    # Get top 100
    top_100 = results[:100]
    
    # Generate CSV
    rows = []
    for rank, item in enumerate(top_100, 1):
        reasoning = generate_reasoning(item['candidate'], item['result'], rank)
        rows.append({
            'candidate_id': item['candidate_id'],
            'rank': rank,
            'score': item['score'],
            'reasoning': reasoning
        })
    
    df = pd.DataFrame(rows)
    df.to_csv(output_file, index=False)
    
    elapsed = time.time() - start
    logger.info(f"\n✅ Ranking complete in {elapsed:.1f}s")
    logger.info(f"   Output: {output_file}")
    logger.info(f"   Top score: {top_100[0]['score']:.4f}")
    logger.info(f"   Bottom score: {top_100[-1]['score']:.4f}")
    
    # Print top 10
    print("\n" + "="*80)
    print("🏆 TOP 10 CANDIDATES")
    print("="*80)
    for i, item in enumerate(top_100[:10], 1):
        p = item['candidate']['profile']
        print(f"  #{i:2d} | {p.get('anonymized_name','?'):25s} | Score: {item['score']:.4f} | {p.get('current_title','?'):25s} | {p.get('years_of_experience',0):.1f}yrs")
    
    return top_100


def main():
    parser = argparse.ArgumentParser(description='INDIA.RUNS Hackathon Candidate Ranker')
    parser.add_argument('--candidates', type=str, default='data/hackathon/*/India_runs_data_and_ai_challenge/candidates.jsonl',
                       help='Path to candidates.jsonl or .gz file')
    parser.add_argument('--jd', type=str, default='data/hackathon/*/India_runs_data_and_ai_challenge/job_description.docx',
                       help='Path to job description file')
    parser.add_argument('--output', type=str, default='data/outputs/submission.csv',
                       help='Output CSV path')
    parser.add_argument('--sample', type=int, default=0,
                       help='Use only N candidates for testing')
    args = parser.parse_args()
    
    # Find the actual files (handle nested path)
    import glob
    candidate_files = glob.glob(args.candidates) or glob.glob('data/hackathon/**/*.jsonl', recursive=True) or glob.glob('data/hackathon/**/*.jsonl.gz', recursive=True)
    jd_files = glob.glob(args.jd) or glob.glob('data/hackathon/**/*.docx', recursive=True) or glob.glob('data/hackathon/**/*.txt', recursive=True)
    
    if not candidate_files:
        logger.error("candidates.jsonl not found! Check path.")
        # Try to find it
        for root, dirs, files in os.walk('data'):
            for f in files:
                if 'candidates' in f and (f.endswith('.jsonl') or f.endswith('.gz')):
                    candidate_files.append(os.path.join(root, f))
        logger.info(f"Found candidates: {candidate_files}")
    
    candidate_file = candidate_files[0] if candidate_files else None
    if not candidate_file or not os.path.exists(candidate_file):
        logger.error(f"Candidate file not found at any expected location")
        return
    
    jd_file = jd_files[0] if jd_files else 'data/jobs/data_scientist_jd.txt'
    
    # Read JD (standalone - no model dependencies needed)
    def read_jd_text(path):
        ext = os.path.splitext(path)[1].lower()
        if ext == '.docx':
            from docx import Document
            doc = Document(path)
            return '\n'.join(p.text for p in doc.paragraphs)
        else:
            with open(path, 'r', encoding='utf-8', errors='replace') as f:
                return f.read()
    jd_text = read_jd_text(jd_file)
    logger.info(f"Loaded JD from {os.path.basename(str(jd_file))}")
    
    # Create output dir
    os.makedirs(os.path.dirname(args.output), exist_ok=True)
    
    # Run ranking
    rank_candidates(
        jd_text=jd_text,
        candidate_file=candidate_file,
        output_file=args.output,
        sample_size=args.sample if args.sample > 0 else None
    )


if __name__ == '__main__':
    main()