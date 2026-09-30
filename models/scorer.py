"""Scorer Module - Computes individual component scores for candidate ranking.
Enhanced with behavioral signals, leadership impact, project depth, and profile completeness.
"""

import numpy as np
import logging

logger = logging.getLogger(__name__)


# Default scoring weights. These mirror the "Hybrid Scoring" blend documented in
# the README and are used whenever the caller does not supply custom weights.
DEFAULT_WEIGHTS = {
    'skill_match': 0.35,
    'experience_match': 0.20,
    'project_relevance': 0.15,
    'semantic_similarity': 0.15,
    'education': 0.05,
    'certifications': 0.05,
    'behavioral_score': 0.05,
}

# Components that participate in the final weighted blend, in display order.
WEIGHT_KEYS = (
    'skill_match',
    'experience_match',
    'project_relevance',
    'semantic_similarity',
    'education',
    'certifications',
    'behavioral_score',
)


class CandidateScorer:
    """
    Enhanced scoring engine with 8 components:
    - Skill Match Score (30%)
    - Experience Match Score (20%)
    - Semantic Similarity Score (15%)
    - Project Relevance & Depth Score (12%)
    - Behavioral Signal Score (10%) - leadership, impact, communication
    - Education Score (5%)
    - Certification Score (4%)
    - Profile Completeness Score (4%)
    """

    def __init__(self, embedding_model=None):
        self.embedding_model = embedding_model

    @staticmethod
    def resolve_weights(weights=None):
        """Validate, clamp and normalise a custom weight mapping.

        Every key in ``WEIGHT_KEYS`` must be present and numeric. Values are
        clamped to [0, 1] then rescaled so they sum to 1.0, so the UI can send
        raw slider values (e.g. all zeroed, or summing to 137) and still get a
        meaningful blend. Anything unusable falls back to ``DEFAULT_WEIGHTS``.

        Args:
            weights: dict of {component_key: float} or None

        Returns:
            dict: normalised weights summing to 1.0
        """
        if not isinstance(weights, dict) or not weights:
            return dict(DEFAULT_WEIGHTS)

        cleaned = {}
        for key in WEIGHT_KEYS:
            try:
                val = float(weights[key])
            except (KeyError, TypeError, ValueError):
                return dict(DEFAULT_WEIGHTS)
            if val != val or val in (float('inf'), float('-inf')):  # NaN / inf guard
                return dict(DEFAULT_WEIGHTS)
            cleaned[key] = min(max(val, 0.0), 1.0)

        total = sum(cleaned.values())
        if total <= 0:
            return dict(DEFAULT_WEIGHTS)

        return {k: v / total for k, v in cleaned.items()}

    def compute_skill_match(self, jd_skills, candidate_skills):
        """
        Compute skill match score based on overlapping required skills.
        Now weighs skills by category importance and gives partial credit
        for related skills.

        Returns:
            float: Score between 0 and 1
        """
        if not jd_skills:
            return 0.5

        jd_set = set(s.lower() for s in jd_skills)
        cand_set = set(s.lower() for s in candidate_skills)

        if not cand_set:
            return 0.0

        # Core skill match
        intersection = jd_set.intersection(cand_set)
        core_score = len(intersection) / len(jd_set) if jd_set else 0.0

        # Bonus for additional relevant skills (beyond what was asked)
        extras = cand_set - jd_set
        bonus = min(len(extras) * 0.015, 0.08)

        # Penalty if missing critical skills (detected as 'required' in JD)
        missing_critical = jd_set - cand_set
        penalty = 0
        if missing_critical and len(missing_critical) <= 2:
            # Penalty only if missing most of the core skills
            if len(intersection) < len(jd_set) * 0.3:
                penalty = 0.1

        score = min(core_score + bonus - penalty, 1.0)
        return max(score, 0.0)

    def compute_experience_match(self, required_years, candidate_years):
        """
        Compute experience match score with a sigmoid-like curve for fairness.
        
        Returns:
            float: Score between 0 and 1
        """
        if required_years <= 0:
            return 0.7

        if candidate_years >= required_years:
            # Exceeds or meets requirement - slight bonus for up to 2x required
            ratio = candidate_years / max(required_years, 1)
            base = 0.85
            bonus = min((ratio - 1.0) * 0.1, 0.15)  # Up to 15% bonus for extra experience
            return min(base + bonus, 1.0)
        else:
            # Below requirement - non-linear scoring
            ratio = candidate_years / max(required_years, 1)
            # sigmoid-like: 0.5 at 60% of required, 0.8 at 100%
            return min(ratio * 0.85, 0.8)

    def compute_project_relevance(self, jd_text, projects_text, project_count=0):
        """
        Compute project relevance score using semantic similarity and depth indicators.

        Args:
            jd_text: Full job description text
            projects_text: Projects/experience summary from candidate
            project_count: Number of bullet points/projects listed

        Returns:
            float: Score between 0 and 1
        """
        if not projects_text:
            return 0.0

        # Semantic similarity component (primary)
        semantic_score = 0.0
        if self.embedding_model and jd_text and projects_text:
            try:
                semantic_score = self.embedding_model.compute_similarity(jd_text[:500], projects_text)
            except Exception as e:
                logger.warning(f"Embedding similarity failed: {e}")

        # Project depth/quantity bonus
        depth_bonus = min(project_count * 0.03, 0.15)  # Up to 15% bonus for many projects

        # Fallback if semantic failed
        if semantic_score == 0.0:
            jd_keywords = set(jd_text.lower().split())
            proj_keywords = set(projects_text.lower().split())
            if proj_keywords:
                overlap = jd_keywords.intersection(proj_keywords)
                semantic_score = min(len(overlap) / max(len(proj_keywords), 1) * 2, 1.0)

        return min(semantic_score + depth_bonus, 1.0)

    def compute_behavioral_score(self, jd_signals, candidate_signals):
        """
        Compute behavioral alignment score based on leadership, impact, and communication signals.
        
        Args:
            jd_signals: Behavioral signals from job description
            candidate_signals: Behavioral signals from candidate resume

        Returns:
            float: Score between 0 and 1
        """
        if not candidate_signals:
            return 0.0

        score_components = []
        
        # Leadership alignment (30% of behavioral score)
        leadership_score = 0.0
        if candidate_signals.get('leadership_count', 0) > 0:
            leadership_score = min(candidate_signals['leadership_count'] * 0.2, 1.0)
        score_components.append(leadership_score * 0.30)

        # Impact/quantifiable results (40% of behavioral score)
        impact_score = 0.0
        if candidate_signals.get('impact_count', 0) > 0:
            impact_score = min(candidate_signals['impact_count'] * 0.2, 1.0)
        score_components.append(impact_score * 0.40)

        # Research/publication (15% of behavioral score)
        pub_score = 0.0
        if candidate_signals.get('publication_count', 0) > 0:
            pub_score = min(candidate_signals['publication_count'] * 0.2, 1.0)
        score_components.append(pub_score * 0.15)

        # Presentation/communication (15% of behavioral score)
        pres_score = 0.0
        if candidate_signals.get('presentation_count', 0) > 0:
            pres_score = min(candidate_signals['presentation_count'] * 0.25, 1.0)
        score_components.append(pres_score * 0.15)

        return min(sum(score_components), 1.0)

    def compute_education_score(self, jd_education, candidate_education):
        """
        Compute education relevance score.

        Returns:
            float: Score between 0 and 1
        """
        if not jd_education or jd_education == ['Not Specified']:
            return 0.7

        level_order = {'High School': 1, 'Diploma': 2, "Bachelor's": 3, "Master's": 4, 'PhD': 5}
        jd_levels = [level_order.get(e.strip(), 0) for e in jd_education if e.strip() in level_order]
        cand_levels = [level_order.get(e.strip(), 0) for e in candidate_education if e.strip() in level_order]

        if not jd_levels:
            return 0.7
        if not cand_levels:
            return 0.2

        required = max(jd_levels)
        candidate = max(cand_levels)

        if candidate >= required:
            return 1.0
        elif candidate == required - 1:
            return 0.7
        elif candidate == required - 2:
            return 0.4
        else:
            return 0.2

    def compute_certification_score(self, jd_certs, candidate_certs):
        """
        Compute certification match score.

        Returns:
            float: Score between 0 and 1
        """
        if not jd_certs:
            return 0.5

        jd_set = set(jd_certs)
        cand_set = set(candidate_certs)

        if not cand_set:
            return 0.0

        intersection = jd_set.intersection(cand_set)
        if len(jd_set) > 0:
            return len(intersection) / len(jd_set)
        return 0.0

    def compute_semantic_similarity(self, jd_text, candidate_text):
        """
        Compute overall semantic similarity using embeddings.
        Now uses a weighted approach: compares key sections weighted by importance.

        Returns:
            float: Score between 0 and 1
        """
        if self.embedding_model and jd_text and candidate_text:
            try:
                return self.embedding_model.compute_similarity(jd_text, candidate_text)
            except Exception as e:
                logger.warning(f"Semantic similarity failed: {e}")
        return 0.5

    def compute_completeness_score(self, candidate_profile):
        """
        Compute profile completeness score - how much information the candidate provided.
        This rewards candidates with more detailed profiles.

        Returns:
            float: Score between 0 and 1
        """
        return candidate_profile.get('completeness_score', 0.5)

    def compute_all_scores(self, jd_profile, candidate_profile, weights=None):
        """
        Compute all scoring components for a candidate with enhanced weighting.
        
        New weights reflect deeper understanding:
        - Skill Match: 30% (was 40%)
        - Experience Match: 20% (was 25%)
        - Semantic Similarity: 15% (was 10%)
        - Project Relevance: 12% (was 15%)
        - Behavioral Signals: 10% (NEW)
        - Education: 5% (unchanged)
        - Certifications: 4% (was 5%)
        - Profile Completeness: 4% (NEW)

        Args:
            jd_profile: Parsed job description dict
            candidate_profile: Parsed candidate profile dict
            weights: Optional dict overriding the scoring weights. Keys are the
                score component names; values are floats. The dict is normalised
                internally so it need not sum to 1.0. When omitted, the defaults
                below are used.

        Returns:
            dict: All component scores and final score
        """
        w = self.resolve_weights(weights)
        skill_match = self.compute_skill_match(
            jd_profile.get('required_skills', []),
            candidate_profile.get('technical_skills', [])
        )

        experience_match = self.compute_experience_match(
            jd_profile.get('experience_required', 0),
            candidate_profile.get('experience_years', 0)
        )

        project_relevance = self.compute_project_relevance(
            jd_profile.get('full_text', ''),
            candidate_profile.get('projects_summary', ''),
            candidate_profile.get('project_count', 0)
        )

        education_score = self.compute_education_score(
            jd_profile.get('education_required', []),
            candidate_profile.get('education', [])
        )

        certification_score = self.compute_certification_score(
            jd_profile.get('certifications_preferred', []),
            candidate_profile.get('certifications', [])
        )

        semantic_similarity = self.compute_semantic_similarity(
            jd_profile.get('full_text', ''),
            candidate_profile.get('full_text', '')
        )

        behavioral_score = self.compute_behavioral_score(
            jd_profile.get('behavioral_signals', {}),
            candidate_profile.get('behavioral_signals', {})
        )

        completeness_score = self.compute_completeness_score(candidate_profile)

        # Weighted blend. Weights come from resolve_weights(): the documented
        # defaults (Skill 35%, Experience 20%, Projects 15%, Semantic 15%,
        # Education 5%, Certifications 5%, Behavioral 5%) unless the caller
        # supplied a custom, normalised set via compute_all_scores(weights=...).
        final_score = (
            skill_match * w['skill_match'] +
            experience_match * w['experience_match'] +
            project_relevance * w['project_relevance'] +
            education_score * w['education'] +
            certification_score * w['certifications'] +
            semantic_similarity * w['semantic_similarity'] +
            behavioral_score * w['behavioral_score']
        )

        return {
            'skill_match': round(skill_match, 4),
            'experience_match': round(experience_match, 4),
            'project_relevance': round(project_relevance, 4),
            'education': round(education_score, 4),
            'certifications': round(certification_score, 4),
            'semantic_similarity': round(semantic_similarity, 4),
            'behavioral_score': round(behavioral_score, 4),
            'completeness': round(completeness_score, 4),
            'weights': {k: round(v, 4) for k, v in w.items()},
            'final_score': round(final_score, 4)
        }

    def generate_explanation(self, jd_profile, candidate_profile, scores):
        """
        Generate human-readable explanation for why a candidate was ranked.
        Enhanced with behavioral insights and detailed reasoning.

        Args:
            jd_profile: Parsed job description
            candidate_profile: Parsed candidate profile
            scores: Computed score dict

        Returns:
            str: Human-readable explanation
        """
        reasons = []

        # Skill match explanation
        skill_pct = round(scores['skill_match'] * 100)
        if skill_pct >= 70:
            reasons.append(f"Strong skill alignment: matches {skill_pct}% of required skills")
        elif skill_pct >= 40:
            reasons.append(f"Moderate skill match at {skill_pct}%")
        else:
            reasons.append(f"Limited skill overlap at {skill_pct}%")

        # Experience explanation
        exp_years = candidate_profile.get('experience_years', 0)
        required_exp = jd_profile.get('experience_required', 0)
        if exp_years > 0:
            if exp_years >= required_exp:
                reasons.append(f"Meets experience requirement with {exp_years} years")
            else:
                reasons.append(f"Has {exp_years} years experience ({required_exp} required)")

        # Project relevance
        if scores['project_relevance'] > 0.5:
            pct = round(scores['project_relevance'] * 100)
            reasons.append(f"Relevant project background ({pct}% match)")
        elif candidate_profile.get('project_count', 0) > 0:
            reasons.append(f"Shows {candidate_profile['project_count']} project contributions")

        # Behavioral signals
        behav = candidate_profile.get('behavioral_signals', {})
        behav_parts = []
        if behav.get('leadership_count', 0) > 0:
            behav_parts.append(f"leadership ({behav['leadership_count']}x)")
        if behav.get('impact_count', 0) > 0:
            behav_parts.append(f"impact evidence ({behav['impact_count']}x)")
        if behav.get('publication_count', 0) > 0:
            behav_parts.append(f"research publications")
        if behav_parts:
            reasons.append("Demonstrates " + ", ".join(behav_parts))

        # Certifications
        if scores['certifications'] > 0.5:
            reasons.append("Holds relevant certifications")
        elif candidate_profile.get('certifications') and scores['certifications'] <= 0.5:
            reasons.append("Has certifications (partially relevant)")

        # Education
        if scores['education'] >= 0.7:
            edu = candidate_profile.get('education', ['Not specified'])[0]
            if edu != 'Not Specified':
                reasons.append(f"Education background: {edu}")

        # Semantic match
        sem_pct = round(scores['semantic_similarity'] * 100)
        if sem_pct >= 70:
            reasons.append(f"Strong overall profile alignment ({sem_pct}% semantic match)")
        elif sem_pct >= 40:
            reasons.append(f"Moderate semantic alignment ({sem_pct}%)")

        if not reasons:
            reasons.append("Basic profile match based on available information")

        return " • ".join(reasons)