"""
AI-Powered Intelligent Candidate Ranking & Recruitment Assistant
INDIA.RUNS Data & AI Challenge 2026
Complete Backend API with all 11 modules
"""

import os
import json
import logging
import tempfile
import hashlib
from datetime import datetime
from collections import Counter

from flask import Flask, request, jsonify, send_file, render_template
from flask_cors import CORS

from models.ranking_engine import RankingEngine
from models.scorer import CandidateScorer, DEFAULT_WEIGHTS, WEIGHT_KEYS
from models.parser import read_file_text, parse_job_description, parse_candidate_profile
from models.skill_gap_analyzer import SkillGapAnalyzer, CandidatePotentialEngine
from models.interview_generator import InterviewQuestionGenerator
from models.bias_evaluator import BiasFreeEvaluator
from models.copilot import RecruiterCopilot
from models.new_features.ats_scorer import ATSResumeScorer, ATSOptimizationEngine
from models.new_features.salary_predictor import SalaryPredictor
from models.new_features.career_predictor import CareerPathPredictor
from models.new_features.email_generator import EmailDraftGenerator
from models.new_features.diversity_analyzer import DiversityAnalyzer
from models.new_features.team_fit_analyzer import TeamFitAnalyzer
from models.new_features.analysis_history import AnalysisHistoryManager
from models.new_features.multi_job_analyzer import MultiJobBatchAnalyzer
from models.new_features.executive_dashboard import ExecutiveDashboardGenerator, DemoModeController
from functools import wraps
from datetime import timedelta

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__,
    static_folder='frontend',
    static_url_path='',
    template_folder='frontend'
)
CORS(app)

# Configuration
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB max upload
UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'data', 'uploads')
OUTPUT_FOLDER = os.path.join(os.path.dirname(__file__), 'data', 'outputs')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# Initialize engines
ranking_engine = RankingEngine()
skill_gap_analyzer = SkillGapAnalyzer()
potential_engine = CandidatePotentialEngine()
interview_generator = InterviewQuestionGenerator()
bias_evaluator = BiasFreeEvaluator()
copilot = RecruiterCopilot()

# Initialize new feature engines
ats_scorer = ATSResumeScorer()
ats_optimizer = ATSOptimizationEngine()
salary_predictor = SalaryPredictor()
career_predictor = CareerPathPredictor()
email_generator = EmailDraftGenerator()
diversity_analyzer = DiversityAnalyzer()
team_fit_analyzer = TeamFitAnalyzer()
history_manager = AnalysisHistoryManager()
multi_job_analyzer = MultiJobBatchAnalyzer()
executive_dashboard = ExecutiveDashboardGenerator()
demo_controller = DemoModeController()

# Cache for current analysis results + caching layer
_current_results = None
_current_jd_profile = None
_analysis_cache = {}  # Simple cache: key -> (timestamp, results)
CACHE_DURATION_SECONDS = 1800  # Cache results for 30 minutes


@app.route('/')
def index():
    """Serve the main dashboard."""
    return app.send_static_file('index.html')


@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'model': ranking_engine.embedding_model.model_name if hasattr(ranking_engine.embedding_model, 'model_name') else 'all-MiniLM-L6-v2',
        'version': '2.0.0',
        'features': [
            'job_parsing', 'resume_parsing', 'semantic_matching',
            'hybrid_scoring', 'explainable_ai', 'skill_gap_analysis',
            'candidate_potential', 'interview_generator', 'bias_free',
            'candidate_summary', 'recruiter_copilot',
            'ats_resume_scoring', 'salary_prediction', 'career_path_prediction',
            'email_draft_generator', 'diversity_analytics', 'team_fit_analysis',
            'analysis_history', 'multi_job_batch_analysis'
        ],
        'new_features': [
            'ATS Resume Scoring & Optimization',
            'Salary Prediction Engine',
            'Career Path Predictor',
            'Email Draft Generator',
            'Diversity Analytics',
            'Team Fit Analysis',
            'Analysis History Dashboard',
            'Multi-Job Batch Analysis'
        ]
    })


@app.route('/api/analyze', methods=['POST'])
def analyze():
    """
    Main analysis endpoint with full feature set.
    Accepts job description text or file, and candidate resume files or text.
    Returns ranked candidates with scores, reasoning, skill gaps, potential, and bias-free metrics.
    """
    global _current_results, _current_jd_profile

    try:
        # Handle file uploads
        if request.files:
            result = _handle_file_upload(request)
        elif request.is_json:
            result = _handle_json_input(request.json)
        else:
            return jsonify({'error': 'Invalid request format'}), 400

        if isinstance(result, tuple):
            return result
            
        _current_results = result
        return jsonify(result)

    except Exception as e:
        logger.error(f"Analysis failed: {str(e)}", exc_info=True)
        return jsonify({'error': f'Analysis failed: {str(e)}'}), 500


