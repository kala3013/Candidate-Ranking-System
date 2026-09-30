"""Diversity Analytics Module - Analyzes diversity metrics across candidate pools."""

import logging
from collections import Counter

logger = logging.getLogger(__name__)


class DiversityAnalyzer:
    """Analyzes diversity metrics across a candidate pool."""

    # Gender-associated words for signal detection (soft indicators)
    MALE_SIGNALS = ['he', 'him', 'his', 'mr.', 'gentleman']
    FEMALE_SIGNALS = ['she', 'her', 'hers', 'ms.', 'mrs.', 'miss']
    NEUTRAL_SIGNALS = ['they', 'them', 'their', 'mx.']

    # University diversity indicators
    TIER_1_INDIA = ['iit', 'iisc', 'iiit', 'bits', 'nit', 'iim']
    TIER_2_INDIA = ['dtu', 'nsut', 'vit', 'srm', 'thapar', 'coep']
    INTERNATIONAL = ['harvard', 'mit', 'stanford', 'oxford', 'cambridge', 'eth', 'cmu', 'berkeley']

    # Skill diversity (different domain skills indicate cognitive diversity)
    DOMAIN_SKILLS = {
        'data_science': ['machine learning', 'deep learning', 'nlp', 'computer vision', 'statistics'],
        'engineering': ['system design', 'architecture', 'scalability', 'distributed systems'],
        'business': ['strategy', 'analytics', 'marketing', 'product', 'stakeholder'],
        'research': ['research', 'publication', 'experiment', 'hypothesis'],
        'creative': ['design', 'visualization', 'storytelling', 'communication'],
        'leadership': ['leadership', 'mentorship', 'team management', 'cross-functional'],
    }

    def __init__(self):
        pass

    def analyze_pool_diversity(self, candidates):
        """
        Analyze diversity metrics across the entire candidate pool.
        
        Args:
            candidates: List of ranked candidate dicts
            
        Returns:
            dict: Diversity analytics with scores and recommendations
        """
        total = len(candidates)
        if total == 0:
            return {'error': 'No candidates to analyze'}
        
        # Extract profiles
        profiles = []
        for c in candidates:
            p = c.get('profile', {})
            p['candidate_name'] = c.get('candidate_name', '')
            profiles.append(p)
        
        # Analyze educational diversity
        edu_diversity = self._analyze_educational_diversity(profiles)
        
        # Analyze skill diversity
        skill_diversity = self._analyze_skill_diversity(profiles)
        
        # Analyze experience diversity
        exp_diversity = self._analyze_experience_diversity(profiles)
        
        # Analyze domain diversity
        domain_diversity = self._analyze_domain_diversity(profiles)
        
        # Score diversity strength
        diversity_score, components = self._calculate_diversity_score(
            edu_diversity, skill_diversity, exp_diversity, domain_diversity
        )
        
        # Recommendations
        recommendations = self._generate_diversity_recommendations(
            diversity_score, components, total
        )
        
        return {
            'overall_diversity_score': diversity_score,
            'diversity_level': 'High' if diversity_score >= 75 else 'Medium' if diversity_score >= 50 else 'Low',
            'total_candidates': total,
            'components': components,
            'educational_diversity': edu_diversity,
            'skill_diversity': skill_diversity,
            'experience_diversity': exp_diversity,
            'domain_diversity': domain_diversity,
            'recommendations': recommendations,
            'diversity_insights': self._generate_insights(diversity_score, components, total),
            'fairness_metrics': {
                'score_distribution_balance': components.get('score_distribution', 'N/A'),
                'representation_balance': components.get('representation', 'N/A')
            }
        }

    def _analyze_educational_diversity(self, profiles):
        """Analyze educational background diversity."""
        universities = []
        degree_levels = []
        
        for p in profiles:
            edu = p.get('education', [])
            for e in edu:
                universities.append(e.lower() if e else '')
                for level in ['phd', "master's", "bachelor's", 'diploma', 'high school']:
                    if level in e.lower():
                        degree_levels.append(level)
                        break
        
        if not universities:
            return {'score': 0, 'unique_schools': 0, 'total_reported': 0}
        
        unique_schools = len(set(u for u in universities if u))
        tier1_count = sum(1 for u in universities if any(t in u for t in self.TIER_1_INDIA))
        tier2_count = sum(1 for u in universities if any(t in u for t in self.TIER_2_INDIA))
        international_count = sum(1 for u in universities if any(t in u for t in self.INTERNATIONAL))
        other_count = max(0, len([u for u in universities if u]) - tier1_count - tier2_count - international_count)
        
        degree_distribution = dict(Counter(degree_levels))
        
        score = min(unique_schools * 10, 50) + min(len(degree_distribution) * 15, 30) + 20
        score = min(score, 100)
        
        return {
            'score': score,
            'unique_universities': unique_schools,
            'tier_1_count': tier1_count,
            'tier_2_count': tier2_count,
            'international_count': international_count,
            'other_count': other_count,
            'degree_distribution': degree_distribution,
            'institution_types': {
                'tier_1_engineering': tier1_count,
                'international': international_count,
                'other_indian': other_count
            }
        }

    def _analyze_skill_diversity(self, profiles):
        """Analyze skill set diversity across candidates."""
        all_skills = []
        for p in profiles:
            all_skills.extend([s.lower() for s in p.get('technical_skills', [])])
        
        if not all_skills:
            return {'score': 0, 'unique_skills': 0}
        
        skill_counts = Counter(all_skills)
        unique_skills = len(skill_counts)
        total_skills = len(all_skills)
        
        # Check domain coverage
        domain_coverage = {}
        for domain, domain_skills in self.DOMAIN_SKILLS.items():
            matched = sum(1 for s in all_skills if any(ds in s for ds in domain_skills))
            domain_coverage[domain] = {
                'candidates_with_skills': matched,
                'coverage_pct': round(matched / max(len(profiles), 1) * 100, 1)
            }
        
        domains_covered = sum(1 for d in domain_coverage.values() if d['coverage_pct'] > 0)
        
        score = min(unique_skills * 2, 40) + min(domains_covered * 12, 50) + 10
        score = min(score, 100)
        
        return {
            'score': score,
            'unique_skills': unique_skills,
            'total_skill_mentions': total_skills,
            'domain_coverage': domain_coverage,
            'domains_covered': domains_covered,
            'top_skills': [{'skill': s, 'count': c} for s, c in skill_counts.most_common(5)],
            'rare_skills': [s for s, c in skill_counts.most_common() if c <= 1][:10]
        }

    def _analyze_experience_diversity(self, profiles):
        """Analyze experience level diversity."""
        exp_levels = {'entry': 0, 'mid': 0, 'senior': 0, 'lead': 0}
        company_counts = []
        
        for p in profiles:
            exp = p.get('experience_years', 0)
            if exp < 2:
                exp_levels['entry'] += 1
            elif exp < 5:
                exp_levels['mid'] += 1
            elif exp < 10:
                exp_levels['senior'] += 1
            else:
                exp_levels['lead'] += 1
            
            companies = p.get('companies', [])
            company_counts.extend(companies)
        
        total = max(sum(exp_levels.values()), 1)
        
        # Herfindahl Index for concentration (1 = perfectly diverse)
        herfindahl = sum((v / total) ** 2 for v in exp_levels.values())
        diversity_index = 1 - herfindahl  # Higher = more diverse
        
        total_companies = len(set(c.lower() for c in company_counts if c))
        
        score = round(diversity_index * 100)
        
        return {
            'score': score,
            'experience_distribution': exp_levels,
            'diversity_index': round(diversity_index, 3),
            'unique_companies_represented': total_companies,
            'largest_group': max(exp_levels, key=exp_levels.get),
            'largest_group_pct': round(max(exp_levels.values()) / total * 100, 1)
        }

    def _analyze_domain_diversity(self, profiles):
        """Analyze domain/industry diversity."""
        domains = []
        for p in profiles:
            domain = p.get('domain', '') or p.get('industry', '')
            if domain:
                domains.append(domain.lower())
        
        if not domains:
            # Infer from skills
            for p in profiles:
                skills = [s.lower() for s in p.get('technical_skills', [])]
                if any('finance' in s for s in skills):
                    domains.append('finance')
                elif any('health' in s for s in skills):
                    domains.append('healthcare')
                elif any('ecommerce' in s for s in skills):
                    domains.append('e-commerce')
                elif any('nlp' in s for s in skills):
                    domains.append('nlp/ai')
                else:
                    domains.append('general')
        
        unique_domains = len(set(domains))
        domain_dist = dict(Counter(domains))
        
        score = min(unique_domains * 20, 100)
        
        return {
            'score': score,
            'unique_domains': unique_domains,
            'domain_distribution': domain_dist,
            'primary_domain': domain_dist.most_common(1)[0][0] if domain_dist else 'General'
        }

    def _calculate_diversity_score(self, edu, skill, exp, domain):
        """Calculate overall diversity score."""
        components = {
            'educational_diversity': edu.get('score', 0),
            'skill_diversity': skill.get('score', 0),
            'experience_diversity': exp.get('score', 0),
            'domain_diversity': domain.get('score', 0),
        }
        
        weights = {'educational_diversity': 0.25, 'skill_diversity': 0.30, 
                   'experience_diversity': 0.25, 'domain_diversity': 0.20}
        
        score = sum(components[k] * weights[k] for k in weights)
        
        return round(score, 1), components

    def _generate_diversity_recommendations(self, score, components, total):
        """Generate diversity improvement recommendations."""
        recommendations = []
        
        if components.get('educational_diversity', 100) < 60:
            recommendations.append('Expand sourcing to include candidates from a wider range of universities and educational backgrounds')
        
        if components.get('skill_diversity', 100) < 60:
            recommendations.append('Look for candidates with complementary skill sets and cross-domain expertise')
        
        if components.get('experience_diversity', 100) < 60:
            recommendations.append('Consider mixing experience levels more evenly - early career and senior talent both add value')
        
        if components.get('domain_diversity', 100) < 60:
            recommendations.append('Source candidates from different industries to bring fresh perspectives')
        
        if not recommendations:
            recommendations.append('The candidate pool shows strong diversity across multiple dimensions')
        
        return recommendations

    def _generate_insights(self, score, components, total):
        """Generate high-level diversity insights."""
        insights = []
        
        if score >= 80:
            insights.append('Highly diverse candidate pool with broad representation')
        elif score >= 60:
            insights.append('Moderately diverse pool with room for improvement in some areas')
        else:
            insights.append('Limited diversity - consider broadening sourcing strategies')
        
        strongest = max(components, key=components.get)
        weakest = min(components, key=components.get)
        
        insights.append(f'Strongest dimension: {strongest.replace("_", " ").title()} ({components[strongest]}/100)')
        insights.append(f'Area for improvement: {weakest.replace("_", " ").title()} ({components[weakest]}/100)')
        
        return insights