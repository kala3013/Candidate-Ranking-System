"""Executive Dashboard & Benchmarking Module - Creates stunning executive summaries and industry comparisons."""

import logging
from datetime import datetime
from collections import Counter

logger = logging.getLogger(__name__)


class ExecutiveDashboardGenerator:
    """Generates executive-level dashboards with industry benchmarking and visual insights."""
    
    # Industry benchmark data (mock but realistic for India market)
    INDUSTRY_BENCHMARKS = {
        'data_scientist': {
            'avg_salary_lpa': 18.5,
            'avg_experience': 4.2,
            'top_skills': ['python', 'sql', 'machine learning', 'deep learning', 'nlp'],
            'avg_skills_per_candidate': 6.8,
            'hiring_difficulty': 'High',
            'market_trend': 'Growing 25% YoY',
            'avg_time_to_hire_days': 45,
            'supply_demand_ratio': 0.6
        },
        'ml_engineer': {
            'avg_salary_lpa': 22.0,
            'avg_experience': 3.8,
            'top_skills': ['python', 'tensorflow', 'pytorch', 'mlops', 'docker'],
            'avg_skills_per_candidate': 7.2,
            'hiring_difficulty': 'Very High',
            'market_trend': 'Growing 35% YoY',
            'avg_time_to_hire_days': 55,
            'supply_demand_ratio': 0.4
        },
        'data_engineer': {
            'avg_salary_lpa': 16.0,
            'avg_experience': 4.5,
            'top_skills': ['sql', 'python', 'spark', 'airflow', 'kafka'],
            'avg_skills_per_candidate': 6.5,
            'hiring_difficulty': 'High',
            'market_trend': 'Growing 30% YoY',
            'avg_time_to_hire_days': 40,
            'supply_demand_ratio': 0.55
        },
        'software_engineer': {
            'avg_salary_lpa': 14.0,
            'avg_experience': 3.5,
            'top_skills': ['python', 'java', 'javascript', 'react', 'sql'],
            'avg_skills_per_candidate': 5.8,
            'hiring_difficulty': 'Medium',
            'market_trend': 'Growing 15% YoY',
            'avg_time_to_hire_days': 30,
            'supply_demand_ratio': 0.8
        }
    }

    # Company brand colors for report theming
    COMPANY_THEMES = {
        'default': {'primary': '#6c63ff', 'secondary': '#00d4ff', 'accent': '#00ff88'},
        'tech': {'primary': '#2563eb', 'secondary': '#3b82f6', 'accent': '#10b981'},
        'finance': {'primary': '#1e293b', 'secondary': '#334155', 'accent': '#f59e0b'},
        'healthcare': {'primary': '#0d9488', 'secondary': '#14b8a6', 'accent': '#06b6d4'},
    }

    def __init__(self):
        pass

    def generate_executive_summary(self, results, jd_profile=None):
        """Generate a comprehensive executive summary with benchmarks."""
        if not results or not results.get('ranked_candidates'):
            return {'error': 'No results to analyze'}
        
        candidates = results['ranked_candidates']
        summary = results.get('summary', {})
        job = jd_profile or results.get('job_profile', {})
        
        role = (job or {}).get('role', 'data_scientist')
        role_key = self._normalize_role(role)
        benchmark = self.INDUSTRY_BENCHMARKS.get(role_key, self.INDUSTRY_BENCHMARKS['data_scientist'])
        
        # Compute candidate pool metrics
        pool_metrics = self._compute_pool_metrics(candidates, summary)
        
        # Compare to industry benchmarks
        benchmark_comparison = self._compare_to_benchmark(pool_metrics, benchmark)
        
        # Compute hiring recommendation
        hiring_rec = self._compute_hiring_recommendation(pool_metrics, benchmark)
        
        # Generate visual data for charts
        chart_data = self._generate_chart_data(candidates, summary)
        
        # Generate insights
        insights = self._generate_executive_insights(pool_metrics, benchmark_comparison, candidates)
        
        # Score the talent pool
        pool_score = self._score_talent_pool(pool_metrics, benchmark)
        
        return {
            'executive_summary': {
                'role': role,
                'total_candidates': len(candidates),
                'analysis_date': datetime.now().strftime('%B %d, %Y'),
                'report_id': f'TALENTRANK-{datetime.now().strftime("%Y%m%d-%H%M%S")}',
                'pool_quality_score': pool_score,
                'pool_quality_label': 'Excellent' if pool_score >= 85 else 'Strong' if pool_score >= 70 else 'Adequate' if pool_score >= 50 else 'Needs Improvement',
            },
            'pool_metrics': pool_metrics,
            'benchmark_comparison': benchmark_comparison,
            'hiring_recommendation': hiring_rec,
            'chart_data': chart_data,
            'insights': insights,
            'market_context': {
                'role_demand': benchmark.get('market_trend', 'Stable'),
                'hiring_difficulty': benchmark.get('hiring_difficulty', 'Medium'),
                'avg_time_to_hire_days': benchmark.get('avg_time_to_hire_days', 30),
                'supply_demand_ratio': benchmark.get('supply_demand_ratio', 0.5),
                'market_avg_salary_lpa': benchmark.get('avg_salary_lpa', 15),
            },
            'top_recommendations': hiring_rec.get('top_recommendations', []),
            'key_risks': hiring_rec.get('risks', [])
        }

    def _compute_pool_metrics(self, candidates, summary):
        """Compute detailed candidate pool metrics."""
        scores = [c['final_score'] * 100 for c in candidates]
        experiences = [c.get('profile', {}).get('experience_years', 0) for c in candidates]
        skills_counts = [len(c.get('profile', {}).get('technical_skills', [])) for c in candidates]
        
        return {
            'candidate_count': len(candidates),
            'average_score': round(summary.get('average_score', 0), 1),
            'median_score': round(summary.get('median_score', 0), 1),
            'top_score': round(summary.get('top_score', 0), 1),
            'score_std_dev': self._std_dev(scores),
            'score_variance': round(self._std_dev(scores) ** 2, 1),
            'average_experience_years': round(sum(experiences) / max(len(experiences), 1), 1),
            'experience_range': {'min': min(experiences) if experiences else 0, 'max': max(experiences) if experiences else 0},
            'average_skills_per_candidate': round(sum(skills_counts) / max(len(skills_counts), 1), 1),
            'skill_diversity': len(set(s for c in candidates for s in c.get('profile', {}).get('technical_skills', []))),
            'top_candidate_name': candidates[0]['candidate_name'] if candidates else '',
            'top_candidate_score': round(candidates[0]['final_score'] * 100, 1) if candidates else 0,
            'score_distribution': summary.get('score_distribution', {}),
        }

    def _compare_to_benchmark(self, pool, benchmark):
        """Compare candidate pool metrics to industry benchmarks."""
        comparisons = []
        
        # Score comparison
        if pool['average_score'] >= 75:
            score_assessment = 'Above Industry Average'
            score_color = 'positive'
        elif pool['average_score'] >= 55:
            score_assessment = 'At Industry Average'
            score_color = 'neutral'
        else:
            score_assessment = 'Below Industry Average'
            score_color = 'negative'
        
        comparisons.append({
            'metric': 'Average Score',
            'pool_value': f"{pool['average_score']}%",
            'benchmark_value': '65% (Industry Avg)',
            'assessment': score_assessment,
            'color': score_color,
            'detail': f"Your pool scores {pool['average_score']}% vs industry average of 65%"
        })
        
        # Experience comparison
        exp_diff = pool['average_experience_years'] - benchmark['avg_experience']
        comparisons.append({
            'metric': 'Avg Experience',
            'pool_value': f"{pool['average_experience_years']} yrs",
            'benchmark_value': f"{benchmark['avg_experience']} yrs",
            'assessment': f"{'+' if exp_diff >= 0 else ''}{round(exp_diff, 1)} yrs difference",
            'color': 'positive' if exp_diff >= 0 else 'neutral',
            'detail': f"Pool experience ({pool['average_experience_years']}yrs) vs industry ({benchmark['avg_experience']}yrs)"
        })
        
        # Skills comparison
        skill_diff = pool['average_skills_per_candidate'] - benchmark['avg_skills_per_candidate']
        comparisons.append({
            'metric': 'Avg Skills/Candidate',
            'pool_value': f"{pool['average_skills_per_candidate']} skills",
            'benchmark_value': f"{benchmark['avg_skills_per_candidate']} skills",
            'assessment': f"{'+' if skill_diff >= 0 else ''}{round(skill_diff, 1)} skills",
            'color': 'positive' if skill_diff >= 0 else 'negative',
            'detail': f"Candidates average {pool['average_skills_per_candidate']} skills vs {benchmark['avg_skills_per_candidate']} industry benchmark"
        })
        
        # Pool size comparison
        comparisons.append({
            'metric': 'Pool Size',
            'pool_value': f"{pool['candidate_count']} candidates",
            'benchmark_value': '10+ recommended',
            'assessment': 'Adequate' if pool['candidate_count'] >= 5 else 'Small Pool',
            'color': 'positive' if pool['candidate_count'] >= 5 else 'negative',
            'detail': f"Consider sourcing more candidates if possible ({pool['candidate_count']} of 10+ recommended)"
        })
        
        return {
            'overall_assessment': score_assessment,
            'comparisons': comparisons,
            'industry_role': benchmark.get('top_skills', [])[:5],
            'pool_strength': 'Strong' if pool['average_score'] >= 70 else 'Moderate' if pool['average_score'] >= 50 else 'Weak'
        }

    def _compute_hiring_recommendation(self, pool, benchmark):
        """Generate hiring recommendation based on pool analysis."""
        recommendations = []
        risks = []
        
        avg_score = pool['average_score']
        count = pool['candidate_count']
        top_score = pool['top_score']
        
        if avg_score >= 75 and count >= 5:
            recommendations.append('Proceed with interviews — strong candidate pool available')
            recommendations.append(f'Top candidate ({pool["top_candidate_name"]}) scored {top_score}% — highly recommended for immediate interview')
            recommendations.append('Consider parallel interviews for top 3 candidates to expedite hiring')
        elif avg_score >= 60 and count >= 3:
            recommendations.append('Schedule interviews — adequate pool quality')
            recommendations.append(f'Prioritize {pool["top_candidate_name"]} with {top_score}% match score')
            recommendations.append('Continue sourcing to strengthen pipeline for future needs')
        elif count >= 1:
            recommendations.append('Expand candidate search for stronger options')
            recommendations.append('Consider upskilling existing candidates if timeline is flexible')
        else:
            recommendations.append('Urgent: Re-evaluate job requirements or expand sourcing channels')
        
        if count < 5:
            risks.append(f'Small candidate pool ({count}) increases hiring risk')
        if avg_score < 60:
            risks.append('Below-average candidate quality may require extended search')
        if pool['average_experience_years'] < benchmark['avg_experience'] * 0.7:
            risks.append('Candidates have significantly less experience than industry average')
        
        # Which candidate to hire
        hire_decision = None
        if pool['top_candidate_score'] >= 75:
            hire_decision = {
                'candidate': pool['top_candidate_name'],
                'confidence': 'High',
                'reason': f'Top scorer with {top_score}% match — strongly recommended for hire',
                'timeline': 'Immediate interview recommended'
            }
        elif pool['top_candidate_score'] >= 60:
            hire_decision = {
                'candidate': pool['top_candidate_name'],
                'confidence': 'Medium',
                'reason': f'Best available candidate with {top_score}% match — consider interviewing',
                'timeline': 'Schedule interview this week'
            }
        
        return {
            'top_recommendations': recommendations,
            'risks': risks,
            'hire_decision': hire_decision,
            'overall_verdict': 'Proceed with hiring' if avg_score >= 65 else 'Expand search' if avg_score >= 45 else 'Re-evaluate strategy',
            'estimated_time_to_hire': benchmark.get('avg_time_to_hire_days', 30),
            'estimated_time_to_hire_text': f"Estimated {benchmark.get('avg_time_to_hire_days', 30)} days to fill position"
        }

    def _generate_chart_data(self, candidates, summary):
        """Generate structured data for frontend chart visualizations."""
        scores = [c['final_score'] * 100 for c in candidates]
        names = [c['candidate_name'] for c in candidates]
        
        return {
            'score_distribution': {
                'labels': ['Excellent (80%+)', 'Good (60-80%)', 'Moderate (40-60%)', 'Below 40%'],
                'values': [
                    sum(1 for s in scores if s >= 80),
                    sum(1 for s in scores if 60 <= s < 80),
                    sum(1 for s in scores if 40 <= s < 60),
                    sum(1 for s in scores if s < 40)
                ]
            },
            'candidate_scores': {
                'labels': names,
                'values': [round(s, 1) for s in scores]
            },
            'skill_breakdown': {
                'labels': ['Skill', 'Experience', 'Semantic', 'Projects', 'Education', 'Certs', 'Soft Skills'],
                'values': [0.35, 0.20, 0.15, 0.15, 0.05, 0.05, 0.05]  # Default weights
            },
            'score_histogram': self._compute_histogram(scores, 5),
            'pool_quality_gauge': {
                'value': round(sum(scores) / max(len(scores), 1), 1),
                'max': 100,
                'thresholds': {'red': 40, 'yellow': 60, 'green': 80}
            }
        }

    def _generate_executive_insights(self, pool, benchmark, candidates):
        """Generate natural language insights for executives."""
        insights = []
        
        # Pool strength insight
        if pool['average_score'] >= 75:
            insights.append('💪 **Strong Talent Pool**: Your candidate pool significantly exceeds industry benchmarks. Proceed confidently with hiring.')
        elif pool['average_score'] >= 55:
            insights.append('📊 **Adequate Talent Pool**: Candidate quality is at market average. Some top performers identified for immediate action.')
        else:
            insights.append('⚠️ **Limited Talent Pool**: Pool quality needs improvement. Consider expanding sourcing channels or adjusting requirements.')
        
        # Top performer insight
        if candidates:
            top = candidates[0]
            insights.append(f'🏆 **Top Performer**: **{top["candidate_name"]}** leads with {round(top["final_score"]*100,1)}% match score — {top["reason"][:100]}...')
        
        # Skill gap insight
        all_skills = set()
        missing_skills = Counter()
        for c in candidates:
            for s in c.get('profile', {}).get('technical_skills', []):
                all_skills.add(s.lower())
            for gap in c.get('skill_gaps', {}).get('missing_required_skills', []):
                missing_skills[gap] += 1
        
        if missing_skills:
            top_gap = missing_skills.most_common(1)[0]
            insights.append(f'🔧 **Critical Skill Gap**: **{top_gap[0]}** is missing in {top_gap[1]}/{len(candidates)} candidates — consider training or prioritizing candidates with this skill.')
        
        # Diversity insight
        if len(all_skills) >= 20:
            insights.append(f'🌈 **Skill Diversity**: Your candidates span {len(all_skills)} unique skills — indicating a diverse and versatile talent pool.')
        
        # Market insight
        role_key = 'data_scientist'  # default
        if pool.get('average_score', 0) > 0:
            role_key = 'data_scientist'  # simplified
        benchmark_data = self.INDUSTRY_BENCHMARKS.get(role_key, {})
        if benchmark_data:
            insights.append(f'📈 **Market Context**: {benchmark_data.get("market_trend", "Stable market")} for this role. {benchmark_data.get("hiring_difficulty", "Medium")} hiring difficulty with avg {benchmark_data.get("avg_time_to_hire_days", 30)} days to hire.')
        
        # Action insight
        insights.append('🎯 **Recommended Action**: ' + (
            'Schedule interviews with top 3 candidates immediately.' if pool['average_score'] >= 65
            else 'Expand sourcing and re-post position with adjusted requirements.' if pool['average_score'] >= 45
            else 'Re-evaluate job description and sourcing strategy before proceeding.'
        ))
        
        return insights

    def _score_talent_pool(self, pool, benchmark):
        """Score overall talent pool quality out of 100."""
        score = 0
        
        # Score quality (40 points)
        score += min(pool['average_score'] * 0.4, 40)
        
        # Count bonus (20 points)
        if pool['candidate_count'] >= 10:
            score += 20
        elif pool['candidate_count'] >= 5:
            score += 15
        elif pool['candidate_count'] >= 3:
            score += 10
        else:
            score += 5
        
        # Experience bonus (15 points)
        exp_ratio = pool['average_experience_years'] / max(benchmark['avg_experience'], 1)
        score += min(exp_ratio * 15, 15)
        
        # Skills bonus (15 points)
        skill_ratio = pool['average_skills_per_candidate'] / max(benchmark['avg_skills_per_candidate'], 1)
        score += min(skill_ratio * 15, 15)
        
        # Diversity bonus (10 points)
        score += min(pool['skill_diversity'] * 2, 10)
        
        return round(min(score, 100), 1)

    def _std_dev(self, values):
        """Calculate standard deviation."""
        if len(values) < 2:
            return 0
        mean = sum(values) / len(values)
        variance = sum((x - mean) ** 2 for x in values) / (len(values) - 1)
        return round(variance ** 0.5, 1)

    def _compute_histogram(self, values, bins):
        """Compute histogram data for score distribution visualization."""
        if not values:
            return {'labels': [], 'values': []}
        min_val = 0
        max_val = 100
        bin_size = (max_val - min_val) / bins
        bin_labels = []
        bin_counts = []
        for i in range(bins):
            lower = min_val + i * bin_size
            upper = lower + bin_size
            bin_labels.append(f'{int(lower)}-{int(upper)}%')
            count = sum(1 for v in values if lower <= v < upper)
            bin_counts.append(count)
        return {'labels': bin_labels, 'values': bin_counts}

    def _normalize_role(self, role):
        """Normalize role string to benchmark keys."""
        role_lower = role.lower().strip()
        for key in self.INDUSTRY_BENCHMARKS:
            if key in role_lower or role_lower in key:
                return key
        mappings = {
            'data scientist': 'data_scientist',
            'ml engineer': 'ml_engineer',
            'machine learning': 'ml_engineer',
            'data engineer': 'data_engineer',
            'software engineer': 'software_engineer',
            'swe': 'software_engineer',
        }
        for key, val in mappings.items():
            if key in role_lower:
                return val
        return 'data_scientist'


