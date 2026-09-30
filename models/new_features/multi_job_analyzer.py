"""Multi-Job Batch Analysis Module - Compare candidate pools across multiple roles."""

import logging
from collections import defaultdict

logger = logging.getLogger(__name__)


class MultiJobBatchAnalyzer:
    """Analyzes and compares candidate pools across multiple job roles simultaneously."""

    def __init__(self):
        pass

    def analyze_multiple_jobs(self, job_candidates_map):
        """
        Analyze candidate pools across multiple job roles.
        
        Args:
            job_candidates_map: dict mapping job_role -> {'job_profile': dict, 'candidates': [ranked_candidates]}
            
        Returns:
            dict: Multi-job analysis with cross-comparisons
        """
        jobs = list(job_candidates_map.keys())
        results = {}
        
        for job_key, data in job_candidates_map.items():
            candidates = data.get('candidates', [])
            job_profile = data.get('job_profile', {})
            results[job_key] = {
                'total_candidates': len(candidates),
                'top_candidate': candidates[0]['candidate_name'] if candidates else None,
                'top_score': candidates[0]['final_score'] if candidates else 0,
                'average_score': sum(c['final_score'] for c in candidates) / max(len(candidates), 1),
                'job_profile': {
                    'role': job_profile.get('role', job_key),
                    'skills': job_profile.get('required_skills', [])[:5]
                },
                'score_distribution': self._score_distribution(candidates),
                'candidates': [
                    {'name': c['candidate_name'], 'score': c['final_score'], 'rank': c['rank']}
                    for c in candidates[:5]
                ]
            }
        
        # Cross-job comparisons
        cross_comparisons = self._cross_compare_jobs(job_candidates_map, jobs)
        
        return {
            'total_jobs_analyzed': len(jobs),
            'jobs': jobs,
            'role_summaries': results,
            'cross_comparisons': cross_comparisons,
            'talent_overlap': self._find_talent_overlap(job_candidates_map, jobs),
            'hiring_priorities': self._rank_hiring_priorities(results),
            'summary': self._generate_multi_job_summary(results)
        }

    def _score_distribution(self, candidates):
        """Calculate score distribution for a job's candidate pool."""
        if not candidates:
            return {}
        scores = [c['final_score'] * 100 for c in candidates]
        return {
            'excellent': sum(1 for s in scores if s >= 80),
            'good': sum(1 for s in scores if 60 <= s < 80),
            'moderate': sum(1 for s in scores if 40 <= s < 60),
            'low': sum(1 for s in scores if s < 40),
            'average': round(sum(scores) / len(scores), 1)
        }

    def _cross_compare_jobs(self, job_candidates_map, jobs):
        """Compare candidate pools across different job roles."""
        comparisons = []
        for i in range(len(jobs)):
            for j in range(i + 1, len(jobs)):
                job1 = jobs[i]
                job2 = jobs[j]
                data1 = job_candidates_map[job1]
                data2 = job_candidates_map[job2]
                
                candidates1 = data1.get('candidates', [])
                candidates2 = data2.get('candidates', [])
                
                avg1 = sum(c['final_score'] for c in candidates1) / max(len(candidates1), 1)
                avg2 = sum(c['final_score'] for c in candidates2) / max(len(candidates2), 1)
                
                comparisons.append({
                    'job_1': job1,
                    'job_2': job2,
                    'candidates_1': len(candidates1),
                    'candidates_2': len(candidates2),
                    'avg_score_1': round(avg1 * 100, 1),
                    'avg_score_2': round(avg2 * 100, 1),
                    'score_difference': round((avg1 - avg2) * 100, 1),
                    'stronger_pool': job1 if avg1 > avg2 else job2
                })
        
        return comparisons

    def _find_talent_overlap(self, job_candidates_map, jobs):
        """Find candidates that appear across multiple job pools."""
        candidate_jobs = defaultdict(list)
        
        for job_key, data in job_candidates_map.items():
            for c in data.get('candidates', []):
                name = c.get('candidate_name', '')
                if name:
                    candidate_jobs[name].append({
                        'job': job_key,
                        'score': c.get('final_score', 0),
                        'rank': c.get('rank', 0)
                    })
        
        overlapping = {
            name: jobs_list
            for name, jobs_list in candidate_jobs.items()
            if len(jobs_list) >= 2
        }
        
        return {
            'total_overlapping': len(overlapping),
            'overlapping_candidates': [
                {
                    'name': name,
                    'matched_roles': [j['job'] for j in jobs_list],
                    'best_score': max(j['score'] for j in jobs_list),
                    'primary_role': max(jobs_list, key=lambda x: x['score'])['job']
                }
                for name, jobs_list in sorted(
                    overlapping.items(),
                    key=lambda x: len(x[1]),
                    reverse=True
                )[:10]
            ]
        }

    def _rank_hiring_priorities(self, results):
        """Rank jobs by hiring priority based on pool strength."""
        priorities = []
        for job_key, data in results.items():
            avg_score = data.get('average_score', 0)
            total = data.get('total_candidates', 0)
            
            if avg_score >= 0.7 and total >= 3:
                priority = 'High - Strong pool available'
            elif avg_score >= 0.5 and total >= 2:
                priority = 'Medium - Adequate pool'
            elif total >= 1:
                priority = 'Low - Limited pool'
            else:
                priority = 'Critical - No candidates'
            
            priorities.append({
                'job': job_key,
                'average_score': round(avg_score * 100, 1),
                'total_candidates': total,
                'priority': priority,
                'recommendation': self._hiring_recommendation(avg_score, total)
            })
        
        priorities.sort(key=lambda x: x['average_score'], reverse=True)
        return priorities

    def _hiring_recommendation(self, avg_score, total):
        """Generate hiring recommendation for a job."""
        if avg_score >= 0.8 and total >= 3:
            return 'Proceed with interviews - strong candidates available'
        elif avg_score >= 0.6 and total >= 2:
            return 'Schedule interviews - good candidate quality'
        elif avg_score >= 0.4 and total >= 1:
            return 'Consider expanding search for better options'
        else:
            return 'Re-evaluate job requirements or source more candidates'

    def _generate_multi_job_summary(self, results):
        """Generate executive summary for multi-job analysis."""
        total_jobs = len(results)
        total_candidates = sum(d['total_candidates'] for d in results.values())
        avg_scores = [d['average_score'] for d in results.values()]
        overall_avg = sum(avg_scores) / len(avg_scores) if avg_scores else 0
        
        best_job = max(results.items(), key=lambda x: x[1]['average_score'])
        weakest_job = min(results.items(), key=lambda x: x[1]['average_score'])
        
        return {
            'total_roles': total_jobs,
            'total_candidates_across_roles': total_candidates,
            'overall_average_score': round(overall_avg * 100, 1),
            'best_suited_role': best_job[0] if best_job else None,
            'best_suited_role_score': round(best_job[1]['average_score'] * 100, 1) if best_job else 0,
            'most_challenging_role': weakest_job[0] if weakest_job else None,
            'most_challenging_role_score': round(weakest_job[1]['average_score'] * 100, 1) if weakest_job else 0,
            'cross_role_insights': []
        }