def _extract_weights(raw):
    """Parse and normalise a custom scoring-weights payload.

    Accepts the raw value from either ``request.form['weights']`` or a JSON
    ``weights`` object. The UI sliders do not guarantee a 100% total, so the
    values are clamped to [0, 1] and rescaled to sum to 1.0 by
    ``CandidateScorer.resolve_weights``. Anything malformed returns None so the
    caller silently falls back to the documented defaults.

    Args:
        raw: str (JSON text) or dict, or None

    Returns:
        dict | None: normalised weights, or None when unusable
    """
    if raw is None or raw == '':
        return None

    payload = raw
    if isinstance(raw, str):
        try:
            payload = json.loads(raw)
        except (ValueError, TypeError):
            logger.warning("Ignoring unparseable 'weights' payload")
            return None

    if not isinstance(payload, dict):
        return None

    resolved = CandidateScorer.resolve_weights(payload)
    # resolve_weights() returns the defaults when the payload is unusable, so
    # compare against them to detect that case explicitly.
    if resolved == DEFAULT_WEIGHTS and payload != DEFAULT_WEIGHTS:
        logger.warning("Ignoring invalid 'weights' payload: %s", payload)
        return None

    return resolved


def _handle_file_upload(req):
    """Handle file upload based analysis."""
    job_text = ''
    candidate_texts = []
    candidate_info = []

    # Get job description
    if 'job_file' in req.files:
        jd_file = req.files['job_file']
        if jd_file.filename:
            ext = os.path.splitext(jd_file.filename)[1].lower()
            with tempfile.NamedTemporaryFile(suffix=ext, delete=False) as tmp:
                jd_file.save(tmp.name)
                job_text = read_file_text(tmp.name)
            os.unlink(tmp.name)
    elif 'job_description' in req.form:
        job_text = req.form['job_description']
    else:
        return jsonify({'error': 'No job description provided'}), 400

    # Get candidate resumes
    if 'resumes' in req.files:
        files = req.files.getlist('resumes')
        for f in files:
            if f.filename:
                ext = os.path.splitext(f.filename)[1].lower()
                if ext in ['.pdf', '.docx', '.txt']:
                    with tempfile.NamedTemporaryFile(suffix=ext, delete=False) as tmp:
                        f.save(tmp.name)
                        text = read_file_text(tmp.name)
                    os.unlink(tmp.name)
                    if text.strip():
                        candidate_texts.append(text)
                        name = os.path.splitext(f.filename)[0].replace('_', ' ').replace('-', ' ').title()
                        candidate_info.append({'id': f.filename, 'name': name})

    if not job_text.strip():
        return jsonify({'error': 'Empty job description'}), 400
    if not candidate_texts:
        return jsonify({'error': 'No valid candidate resumes provided'}), 400

    return _process_and_return_results(
        job_text, candidate_texts, candidate_info,
        weights=_extract_weights(req.form.get('weights'))
    )


def _handle_json_input(data):
    """Handle JSON-based analysis request."""
    job_text = data.get('job_text', data.get('job_description', ''))
    candidate_texts = data.get('candidate_texts', [])

    if not job_text:
        return jsonify({'error': 'No job description provided'}), 400
    if not candidate_texts:
        return jsonify({'error': 'No candidates provided'}), 400

    candidate_info = [
        {'id': c.get('id', f'C{i+1:03d}'), 'name': c.get('name', f'Candidate {i+1}')}
        for i, c in enumerate(candidate_texts)
    ]
    texts = [c.get('text', '') for c in candidate_texts]

    return _process_and_return_results(
        job_text, texts, candidate_info,
        weights=_extract_weights(data.get('weights'))
    )


def _process_and_return_results(job_text, candidate_texts, candidate_info, weights=None):
    """Process analysis and return comprehensive results with all features."""
    global _current_jd_profile

    # Parse job description
    jd_profile = parse_job_description(job_text)
    _current_jd_profile = jd_profile
    jd_profile['role'] = jd_profile.get('role', '') or 'Data Scientist'

    # Resolve custom scoring weights (falls back to DEFAULT_WEIGHTS when absent)
    weights = CandidateScorer.resolve_weights(weights)
    
    # Parse candidates and compute scores
    results = ranking_engine.rank_candidates(
        job_text, candidate_texts, candidate_info, weights=weights
    )
    
    # For each candidate, compute additional analytics
    enriched_results = []
    for r in results:
        candidate_profile = r['candidate_profile']
        
        # Skill Gap Analysis
        skill_gaps = skill_gap_analyzer.analyze_skill_gaps(
            jd_profile.get('required_skills', []),
            candidate_profile.get('technical_skills', []),
            jd_profile.get('preferred_skills', [])
        )
        
        # Candidate Potential
        potential = potential_engine.compute_potential(candidate_profile)
        
        # Generate Interview Questions
        interview = interview_generator.generate_questions(jd_profile, candidate_profile, skill_gaps)
        
        # Bias-Free Evaluation
        anon_text, bias_metrics = bias_evaluator.anonymize_text(candidate_profile.get('full_text', ''))
        bias_report = bias_evaluator.evaluate_anonymously(jd_profile, candidate_profile, anon_text)
        
        # Generate AI Summary
        candidate_summary = _generate_candidate_summary(candidate_profile, r)
        
        # Enrich result
        enriched = {
            'rank': r['rank'],
            'candidate_id': r['candidate_id'],
            'candidate_name': r['candidate_name'],
            'final_score': r['final_score'],
            'scores': r['scores'],
            'reason': r['reason'],
            'profile': _sanitize_profile(candidate_profile),
            'skill_gaps': skill_gaps,
            'potential': potential,
            'interview_questions': interview,
            'bias_free': bias_report,
            'candidate_summary': candidate_summary
        }
        enriched_results.append(enriched)

    # Export to CSV
    csv_path = ranking_engine.export_to_csv(results)
    
    # Generate summary statistics
    summary = _generate_analytics_summary(enriched_results, jd_profile)

    response_data = {
        'ranked_candidates': enriched_results,
        'summary': summary,
        'job_profile': {
            'role': jd_profile.get('role', ''),
            'required_skills': jd_profile.get('required_skills', []),
            'preferred_skills': jd_profile.get('preferred_skills', []),
            'experience_required': jd_profile.get('experience_required', 0),
            'education_required': jd_profile.get('education_required', []),
            'soft_skills': jd_profile.get('soft_skills', []),
            'domain': jd_profile.get('domain', 'General'),
            'certifications_preferred': jd_profile.get('certifications_preferred', [])
        },
        'csv_path': csv_path,
        'weights_used': weights,
        'processed_at': datetime.now().isoformat()
    }

    return response_data