class DemoModeController:
    """Controls the automated demo walkthrough."""
    
    def __init__(self):
        self.demo_steps = [
            {'action': 'load_sample', 'label': '📂 Loading sample data', 'duration': 2},
            {'action': 'analyze', 'label': '🧠 AI Analysis Engine starting', 'duration': 3},
            {'action': 'show_rankings', 'label': '🏆 Top candidates ranked', 'duration': 2},
            {'action': 'show_comparison', 'label': '⚖️ Comparing top candidates', 'duration': 2},
            {'action': 'show_skill_gaps', 'label': '🔧 Analyzing skill gaps', 'duration': 2},
            {'action': 'show_interview', 'label': '🎯 Generating interview questions', 'duration': 2},
            {'action': 'show_copilot', 'label': '🤖 Recruiter Copilot demo', 'duration': 2},
            {'action': 'show_report', 'label': '📄 Generating executive report', 'duration': 2},
            {'action': 'complete', 'label': '✅ Demo complete! All features operational.', 'duration': 0}
        ]
    
    def get_demo_config(self):
        """Return demo configuration for frontend."""
        return {
            'steps': self.demo_steps,
            'total_steps': len(self.demo_steps),
            'estimated_duration_seconds': sum(s['duration'] for s in self.demo_steps),
            'version': '2.0.0',
            'features_demoed': [
                'Semantic Resume Parsing',
                '7-Dimension Hybrid Scoring',
                'Explainable AI Rankings',
                'Skill Gap Analysis',
                'Interview Question Generation',
                'Bias-Free Evaluation',
                'Recruiter Copilot',
                'Executive Report Generation',
                'ATS Resume Scoring',
                'Salary Prediction',
                'Career Path Prediction',
                'Diversity Analytics',
                'Team Fit Analysis'
            ]
        }