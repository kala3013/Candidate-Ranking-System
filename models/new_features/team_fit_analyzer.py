"""Team Fit Analysis Module - Evaluates behavioral and cultural fit for team compatibility."""

import logging

logger = logging.getLogger(__name__)


class TeamFitAnalyzer:
    """Analyzes candidate-team compatibility based on behavioral signals, work style, and team dynamics."""

    # Team culture archetypes
    TEAM_CULTURES = {
        'startup': {
            'traits': ['fast-paced', 'autonomous', 'cross-functional', 'adaptive', 'ownership'],
            'preferred_behaviors': ['leadership', 'initiative', 'versatility', 'problem-solving'],
            'description': 'Fast-moving environment requiring autonomy and versatility'
        },
        'enterprise': {
            'traits': ['structured', 'process-driven', 'collaborative', 'stable', 'scalable'],
            'preferred_behaviors': ['collaboration', 'documentation', 'mentorship', 'process'],
            'description': 'Structured environment with established processes and teams'
        },
        'research': {
            'traits': ['innovative', 'exploratory', 'analytical', 'rigorous', 'publication-driven'],
            'preferred_behaviors': ['research', 'publication', 'experimentation', 'deep-analysis'],
            'description': 'Research-focused environment emphasizing innovation and rigor'
        },
        'consulting': {
            'traits': ['client-facing', 'deadline-driven', 'results-oriented', 'dynamic', 'presentation'],
            'preferred_behaviors': ['communication', 'presentation', 'client-management', 'delivery'],
            'description': 'Client-focused environment with fast turnaround expectations'
        },
        'product': {
            'traits': ['user-centric', 'iterative', 'data-driven', 'collaborative', 'agile'],
            'preferred_behaviors': ['product-thinking', 'user-empathy', 'a/b-testing', 'cross-functional'],
            'description': 'Product-focused environment emphasizing user experience and iteration'
        }
    }

    # Work style dimensions
    WORK_STYLES = {
        'collaborative': ['team', 'collaboration', 'cross-functional', 'pair programming', 'group'],
        'independent': ['autonomous', 'self-starter', 'independent', 'ownership', 'self-directed'],
        'structured': ['process', 'methodology', 'agile', 'scrum', 'documentation', 'organized'],
        'flexible': ['adaptive', 'dynamic', 'fast-changing', 'flexible', 'versatile'],
        'analytical': ['analytical', 'data-driven', 'metrics', 'quantitative', 'research'],
        'creative': ['creative', 'innovative', 'design', 'novel', 'exploratory'],
    }

    def __init__(self):
        pass

    def analyze_team_fit(self, candidate_profile, team_culture='startup', team_skills=None):
        """
        Analyze how well a candidate fits a specific team culture.
        
        Args:
            candidate_profile: Candidate profile dict
            team_culture: Team culture type ('startup', 'enterprise', 'research', 'consulting', 'product')
            team_skills: List of skills the team currently has (for gap analysis)
            
        Returns:
            dict: Team fit analysis with scores and recommendations
        """
        culture = self.TEAM_CULTURES.get(team_culture, self.TEAM_CULTURES['startup'])
        behavioral = candidate_profile.get('behavioral_signals', {})
        skills = [s.lower() for s in candidate_profile.get('technical_skills', [])]
        soft_skills = [s.lower() for s in candidate_profile.get('soft_skills', [])]
        all_text = ' '.join([
            candidate_profile.get('projects_summary', '') or '',
            candidate_profile.get('full_text', '') or '',
            ' '.join(soft_skills)
        ]).lower()
        
        # 1. Behavioral Compatibility (40%)
        behavioral_fit = self._calculate_behavioral_fit(behavioral, culture, all_text)
        
        # 2. Work Style Alignment (30%)
        work_style_fit = self._calculate_work_style_fit(all_text, culture)
        
        # 3. Skill Complementarity (20%)
        skill_fit = self._calculate_skill_fit(skills, team_skills or [])
        
        # 4. Communication & Soft Skills (10%)
        comm_fit = self._calculate_communication_fit(soft_skills, behavioral, all_text)
        
        # Overall score
        overall = round(
            behavioral_fit['score'] * 0.40 +
            work_style_fit['score'] * 0.30 +
            skill_fit['score'] * 0.20 +
            comm_fit['score'] * 0.10
        )
        
        # Determine fit level
        if overall >= 80:
            fit_level = 'Excellent Fit'
            recommendation = 'Highly recommended for this team culture'
        elif overall >= 65:
            fit_level = 'Good Fit'
            recommendation = 'Good alignment with minor adjustments needed'
        elif overall >= 50:
            fit_level = 'Moderate Fit'
            recommendation = 'Adequate fit - consider onboarding support'
        else:
            fit_level = 'Needs Assessment'
            recommendation = 'May require significant adaptation to team culture'
        
        return {
            'overall_fit_score': overall,
            'fit_level': fit_level,
            'recommendation': recommendation,
            'team_culture': team_culture,
            'culture_description': culture['description'],
            'components': {
                'behavioral_compatibility': behavioral_fit,
                'work_style_alignment': work_style_fit,
                'skill_complementarity': skill_fit,
                'communication_fit': comm_fit
            },
            'strengths': self._identify_strengths(behavioral_fit, work_style_fit, skill_fit, comm_fit),
            'areas_for_development': self._identify_development_areas(behavioral_fit, work_style_fit, skill_fit, comm_fit),
            'integration_recommendations': self._integration_recommendations(overall, team_culture),
            'team_dynamics_contribution': self._team_dynamics_contribution(behavioral, skills)
        }

    def _calculate_behavioral_fit(self, behavioral, culture, text):
        """Calculate behavioral compatibility with team culture."""
        score = 0
        details = []
        
        preferred = culture['preferred_behaviors']
        matched = []
        
        for behavior in preferred:
            count_key = f'{behavior}_count'
            if count_key in behavioral and behavioral[count_key] > 0:
                matched.append(behavior)
                score += 20
                details.append(f'Demonstrates {behavior.replace("-", " ")}')
            elif behavior.replace('-', ' ') in text:
                score += 10
                matched.append(behavior)
                details.append(f'Mentions {behavior.replace("-", " ")}')
        
        # Leadership bonus
        if behavioral.get('leadership_count', 0) > 0 and 'leadership' in preferred:
            score += 10
            details.append('Leadership experience valued in this culture')
        
        # Impact evidence
        if behavioral.get('impact_count', 0) > 0:
            score += 5
            details.append('Quantifiable impact orientation')
        
        score = min(score, 100)
        
        return {
            'score': score,
            'matched_behaviors': matched,
            'details': details,
            'assessment': 'Strong behavioral alignment' if score >= 70 else 'Partial behavioral alignment' if score >= 40 else 'Limited behavioral alignment'
        }

    def _calculate_work_style_fit(self, text, culture):
        """Calculate work style alignment."""
        score = 0
        details = []
        matched_styles = []
        
        culture_traits = set(culture['traits'])
        
        for style, keywords in self.WORK_STYLES.items():
            if any(kw in text for kw in keywords):
                matched_styles.append(style)
                # Check if this style matches culture traits
                if style in culture_traits or any(t in style for t in culture_traits):
                    score += 25
                    details.append(f'{style.title()} work style aligns with team culture')
                else:
                    score += 10
                    details.append(f'{style.title()} work style present')
        
        # Versatility bonus
        if len(matched_styles) >= 3:
            score += 10
            details.append('Versatile work style adaptable to different situations')
        
        score = min(score, 100)
        
        return {
            'score': score,
            'matched_styles': matched_styles,
            'details': details,
            'assessment': 'Strong work style alignment' if score >= 70 else 'Moderate alignment' if score >= 40 else 'Limited alignment'
        }

    def _calculate_skill_fit(self, candidate_skills, team_skills):
        """Calculate skill complementarity with existing team."""
        if not team_skills:
            return {'score': 50, 'details': ['No team skill data available for comparison'], 'complementary_skills': []}
        
        team_set = set(s.lower() for s in team_skills)
        candidate_set = set(candidate_skills)
        
        overlapping = candidate_set & team_set
        complementary = candidate_set - team_set
        
        # Score based on complementary value
        overlap_pct = len(overlapping) / max(len(team_set), 1)
        complement_pct = len(complementary) / max(len(candidate_set), 1)
        
        # Ideal: some overlap (for collaboration) + unique skills (for value add)
        if 0.2 <= overlap_pct <= 0.6 and complement_pct >= 0.3:
            score = 85
            assessment = 'Excellent skill complementarity'
        elif overlap_pct > 0.6:
            score = 60
            assessment = 'Good overlap but limited new skill addition'
        elif complement_pct > 0.5:
            score = 75
            assessment = 'Brings many new skills to the team'
        else:
            score = 40
            assessment = 'Limited skill synergy with existing team'
        
        return {
            'score': score,
            'overlapping_skills': list(overlapping)[:5],
            'complementary_skills': list(complementary)[:5],
            'assessment': assessment,
            'details': [
                f'{len(overlapping)} overlapping skills for collaboration',
                f'{len(complementary)} complementary skills for team expansion'
            ]
        }

    def _calculate_communication_fit(self, soft_skills, behavioral, text):
        """Calculate communication and soft skills fit."""
        score = 0
        details = []
        
        comm_keywords = ['communication', 'presentation', 'stakeholder', 'collaboration', 'teamwork',
                        'written', 'verbal', 'interpersonal', 'negotiation', 'client']
        
        matched_comm = [s for s in soft_skills if any(kw in s for kw in comm_keywords)]
        text_matches = sum(1 for kw in comm_keywords if kw in text)
        
        if matched_comm:
            score += 30
            details.append(f'Communication skills identified: {", ".join(matched_comm[:3])}')
        
        if text_matches >= 3:
            score += 20
            details.append('Strong communication signals in profile')
        elif text_matches >= 1:
            score += 10
        
        if behavioral.get('presentation_count', 0) > 0:
            score += 20
            details.append('Presentation experience demonstrates communication ability')
        
        if behavioral.get('leadership_count', 0) > 0:
            score += 15
            details.append('Leadership roles require strong communication')
        
        # Collaboration evidence
        if any('collaborat' in s for s in soft_skills) or 'collaborat' in text:
            score += 15
            details.append('Collaboration-oriented communication style')
        
        score = min(score, 100)
        
        return {
            'score': score,
            'details': details,
            'assessment': 'Strong communicator' if score >= 70 else 'Adequate communication skills' if score >= 40 else 'Communication development recommended'
        }

    def _identify_strengths(self, behavioral, work_style, skill, comm):
        """Identify top strengths for team fit."""
        strengths = []
        if behavioral['score'] >= 70:
            strengths.append('Strong behavioral alignment with team culture')
        if work_style['score'] >= 70:
            strengths.append('Work style naturally fits team dynamics')
        if skill['score'] >= 70:
            strengths.append('Brings valuable complementary skills to the team')
        if comm['score'] >= 70:
            strengths.append('Excellent communication and collaboration skills')
        if not strengths:
            strengths.append('Potential for growth with proper onboarding and support')
        return strengths

    def _identify_development_areas(self, behavioral, work_style, skill, comm):
        """Identify areas needing development."""
        areas = []
        if behavioral['score'] < 50:
            areas.append('May need time to adapt to team culture and norms')
        if work_style['score'] < 50:
            areas.append('Work style differences may require adjustment period')
        if skill['score'] < 50:
            areas.append('Skill gaps with existing team may need bridging')
        if comm['score'] < 50:
            areas.append('Communication style development recommended')
        return areas

    def _integration_recommendations(self, overall_score, team_culture):
        """Generate onboarding and integration recommendations."""
        recommendations = []
        
        if overall_score >= 80:
            recommendations.append('Fast-track onboarding - candidate is well-aligned with team culture')
            recommendations.append('Assign a mentor for technical domain knowledge transfer')
        elif overall_score >= 60:
            recommendations.append('Structured onboarding with clear culture orientation sessions')
            recommendations.append('Pair with team members for first 2 weeks for culture assimilation')
            recommendations.append('Regular check-ins during first month to address adaptation')
        else:
            recommendations.append('Extended onboarding program with culture buddy system')
            recommendations.append('Set clear expectations and provide frequent feedback')
            recommendations.append('Consider gradual responsibility increase during ramp-up')
        
        if team_culture == 'startup':
            recommendations.append('Emphasize ownership and autonomy expectations from day one')
        elif team_culture == 'enterprise':
            recommendations.append('Provide documentation and process orientation sessions')
        elif team_culture == 'research':
            recommendations.append('Allocate exploration time for research culture adaptation')
        
        return recommendations

    def _team_dynamics_contribution(self, behavioral, skills):
        """Analyze how candidate contributes to team dynamics."""
        contributions = []
        
        if behavioral.get('leadership_count', 0) > 0:
            contributions.append('Can mentor junior team members')
        if behavioral.get('publication_count', 0) > 0:
            contributions.append('Brings research and knowledge sharing orientation')
        if len(skills) >= 8:
            contributions.append('Versatile skill set enables cross-functional support')
        if behavioral.get('impact_count', 0) > 0:
            contributions.append('Results-driven approach can elevate team standards')
        
        if not contributions:
            contributions.append('Eager to learn and contribute to team goals')
        
        return contributions

    def compare_team_fits(self, candidates, team_culture='startup', team_skills=None):
        """Compare multiple candidates for team fit."""
        results = []
        for c in candidates:
            profile = c.get('profile', {})
            fit = self.analyze_team_fit(profile, team_culture, team_skills)
            results.append({
                'candidate_name': c.get('candidate_name', 'Unknown'),
                'candidate_id': c.get('candidate_id', ''),
                'overall_fit_score': fit['overall_fit_score'],
                'fit_level': fit['fit_level'],
                'recommendation': fit['recommendation'],
                'components': fit['components'],
                'strengths': fit['strengths']
            })
        
        results.sort(key=lambda x: x['overall_fit_score'], reverse=True)
        
        return {
            'team_culture': team_culture,
            'total_candidates': len(results),
            'ranked_fit': results,
            'top_candidate': results[0]['candidate_name'] if results else None,
            'top_fit_score': results[0]['overall_fit_score'] if results else 0
        }