#!/usr/bin/env python3
"""
CLI Tool: AI-Powered Candidate Ranking System

Usage:
    python scripts/rank_candidates.py --jd data/jobs/data_scientist_jd.txt --resumes data/resumes/ --output data/outputs/ranked_candidates.csv
    python scripts/rank_candidates.py --jd-file data/jobs/data_scientist_jd.txt --resume-dir data/resumes/ --output data/outputs/ranked_candidates.csv
    python scripts/rank_candidates.py --sample  # Run with sample data
"""

import os
import sys
import json
import argparse
import logging
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.ranking_engine import RankingEngine
from models.parser import read_file_text

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def run_sample():
    """Run analysis with sample data."""
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    jobs_dir = os.path.join(base_dir, 'data', 'jobs')
    resumes_dir = os.path.join(base_dir, 'data', 'resumes')
    output_dir = os.path.join(base_dir, 'data', 'outputs')
    os.makedirs(output_dir, exist_ok=True)

    # Find job files
    jd_files = [f for f in os.listdir(jobs_dir) if f.lower().endswith(('.txt', '.pdf', '.docx'))]
    if not jd_files:
        logger.error("No job description files found in data/jobs/")
        return

    jd_path = os.path.join(jobs_dir, jd_files[0])
    logger.info(f"Reading job description: {jd_files[0]}")
    job_text = read_file_text(jd_path)

    # Find resume files
    resume_files = sorted([
        f for f in os.listdir(resumes_dir) if f.lower().endswith(('.txt', '.pdf', '.docx'))
    ])
    if not resume_files:
        logger.error("No resume files found in data/resumes/")
        return

    logger.info(f"Found {len(resume_files)} candidate resumes")
    
    candidate_texts = []
    candidate_info = []
    for fname in resume_files:
        rpath = os.path.join(resumes_dir, fname)
        text = read_file_text(rpath)
        if text.strip():
            candidate_texts.append(text)
            name = os.path.splitext(fname)[0].replace('_', ' ').title()
            candidate_info.append({'id': fname, 'name': name})
            logger.info(f"  Loaded: {name}")

    # Run ranking engine
    logger.info("\n" + "="*60)
    logger.info("Running AI-Powered Candidate Ranking...")
    logger.info("="*60)
    
    engine = RankingEngine()
    results = engine.rank_candidates(job_text, candidate_texts, candidate_info)

    # Export to CSV
    output_path = os.path.join(output_dir, 'ranked_candidates.csv')
    engine.export_to_csv(results, output_path)
    
    # Also export as JSON
    json_path = os.path.join(output_dir, 'ranked_candidates.json')
    export_to_json(results, json_path)

    # Print results
    print_ranked_results(results)

    logger.info(f"\n✅ Results exported to:")
    logger.info(f"   CSV: {output_path}")
    logger.info(f"   JSON: {json_path}")

    return results


def export_to_json(results, output_path):
    """Export results to JSON format."""
    output = []
    for r in results:
        entry = {
            'rank': r['rank'],
            'candidate_id': r['candidate_id'],
            'candidate_name': r['candidate_name'],
            'final_score': r['final_score'],
            'scores': r['scores'],
            'reason': r['reason'],
            'profile': {
                'technical_skills': r['candidate_profile'].get('technical_skills', []),
                'soft_skills': r['candidate_profile'].get('soft_skills', []),
                'education': r['candidate_profile'].get('education', []),
                'certifications': r['candidate_profile'].get('certifications', []),
                'experience_years': r['candidate_profile'].get('experience_years', 0),
                'behavioral_signals': r['candidate_profile'].get('behavioral_signals', {})
            }
        }
        output.append(entry)
    
    with open(output_path, 'w') as f:
        json.dump({
            'generated_at': datetime.now().isoformat(),
            'total_candidates': len(results),
            'ranked_candidates': output
        }, f, indent=2)


