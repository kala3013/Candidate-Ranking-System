"""
AI-Powered Candidate Ranking System
Models Package - Sentence-BERT embeddings, parsing, scoring, and ranking

Enhanced with:
- Skill Gap Analysis & Learning Recommendations
- Candidate Potential Engine (future growth prediction)
- Interview Question Generator
- Bias-Free Evaluation Module
- Recruiter Copilot Chat Assistant
- Behavioral signal extraction (leadership, impact, publications)
- Project depth and quantifiable achievement analysis
- Profile completeness scoring
- Semantic similarity with hybrid scoring
"""

from .embedding_model import EmbeddingModel
from .parser import (
    parse_job_description, parse_candidate_profile, read_file_text,
    extract_skills, extract_behavioral_signals
)
from .scorer import CandidateScorer
from .ranking_engine import RankingEngine
from .skill_gap_analyzer import SkillGapAnalyzer, CandidatePotentialEngine
from .interview_generator import InterviewQuestionGenerator
from .bias_evaluator import BiasFreeEvaluator
from .copilot import RecruiterCopilot

__all__ = [
    'EmbeddingModel',
    'parse_job_description', 'parse_candidate_profile', 'read_file_text',
    'extract_skills', 'extract_behavioral_signals',
    'CandidateScorer',
    'RankingEngine',
    'SkillGapAnalyzer', 'CandidatePotentialEngine',
    'InterviewQuestionGenerator',
    'BiasFreeEvaluator',
    'RecruiterCopilot'
]