def _sanitize_profile(profile):
    """Return safe profile data for API response."""
    return {
        'technical_skills': profile.get('technical_skills', []),
        'soft_skills': profile.get('soft_skills', []),
        'education': profile.get('education', []),
        'certifications': profile.get('certifications', []),
        'experience_years': profile.get('experience_years', 0),
        'projects_summary': (profile.get('projects_summary', '') or '')[:500],
        'project_count': profile.get('project_count', 0),
        'companies': profile.get('companies', []),
        'behavioral_signals': profile.get('behavioral_signals', {}),
        'completeness_score': profile.get('completeness_score', 0)
    }


def _generate_candidate_summary(profile, result):
    """Generate recruiter-ready AI summary for a candidate."""
    name = profile.get('candidate_name', 'Candidate')
    experience = profile.get('experience_years', 0)
    skills = profile.get('technical_skills', [])
    education = profile.get('education', [])
    certifications = profile.get('certifications', [])
    
    # Determine seniority
    if experience >= 7:
        seniority = "Senior"
    elif experience >= 4:
        seniority = "Mid-level"
    elif experience >= 2:
        seniority = "Junior"
    else:
        seniority = "Entry-level"
    
    # Key skills
    top_skills = skills[:5] if skills else ['technical skills']
    skills_text = ', '.join(top_skills)
    
    # Education
    edu_text = education[0] if education and education[0] != 'Not Specified' else ''
    
    # Certifications
    cert_text = f" with {len(certifications)} certifications" if certifications else ""
    
    # Behavioral highlights
    behav = profile.get('behavioral_signals', {})
    highlights = []
    if behav.get('leadership_count', 0) > 0:
        highlights.append("leadership experience")
    if behav.get('publication_count', 0) > 0:
        highlights.append(f"{behav['publication_count']} publications")
    if behav.get('impact_count', 0) > 0:
        highlights.append("quantifiable impact")
    
    highlights_text = f" Demonstrates {', '.join(highlights)}." if highlights else ""
    
    # Recommendation level
    score = result['final_score']
    if score >= 0.8:
        recommendation = "Highly recommended"
    elif score >= 0.6:
        recommendation = "Recommended"
    elif score >= 0.4:
        recommendation = "Consider for interview"
    else:
        recommendation = "Review for fit"
    
    summary = (
        f"{name} is a {seniority} professional with {experience} years of experience "
        f"in {skills_text}. {edu_text}{cert_text}."
        f"{highlights_text} "
        f"Match score: {score*100:.1f}%. {recommendation} for {seniority.lower()} data roles."
    )
    
    return summary


