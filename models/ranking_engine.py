"""Ranking Engine - Orchestrates the full candidate ranking pipeline."""

import os
import json
import logging
import pandas as pd
from datetime import datetime

from .parser import read_file_text, parse_job_description, parse_candidate_profile, extract_behavioral_signals
from .embedding_model import EmbeddingModel
from .scorer import CandidateScorer

logger = logging.getLogger(__name__)


class RankingEngine:
    """
    Main ranking engine that orchestrates:
    1. Reading and parsing job descriptions
    2. Reading and parsing candidate resumes
    3. Computing embeddings and similarity scores
    4. Generating final rankings with explanations
    5. Exporting results to CSV
    """

    def __init__(self):
        """Initialize the ranking engine with embedding model and scorer."""
        self.embedding_model = EmbeddingModel()
        self.scorer = CandidateScorer(self.embedding_model)

    def analyze_job(self, jd_text):
        """
        Analyze a job description text.

        Args:
            jd_text: Job description text content.

        Returns:
            dict: Parsed job profile
        """
        return parse_job_description(jd_text)

    def analyze_candidate(self, resume_text, candidate_id='C000', candidate_name='Unknown'):
        """
        Analyze a candidate resume text.

        Args:
            resume_text: Resume text content.
            candidate_id: Unique identifier for the candidate.
            candidate_name: Name of the candidate.

        Returns:
            dict: Parsed candidate profile
        """
        return parse_candidate_profile(resume_text, candidate_id, candidate_name)

    def rank_candidates(self, jd_text, candidate_texts, candidate_info=None, weights=None):
        """
        Rank a list of candidates against a job description.

        Args:
            jd_text: Job description text.
            candidate_texts: List of resume text contents.
            candidate_info: Optional list of dicts with 'id' and 'name' keys.
            weights: Optional custom scoring weights (see
                CandidateScorer.resolve_weights). Normalised internally.

        Returns:
            list: Ranked list of candidate results with scores and explanations.
        """
        # Parse job description
        jd_profile = self.analyze_job(jd_text)
        logger.info(f"Job parsed: {len(jd_profile.get('required_skills', []))} skills, "
                     f"{jd_profile.get('experience_required', 0)} years exp required")

        # Parse candidates and compute scores
        results = []
        for i, text in enumerate(candidate_texts):
            cid = candidate_info[i]['id'] if candidate_info and i < len(candidate_info) else f'C{i+1:03d}'
            cname = candidate_info[i]['name'] if candidate_info and i < len(candidate_info) else f'Candidate {i+1}'

            candidate_profile = self.analyze_candidate(text, cid, cname)
            scores = self.scorer.compute_all_scores(jd_profile, candidate_profile, weights=weights)
            explanation = self.scorer.generate_explanation(jd_profile, candidate_profile, scores)

            results.append({
                'candidate_id': cid,
                'candidate_name': cname,
                'final_score': scores['final_score'],
                'scores': scores,
                'reason': explanation,
                'candidate_profile': candidate_profile
            })

        # Sort by final score descending
        results.sort(key=lambda x: x['final_score'], reverse=True)

        # Assign ranks
        for rank, result in enumerate(results, 1):
            result['rank'] = rank

        logger.info(f"Ranked {len(results)} candidates")
        return results

    def export_to_csv(self, ranked_results, output_path=None):
        """
        Export ranked results to CSV file.

        Args:
            ranked_results: List of ranked candidate dicts.
            output_path: Output CSV file path. Defaults to data/outputs/ranked_candidates.csv

        Returns:
            str: Path to the generated CSV file.
        """
        if output_path is None:
            output_path = os.path.join(
                os.path.dirname(os.path.dirname(__file__)),
                'data', 'outputs', 'ranked_candidates.csv'
            )

        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        rows = []
        for r in ranked_results:
            rows.append({
                'Rank': r['rank'],
                'Candidate_ID': r['candidate_id'],
                'Candidate_Name': r['candidate_name'],
                'Final_Score': r['final_score'],
                'Skill_Match': r['scores']['skill_match'],
                'Experience_Match': r['scores']['experience_match'],
                'Project_Relevance': r['scores']['project_relevance'],
                'Education': r['scores']['education'],
                'Certifications': r['scores']['certifications'],
                'Semantic_Similarity': r['scores']['semantic_similarity'],
                'Behavioral_Score': r['scores'].get('behavioral_score', 0),
                'Profile_Completeness': r['scores'].get('completeness', 0),
                'Reason': r['reason'],
                'Skills': ', '.join(r.get('candidate_profile', {}).get('technical_skills', [])),
                'Experience_Years': r.get('candidate_profile', {}).get('experience_years', 0),
                'Education_Level': ', '.join(r.get('candidate_profile', {}).get('education', [])),
                'Certifications_List': ', '.join(r.get('candidate_profile', {}).get('certifications', []))
            })

        df = pd.DataFrame(rows)
        df.to_csv(output_path, index=False)
        logger.info(f"Results exported to {output_path}")
        return output_path

    def process_jd_file(self, file_path):
        """
        Read and parse a job description file.

        Args:
            file_path: Path to the JD file (PDF, DOCX, TXT).

        Returns:
            tuple: (text_content, parsed_profile)
        """
        text = read_file_text(file_path)
        profile = parse_job_description(text)
        return text, profile

    def process_resume_file(self, file_path, candidate_id='C000', candidate_name='Unknown'):
        """
        Read and parse a resume file.

        Args:
            file_path: Path to the resume file.
            candidate_id: Candidate ID.
            candidate_name: Candidate name.

        Returns:
            tuple: (text_content, parsed_profile)
        """
        text = read_file_text(file_path)
        profile = parse_candidate_profile(text, candidate_id, candidate_name)
        return text, profile

    def batch_process_resumes(self, resume_dir):
        """
        Batch process all resume files in a directory.

        Args:
            resume_dir: Directory containing resume files.

        Returns:
            tuple: (texts, info_list)
        """
        texts = []
        info_list = []

        supported = ['.pdf', '.docx', '.txt']
        for fname in sorted(os.listdir(resume_dir)):
            ext = os.path.splitext(fname)[1].lower()
            if ext in supported:
                fpath = os.path.join(resume_dir, fname)
                text = read_file_text(fpath)
                if text.strip():
                    texts.append(text)
                    name = os.path.splitext(fname)[0].replace('_', ' ').replace('-', ' ').title()
                    info_list.append({'id': fname, 'name': name})

        return texts, info_list