def print_ranked_results(results):
    """Print formatted ranking results to console."""
    print("\n" + "="*80)
    print("🏆 RANKED CANDIDATES")
    print("="*80)
    print(f"{'Rank':<6} {'Candidate':<25} {'Score':<8} {'Skill':<8} {'Exp':<8} {'Behav':<8} {'Semantic':<10}")
    print("-"*80)
    
    for r in results:
        name = r['candidate_name'][:24]
        score = f"{r['final_score']*100:.1f}%"
        skill = f"{r['scores']['skill_match']*100:.0f}%"
        exp = f"{r['scores']['experience_match']*100:.0f}%"
        behav = f"{r['scores'].get('behavioral_score', 0)*100:.0f}%"
        sem = f"{r['scores']['semantic_similarity']*100:.0f}%"
        print(f"{r['rank']:<6} {name:<25} {score:<8} {skill:<8} {exp:<8} {behav:<8} {sem:<10}")
    
    print("-"*80)
    print("\n📋 DETAILED EXPLANATIONS:")
    for r in results:
        print(f"\n  #{r['rank']} {r['candidate_name']} ({r['final_score']*100:.1f}%)")
        print(f"  → {r['reason']}")


def run_cli():
    """Run CLI mode with command line arguments."""
    parser = argparse.ArgumentParser(
        description='AI-Powered Candidate Ranking System',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python scripts/rank_candidates.py --sample
  python scripts/rank_candidates.py --jd data/jobs/data_scientist_jd.txt --resume-dir data/resumes/ --output results.csv
        """
    )
    
    parser.add_argument('--sample', action='store_true', help='Run with sample data')
    parser.add_argument('--jd', type=str, help='Path to job description file')
    parser.add_argument('--jd-text', type=str, help='Job description text (inline)')
    parser.add_argument('--resume-dir', type=str, help='Directory containing resume files')
    parser.add_argument('--resume-files', type=str, nargs='+', help='List of resume files')
    parser.add_argument('--output', type=str, help='Output CSV file path')
    
    args = parser.parse_args()

    if args.sample:
        run_sample()
        return

    # Get job description
    job_text = ''
    if args.jd:
        logger.info(f"Reading job description from: {args.jd}")
        job_text = read_file_text(args.jd)
    elif args.jd_text:
        job_text = args.jd_text
    else:
        logger.error("No job description provided. Use --jd, --jd-text, or --sample")
        return

    if not job_text.strip():
        logger.error("Empty job description")
        return

    # Get candidate resumes
    candidate_texts = []
    candidate_info = []
    
    if args.resume_dir:
        engine = RankingEngine()
        resume_files = sorted([
            f for f in os.listdir(args.resume_dir) 
            if f.lower().endswith(('.txt', '.pdf', '.docx'))
        ])
        for fname in resume_files:
            fpath = os.path.join(args.resume_dir, fname)
            text = read_file_text(fpath)
            if text.strip():
                candidate_texts.append(text)
                name = os.path.splitext(fname)[0].replace('_', ' ').title()
                candidate_info.append({'id': fname, 'name': name})
    
    if args.resume_files:
        for fpath in args.resume_files:
            text = read_file_text(fpath)
            if text.strip():
                candidate_texts.append(text)
                name = os.path.splitext(os.path.basename(fpath))[0].replace('_', ' ').title()
                candidate_info.append({'id': os.path.basename(fpath), 'name': name})

    if not candidate_texts:
        logger.error("No candidate resumes provided")
        return

    logger.info(f"Processing {len(candidate_texts)} candidates...")
    
    engine = RankingEngine()
    results = engine.rank_candidates(job_text, candidate_texts, candidate_info)
    
    # Export
    if args.output:
        engine.export_to_csv(results, args.output)
        logger.info(f"Results saved to: {args.output}")
    else:
        output_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            'data', 'outputs', 'ranked_candidates.csv'
        )
        engine.export_to_csv(results, output_path)
    
    print_ranked_results(results)


if __name__ == '__main__':
    run_cli()