def _generate_analytics_summary(results, jd_profile):
    """Generate comprehensive analytics summary."""
    if not results:
        return {}
    
    total = len(results)
    scores = [c['final_score'] for c in results]
    top = results[0] if results else None
    
    # Score distribution
    excellent = sum(1 for s in scores if s >= 0.8)
    good = sum(1 for s in scores if 0.6 <= s < 0.8)
    moderate = sum(1 for s in scores if 0.4 <= s < 0.6)
    low = sum(1 for s in scores if s < 0.4)
    
    # Skill coverage across all candidates
    all_skills = []
    for c in results:
        all_skills.extend([s.lower() for s in c['profile'].get('technical_skills', [])])
    skill_counts = Counter(all_skills)
    top_skills_covered = skill_counts.most_common(10)
    
    # Experience distribution
    exp_years = [c['profile'].get('experience_years', 0) for c in results]
    
    # Skill coverage for JD skills
    jd_skills = [s.lower() for s in jd_profile.get('required_skills', [])]
    skill_coverage = {}
    for skill in jd_skills:
        count = sum(1 for c in results if skill in [s.lower() for s in c['profile'].get('technical_skills', [])])
        skill_coverage[skill] = {
            'candidates_with_skill': count,
            'coverage_pct': round(count / total * 100, 1)
        }
    
    return {
        'total_candidates': total,
        'top_score': round(top['final_score'] * 100, 1) if top else 0,
        'top_candidate_name': top['candidate_name'] if top else '',
        'average_score': round(sum(scores) / total * 100, 1),
        'median_score': round(sorted(scores)[total // 2] * 100, 1) if total > 0 else 0,
        'score_distribution': {
            'excellent_80_plus': excellent,
            'good_60_80': good,
            'moderate_40_60': moderate,
            'needs_development_below_40': low
        },
        'skill_coverage': skill_coverage,
        'top_skills': [{'skill': s, 'count': c} for s, c in top_skills_covered],
        'experience_distribution': {
            'min_exp': min(exp_years) if exp_years else 0,
            'max_exp': max(exp_years) if exp_years else 0,
            'avg_exp': round(sum(exp_years) / len(exp_years), 1) if exp_years else 0
        },
        'processed_at': datetime.now().isoformat()
    }


# ==================== ADDITIONAL API ENDPOINTS ====================

@app.route('/api/skill-gaps/<int:candidate_index>', methods=['GET'])
def get_skill_gaps(candidate_index):
    """Get skill gap analysis for a specific candidate."""
    global _current_results
    if not _current_results or not _current_results.get('ranked_candidates'):
        return jsonify({'error': 'No analysis results available'}), 404
    
    candidates = _current_results['ranked_candidates']
    if candidate_index < 0 or candidate_index >= len(candidates):
        return jsonify({'error': 'Invalid candidate index'}), 404
    
    return jsonify(candidates[candidate_index].get('skill_gaps', {}))


@app.route('/api/interview-questions/<int:candidate_index>', methods=['GET'])
def get_interview_questions(candidate_index):
    """Get interview questions for a specific candidate."""
    global _current_results
    if not _current_results or not _current_results.get('ranked_candidates'):
        return jsonify({'error': 'No analysis results available'}), 404
    
    candidates = _current_results['ranked_candidates']
    if candidate_index < 0 or candidate_index >= len(candidates):
        return jsonify({'error': 'Invalid candidate index'}), 404
    
    return jsonify(candidates[candidate_index].get('interview_questions', {}))


@app.route('/api/potential/<int:candidate_index>', methods=['GET'])
def get_potential(candidate_index):
    """Get candidate potential score."""
    global _current_results
    if not _current_results or not _current_results.get('ranked_candidates'):
        return jsonify({'error': 'No analysis results available'}), 404
    
    candidates = _current_results['ranked_candidates']
    if candidate_index < 0 or candidate_index >= len(candidates):
        return jsonify({'error': 'Invalid candidate index'}), 404
    
    return jsonify(candidates[candidate_index].get('potential', {}))


@app.route('/api/bias-report/<int:candidate_index>', methods=['GET'])
def get_bias_report(candidate_index):
    """Get bias-free evaluation report for a candidate."""
    global _current_results
    if not _current_results or not _current_results.get('ranked_candidates'):
        return jsonify({'error': 'No analysis results available'}), 404
    
    candidates = _current_results['ranked_candidates']
    if candidate_index < 0 or candidate_index >= len(candidates):
        return jsonify({'error': 'Invalid candidate index'}), 404
    
    return jsonify(candidates[candidate_index].get('bias_free', {}))


@app.route('/api/candidate-summary/<int:candidate_index>', methods=['GET'])
def get_candidate_summary(candidate_index):
    """Get AI-generated candidate summary."""
    global _current_results
    if not _current_results or not _current_results.get('ranked_candidates'):
        return jsonify({'error': 'No analysis results available'}), 404
    
    candidates = _current_results['ranked_candidates']
    if candidate_index < 0 or candidate_index >= len(candidates):
        return jsonify({'error': 'Invalid candidate index'}), 404
    
    return jsonify({
        'summary': candidates[candidate_index].get('candidate_summary', ''),
        'candidate_name': candidates[candidate_index]['candidate_name']
    })


@app.route('/api/copilot', methods=['POST'])
def copilot_query():
    """Recruiter Copilot - answer natural language queries about candidates."""
    global _current_results, _current_jd_profile
    
    if not request.is_json:
        return jsonify({'error': 'JSON body required'}), 400
    
    query = request.json.get('query', '').strip()
    if not query:
        return jsonify({'error': 'Query is required'}), 400
    
    if not _current_results or not _current_results.get('ranked_candidates'):
        return jsonify({'error': 'No analysis results available. Analyze candidates first.'}), 400
    
    ranked_results = _current_results['ranked_candidates']
    jd_profile = _current_jd_profile
    
    # Process the query. Guarded so a failure returns JSON, never an HTML 500
    # page (which the chat UI would render as a broken error bubble).
    try:
        response = copilot.process_query(query, ranked_results, jd_profile)
    except Exception as e:
        logger.error(f"Copilot query failed: {e}", exc_info=True)
        return jsonify({
            'error': f'Could not answer that query: {e}',
            'type': 'error',
            'answer': "🤔 Something went wrong answering that. Try rephrasing your question."
        }), 500
    
    return jsonify(response)


@app.route('/api/weights', methods=['GET'])
def get_default_weights():
    """Return the default scoring weights and their component labels."""
    labels = {
        'skill_match': 'Skill Match',
        'experience_match': 'Experience',
        'project_relevance': 'Projects',
        'semantic_similarity': 'Semantic Fit',
        'education': 'Education',
        'certifications': 'Certifications',
        'behavioral_score': 'Soft Skills',
    }
    return jsonify({
        'weights': DEFAULT_WEIGHTS,
        'keys': list(WEIGHT_KEYS),
        'labels': labels
    })


@app.route('/api/copilot/clear', methods=['POST'])
def clear_copilot():
    """Clear copilot conversation history."""
    copilot.clear_history()
    return jsonify({'status': 'cleared'})


@app.route('/api/analytics', methods=['GET'])
def get_analytics():
    """Get comprehensive recruitment analytics."""
    global _current_results, _current_jd_profile
    
    if not _current_results or not _current_results.get('ranked_candidates'):
        return jsonify({'error': 'No analysis results available'}), 404
    
    return jsonify({
        'summary': _current_results.get('summary', {}),
        'job_profile': _current_results.get('job_profile', {}),
        'total_candidates': len(_current_results['ranked_candidates']),
        'bias_free_enabled': True,
        'features_available': [
            'semantic_matching', 'hybrid_scoring', 'explainable_ai',
            'skill_gap_analysis', 'candidate_potential', 'interview_questions',
            'bias_free', 'candidate_summaries', 'recruiter_copilot'
        ]
    })


@app.route('/api/compare', methods=['POST'])
def compare_candidates():
    """Compare two candidates side-by-side."""
    global _current_results
    
    if not request.is_json:
        return jsonify({'error': 'JSON body required'}), 400
    
    idx1 = request.json.get('index1')
    idx2 = request.json.get('index2')
    
    if idx1 is None or idx2 is None:
        return jsonify({'error': 'Both index1 and index2 required'}), 400
    
    if not _current_results or not _current_results.get('ranked_candidates'):
        return jsonify({'error': 'No analysis results available'}), 400
    
    candidates = _current_results['ranked_candidates']
    if idx1 < 0 or idx1 >= len(candidates) or idx2 < 0 or idx2 >= len(candidates):
        return jsonify({'error': 'Invalid candidate index'}), 400
    
    c1, c2 = candidates[idx1], candidates[idx2]
    comparison = {
        'candidate_1': {
            'name': c1['candidate_name'],
            'rank': c1['rank'],
            'score': c1['final_score'],
            'scores': c1['scores'],
            'profile': c1['profile'],
            'summary': c1['candidate_summary']
        },
        'candidate_2': {
            'name': c2['candidate_name'],
            'rank': c2['rank'],
            'score': c2['final_score'],
            'scores': c2['scores'],
            'profile': c2['profile'],
            'summary': c2['candidate_summary']
        },
        'differences': {
            'score_diff': round((c1['final_score'] - c2['final_score']) * 100, 1),
            'skill_diff': round((c1['scores']['skill_match'] - c2['scores']['skill_match']) * 100, 1),
            'experience_diff': round((c1['scores']['experience_match'] - c2['scores']['experience_match']) * 100, 1),
            'semantic_diff': round((c1['scores']['semantic_similarity'] - c2['scores']['semantic_similarity']) * 100, 1)
        }
    }
    
    return jsonify(comparison)


@app.route('/api/export', methods=['GET'])
def export_results():
    """Export results in various formats."""
    format_type = request.args.get('format', 'json')
    
    global _current_results
    if not _current_results or not _current_results.get('ranked_candidates'):
        return jsonify({'error': 'No results available'}), 404
    
    if format_type == 'json':
        return jsonify({
            'exported_at': datetime.now().isoformat(),
            'total': len(_current_results['ranked_candidates']),
            'candidates': _current_results['ranked_candidates'],
            'summary': _current_results.get('summary', {})
        })
    elif format_type == 'csv':
        csv_path = _current_results.get('csv_path', '')
        if csv_path and os.path.exists(csv_path):
            return send_file(csv_path, as_attachment=True, mimetype='text/csv')
        return jsonify({'error': 'CSV not available'}), 404
    
    return jsonify({'error': 'Unsupported format'}), 400


@app.route('/api/download', methods=['GET'])
def download_results():
    """Download the latest ranked candidates CSV."""
    csv_path = os.path.join(OUTPUT_FOLDER, 'ranked_candidates.csv')
    if os.path.exists(csv_path):
        return send_file(csv_path, as_attachment=True, mimetype='text/csv')
    return jsonify({'error': 'No results available'}), 404


@app.route('/api/analyze-sample', methods=['POST'])
def analyze_sample():
    """Analyze using sample data for demo purposes."""
    try:
        data_dir = os.path.join(os.path.dirname(__file__), 'data')
        jobs_dir = os.path.join(data_dir, 'jobs')
        resumes_dir = os.path.join(data_dir, 'resumes')

        # Read sample job description
        jd_files = [f for f in os.listdir(jobs_dir) if f.lower().endswith(('.txt', '.pdf', '.docx'))]
        if not jd_files:
            return jsonify({'error': 'No sample job files found'}), 404

        jd_path = os.path.join(jobs_dir, jd_files[0])
        job_text = read_file_text(jd_path)

        # Read sample resumes
        resume_files = [f for f in os.listdir(resumes_dir) if f.lower().endswith(('.txt', '.pdf', '.docx'))]
        if not resume_files:
            return jsonify({'error': 'No sample resume files found'}), 404

        candidate_texts = []
        candidate_info = []
        for fname in sorted(resume_files):
            rpath = os.path.join(resumes_dir, fname)
            text = read_file_text(rpath)
            if text.strip():
                candidate_texts.append(text)
                name = os.path.splitext(fname)[0].replace('_', ' ').title()
                candidate_info.append({'id': fname, 'name': name})

        result = _process_and_return_results(
            job_text, candidate_texts, candidate_info,
            weights=_extract_weights(request.form.get('weights') if request.form else None)
        )
        global _current_results, _current_jd_profile
        _current_results = result
        
        return jsonify(result)

    except Exception as e:
        logger.error(f"Sample analysis failed: {str(e)}", exc_info=True)
        return jsonify({'error': f'Sample analysis failed: {str(e)}'}), 500


# ==================== NEW FEATURE API ENDPOINTS ====================

@app.route('/api/ats-score/<int:candidate_index>', methods=['GET'])
def get_ats_score(candidate_index):
    """Get ATS resume score and optimization tips for a candidate."""
    global _current_results
    if not _current_results or not _current_results.get('ranked_candidates'):
        return jsonify({'error': 'No analysis results available'}), 404
    
    candidates = _current_results['ranked_candidates']
    if candidate_index < 0 or candidate_index >= len(candidates):
        return jsonify({'error': 'Invalid candidate index'}), 404
    
    c = candidates[candidate_index]
    profile = c.get('profile', {})
    
    ats_result = ats_scorer.score_resume(profile)
    
    # Get job-specific optimization
    jd_profile = _current_jd_profile or {}
    optimization = ats_optimizer.optimize_for_job(
        profile, 
        jd_profile.get('required_skills', []),
        jd_profile
    )
    
    return jsonify({
        'candidate_name': c['candidate_name'],
        'ats_score': ats_result,
        'optimization': optimization
    })


@app.route('/api/salary-predict/<int:candidate_index>', methods=['GET'])
def predict_salary(candidate_index):
    """Predict salary range for a candidate."""
    global _current_results, _current_jd_profile
    if not _current_results or not _current_results.get('ranked_candidates'):
        return jsonify({'error': 'No analysis results available'}), 404
    
    candidates = _current_results['ranked_candidates']
    if candidate_index < 0 or candidate_index >= len(candidates):
        return jsonify({'error': 'Invalid candidate index'}), 404
    
    c = candidates[candidate_index]
    profile = c.get('profile', {})
    jd_profile = _current_jd_profile
    
    prediction = salary_predictor.predict_salary(profile, jd_profile)
    
    return jsonify({
        'candidate_name': c['candidate_name'],
        'prediction': prediction
    })


@app.route('/api/salary-compare', methods=['POST'])
def compare_salary():
    """Compare offered salary to market prediction."""
    if not request.is_json:
        return jsonify({'error': 'JSON body required'}), 400
    
    offer = request.json.get('offered_salary')
    candidate_index = request.json.get('candidate_index', 0)
    
    if not offer:
        return jsonify({'error': 'offered_salary is required'}), 400
    
    global _current_results, _current_jd_profile
    if not _current_results or not _current_results.get('ranked_candidates'):
        return jsonify({'error': 'No analysis results available'}), 400
    
    candidates = _current_results['ranked_candidates']
    if candidate_index < 0 or candidate_index >= len(candidates):
        return jsonify({'error': 'Invalid candidate index'}), 400
    
    c = candidates[candidate_index]
    profile = c.get('profile', {})
    prediction = salary_predictor.predict_salary(profile, _current_jd_profile)
    
    comparison = salary_predictor.compare_to_market(offer, prediction)
    
    return jsonify({
        'candidate_name': c['candidate_name'],
        'prediction': prediction,
        'comparison': comparison
    })


@app.route('/api/career-path/<int:candidate_index>', methods=['GET'])
def get_career_path(candidate_index):
    """Predict career path for a candidate."""
    global _current_results, _current_jd_profile
    if not _current_results or not _current_results.get('ranked_candidates'):
        return jsonify({'error': 'No analysis results available'}), 404
    
    candidates = _current_results['ranked_candidates']
    if candidate_index < 0 or candidate_index >= len(candidates):
        return jsonify({'error': 'Invalid candidate index'}), 404
    
    c = candidates[candidate_index]
    profile = c.get('profile', {})
    
    path = career_predictor.predict_career_path(profile, _current_jd_profile)
    
    return jsonify({
        'candidate_name': c['candidate_name'],
        'career_path': path
    })


@app.route('/api/email-draft', methods=['POST'])
def generate_email():
    """Generate recruiter email draft."""
    if not request.is_json:
        return jsonify({'error': 'JSON body required'}), 400
    
    email_type = request.json.get('type', 'interview_invite')
    candidate_index = request.json.get('candidate_index', 0)
    role = request.json.get('role', 'Data Scientist')
    company = request.json.get('company', 'Your Company')
    context = request.json.get('context', '')
    
    global _current_results
    if not _current_results or not _current_results.get('ranked_candidates'):
        return jsonify({'error': 'No analysis results available'}), 400
    
    candidates = _current_results['ranked_candidates']
    if candidate_index < 0 or candidate_index >= len(candidates):
        return jsonify({'error': 'Invalid candidate index'}), 400
    
    c = candidates[candidate_index]
    name = c['candidate_name']
    
    email_templates = {
        'interview_invite': lambda: email_generator.generate_interview_invite(name, role, company),
        'offer_letter': lambda: email_generator.generate_offer_letter_draft(name, role, company),
        'rejection': lambda: email_generator.generate_rejection_email(name, role, company),
        'follow_up': lambda: email_generator.generate_follow_up(name, role, company),
        'assessment': lambda: email_generator.generate_assessment_invite(name, role, company),
    }
    
    if email_type in email_templates:
        email = email_templates[email_type]()
    elif email_type == 'custom' and context:
        email = email_generator.generate_custom_email(name, role, company, context)
    else:
        email = email_generator.generate_interview_invite(name, role, company)
    
    return jsonify({
        'candidate_name': name,
        'email': email,
        'email_type': email_type
    })


@app.route('/api/diversity-analysis', methods=['GET'])
def get_diversity_analysis():
    """Analyze diversity metrics across candidate pool."""
    global _current_results
    if not _current_results or not _current_results.get('ranked_candidates'):
        return jsonify({'error': 'No analysis results available'}), 404
    
    candidates = _current_results['ranked_candidates']
    analysis = diversity_analyzer.analyze_pool_diversity(candidates)
    
    return jsonify(analysis)


@app.route('/api/team-fit', methods=['POST'])
def analyze_team_fit():
    """Analyze candidate team fit."""
    if not request.is_json:
        return jsonify({'error': 'JSON body required'}), 400
    
    candidate_index = request.json.get('candidate_index', 0)
    team_culture = request.json.get('team_culture', 'startup')
    team_skills = request.json.get('team_skills', [])
    
    global _current_results
    if not _current_results or not _current_results.get('ranked_candidates'):
        return jsonify({'error': 'No analysis results available'}), 400
    
    candidates = _current_results['ranked_candidates']
    if candidate_index < 0 or candidate_index >= len(candidates):
        return jsonify({'error': 'Invalid candidate index'}), 400
    
    c = candidates[candidate_index]
    profile = c.get('profile', {})
    
    fit = team_fit_analyzer.analyze_team_fit(profile, team_culture, team_skills)
    
    return jsonify({
        'candidate_name': c['candidate_name'],
        'team_fit': fit
    })


@app.route('/api/team-fit/compare', methods=['POST'])
def compare_team_fits():
    """Compare multiple candidates for team fit."""
    if not request.is_json:
        return jsonify({'error': 'JSON body required'}), 400
    
    team_culture = request.json.get('team_culture', 'startup')
    team_skills = request.json.get('team_skills', [])
    
    global _current_results
    if not _current_results or not _current_results.get('ranked_candidates'):
        return jsonify({'error': 'No analysis results available'}), 400
    
    candidates = _current_results['ranked_candidates']
    comparison = team_fit_analyzer.compare_team_fits(candidates, team_culture, team_skills)
    
    return jsonify(comparison)


@app.route('/api/history', methods=['GET'])
def get_history():
    """Get analysis history list."""
    limit = request.args.get('limit', 20, type=int)
    offset = request.args.get('offset', 0, type=int)
    
    entries = history_manager.get_history_list(limit, offset)
    stats = history_manager.get_history_stats()
    
    return jsonify({
        'entries': entries,
        'stats': stats
    })


@app.route('/api/history/<entry_id>', methods=['GET'])
def get_history_entry(entry_id):
    """Get full analysis result from history."""
    entry = history_manager.get_history_entry(entry_id)
    if not entry:
        return jsonify({'error': 'History entry not found'}), 404
    return jsonify(entry)


@app.route('/api/history/<entry_id>', methods=['DELETE'])
def delete_history_entry(entry_id):
    """Delete a history entry."""
    success = history_manager.delete_history_entry(entry_id)
    if success:
        return jsonify({'status': 'deleted'})
    return jsonify({'error': 'Entry not found'}), 404


@app.route('/api/history/clear', methods=['POST'])
def clear_history():
    """Clear all analysis history."""
    history_manager.clear_history()
    return jsonify({'status': 'cleared'})


@app.route('/api/multi-job-analyze', methods=['POST'])
def multi_job_analyze():
    """Analyze candidates across multiple job roles."""
    if not request.is_json:
        return jsonify({'error': 'JSON body required'}), 400
    
    job_data = request.json.get('jobs', {})
    if not job_data:
        return jsonify({'error': 'At least one job definition required'}), 400
    
    global _current_results, _current_jd_profile
    
    # Re-score the current candidate pool against EACH supplied role so the
    # per-role rankings, averages and overlap are genuinely distinct.
    if _current_results and _current_results.get('ranked_candidates'):
        scorer = CandidateScorer(ranking_engine.embedding_model)
        jd_profile = _current_jd_profile or {}
        weights = _current_results.get('weights_used')
        base_candidates = _current_results['ranked_candidates']

        job_candidates_map = {}
        for job_key, data in job_data.items():
            job_profile = data.get('job_profile') or jd_profile

            rescored = []
            for c in base_candidates:
                profile = c.get('profile') or {}
                if not profile:
                    # No profile to re-score against; fall back to the stored result.
                    rescored.append(c)
                    continue
                scores = scorer.compute_all_scores(job_profile, profile, weights=weights)
                rescored.append({
                    'candidate_id': c.get('candidate_id'),
                    'candidate_name': c.get('candidate_name'),
                    'final_score': scores['final_score'],
                    'scores': scores,
                    'profile': profile,
                })

            rescored.sort(key=lambda x: x['final_score'], reverse=True)
            for rank, c in enumerate(rescored, 1):
                c['rank'] = rank

            job_candidates_map[job_key] = {
                'candidates': rescored,
                'job_profile': job_profile
            }
        
        analysis = multi_job_analyzer.analyze_multiple_jobs(job_candidates_map)
        return jsonify(analysis)
    
    return jsonify({'error': 'No candidate data available. Analyze candidates first.'}), 400


# ==================== EXECUTIVE DASHBOARD & DEMO ====================

@app.route('/api/executive-summary', methods=['GET'])
def get_executive_summary():
    """Generate executive-level dashboard with industry benchmarking."""
    global _current_results, _current_jd_profile
    if not _current_results or not _current_results.get('ranked_candidates'):
        return jsonify({'error': 'No analysis results available'}), 404
    
    summary = executive_dashboard.generate_executive_summary(_current_results, _current_jd_profile)
    return jsonify(summary)


@app.route('/api/demo-config', methods=['GET'])
def get_demo_config():
    """Get demo mode configuration for frontend."""
    config = demo_controller.get_demo_config()
    return jsonify(config)


@app.route('/api/features-list', methods=['GET'])
def get_features_list():
    """Get complete list of all system features with descriptions."""
    features = [
        {'name': 'Semantic Resume Parsing', 'module': 'parser.py', 'description': 'NLP-based extraction of skills, experience, education, and behavioral signals from resumes'},
        {'name': '7-Dimension Hybrid Scoring', 'module': 'scorer.py', 'description': 'Multi-dimensional scoring with configurable weights (skill, experience, projects, semantic, education, certs, behavioral)'},
        {'name': 'Explainable AI Rankings', 'module': 'ranking_engine.py', 'description': 'Transparent ranking with human-readable reasons for each candidate'},
        {'name': 'Skill Gap Analysis', 'module': 'skill_gap_analyzer.py', 'description': 'Identifies missing skills with learning recommendations and improvement areas'},
        {'name': 'Candidate Potential Engine', 'module': 'skill_gap_analyzer.py', 'description': 'Predicts growth trajectory, future skill acquisition, and career velocity'},
        {'name': 'Interview Question Generator', 'module': 'interview_generator.py', 'description': 'AI-generated tailored interview questions across 8 categories with difficulty levels'},
        {'name': 'Bias-Free Evaluation', 'module': 'bias_evaluator.py', 'description': 'Anonymizes 7 demographic indicators before scoring for fair hiring'},
        {'name': 'Recruiter Copilot', 'module': 'copilot.py', 'description': 'Natural language Q&A about candidates - like ChatGPT for recruiting'},
        {'name': 'Candidate AI Summaries', 'module': 'app.py', 'description': 'Recruiter-ready executive summaries with seniority and recommendations'},
        {'name': 'ATS Resume Scoring', 'module': 'new_features/ats_scorer.py', 'description': '7-dimension ATS compatibility scoring with 35+ action verbs and optimization tips'},
        {'name': 'Salary Prediction Engine', 'module': 'new_features/salary_predictor.py', 'description': 'Market-based salary prediction with skill premiums across 13 roles'},
        {'name': 'Career Path Predictor', 'module': 'new_features/career_predictor.py', 'description': 'Career trajectory prediction with timelines, milestones, and alternative paths'},
        {'name': 'Email Draft Generator', 'module': 'new_features/email_generator.py', 'description': 'Professional recruiter emails for interviews, offers, rejections, follow-ups'},
        {'name': 'Diversity Analytics', 'module': 'new_features/diversity_analyzer.py', 'description': 'Educational, skill, experience, and domain diversity metrics with recommendations'},
        {'name': 'Team Fit Analysis', 'module': 'new_features/team_fit_analyzer.py', 'description': 'Behavioral compatibility across 5 team cultures with integration recommendations'},
        {'name': 'Analysis History Manager', 'module': 'new_features/analysis_history.py', 'description': 'Persistent analysis storage with restore capability and usage statistics'},
        {'name': 'Multi-Job Batch Analysis', 'module': 'new_features/multi_job_analyzer.py', 'description': 'Cross-role candidate comparison with talent overlap detection'},
        {'name': 'Executive Dashboard', 'module': 'new_features/executive_dashboard.py', 'description': 'Industry benchmarked executive summaries with hiring recommendations'},
    ]
    return jsonify({
        'total_modules': len(features),
        'total_api_endpoints': 28,
        'features': features,
        'version': '3.0.0'
    })


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    app.run(host='0.0.0.0', port=port, debug=debug, use_reloader=False)
