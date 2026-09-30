"""Salary Prediction Module - AI-based salary range prediction for candidates."""

import logging
from statistics import median, mean

logger = logging.getLogger(__name__)


class SalaryPredictor:
    """Predicts salary ranges based on candidate profile, experience, skills, and market data."""

    # Industry salary benchmarks (annual INR in lakhs)
    SALARY_BENCHMARKS = {
        'data_scientist': {'entry': (6, 12), 'mid': (14, 25), 'senior': (28, 50), 'lead': (50, 80)},
        'ml_engineer': {'entry': (7, 14), 'mid': (15, 28), 'senior': (30, 55), 'lead': (55, 90)},
        'data_engineer': {'entry': (6, 12), 'mid': (13, 24), 'senior': (25, 45), 'lead': (45, 75)},
        'software_engineer': {'entry': (5, 12), 'mid': (14, 28), 'senior': (30, 50), 'lead': (50, 80)},
        'frontend_developer': {'entry': (4, 10), 'mid': (12, 22), 'senior': (24, 42), 'lead': (42, 70)},
        'backend_developer': {'entry': (5, 11), 'mid': (13, 24), 'senior': (26, 48), 'lead': (48, 78)},
        'fullstack_developer': {'entry': (5, 12), 'mid': (14, 25), 'senior': (27, 48), 'lead': (48, 78)},
        'devops_engineer': {'entry': (6, 14), 'mid': (15, 28), 'senior': (30, 50), 'lead': (50, 85)},
        'product_manager': {'entry': (8, 16), 'mid': (18, 35), 'senior': (38, 65), 'lead': (65, 100)},
        'data_analyst': {'entry': (4, 8), 'mid': (9, 16), 'senior': (18, 30), 'lead': (30, 50)},
        'business_analyst': {'entry': (4, 8), 'mid': (9, 15), 'senior': (16, 28), 'lead': (28, 45)},
        'ai_researcher': {'entry': (10, 20), 'mid': (22, 40), 'senior': (42, 70), 'lead': (70, 120)},
        'cloud_architect': {'entry': (12, 22), 'mid': (24, 42), 'senior': (45, 75), 'lead': (75, 120)},
    }

    # Skill premium adjustments (percentage increase for high-demand skills)
    SKILL_PREMIUMS = {
        'aws': 15, 'kubernetes': 12, 'tensorflow': 10, 'pytorch': 10,
        'spark': 10, 'kafka': 8, 'airflow': 8, 'docker': 8,
        'nlp': 12, 'llm': 20, 'generative ai': 20, 'rag': 15,
        'mlops': 12, 'terraform': 10, 'gcp': 10, 'azure': 10,
        'deep learning': 15, 'computer vision': 12, 'transformers': 12,
        'langchain': 15, 'fastapi': 5, 'react': 5, 'typescript': 5,
        'python': 3, 'sql': 2,
    }

    # Location adjustment factors (India base)
    LOCATION_FACTORS = {
        'bangalore': 1.15, 'bengaluru': 1.15, 'mumbai': 1.12, 'pune': 1.08,
        'hyderabad': 1.10, 'delhi': 1.12, 'noida': 1.05, 'gurgaon': 1.10,
        'chennai': 1.05, 'kolkata': 0.95, 'ahmedabad': 0.90, 'remote': 1.0,
        'international': 1.5, 'usa': 2.0, 'us': 2.0, 'uk': 1.6, 'europe': 1.5,
    }

    def __init__(self):
        pass

    def predict_salary(self, profile, jd_profile=None):
        """
        Predict salary range for a candidate.
        
        Args:
            profile: Candidate profile dict
            jd_profile: Job description profile (optional, for role-specific prediction)
            
        Returns:
            dict: Predicted salary range with confidence and breakdown
        """
        experience = profile.get('experience_years', 0)
        skills = [s.lower() for s in profile.get('technical_skills', [])]
        education = profile.get('education', [])
        certifications = profile.get('certifications', [])
        
        # Determine role level
        role = (jd_profile.get('role', '') if jd_profile else '') or 'data_scientist'
        role_key = self._normalize_role(role)
        
        # Determine seniority level
        level = self._determine_level(experience, skills, education)
        
        # Get base salary range for role and level
        base_range = self.SALARY_BENCHMARKS.get(role_key, self.SALARY_BENCHMARKS['data_scientist'])
        salary_range = base_range.get(level, base_range['mid'])
        base_min, base_max = salary_range
        
        # Apply skill premium
        skill_premium = self._calculate_skill_premium(skills)
        premium_min = base_min * (1 + skill_premium / 100)
        premium_max = base_max * (1 + skill_premium / 100)
        
        # Education adjustment
        edu_adjustment = self._calculate_education_adjustment(education)
        adj_min = premium_min * (1 + edu_adjustment)
        adj_max = premium_max * (1 + edu_adjustment)
        
        # Certification adjustment
        cert_adjustment = min(len(certifications) * 0.02, 0.10)
        final_min = adj_min * (1 + cert_adjustment)
        final_max = adj_max * (1 + cert_adjustment)
        
        # Experience precision within level
        exp_factor = 1.0
        if level == 'entry':
            exp_factor = 0.8 + (experience / 2) * 0.2 if experience > 0 else 0.8
        elif level == 'mid':
            exp_factor = 0.9 + ((experience - 3) / 4) * 0.1
        elif level == 'senior':
            exp_factor = 0.95 + ((experience - 7) / 5) * 0.05
        elif level == 'lead':
            exp_factor = 1.0 + ((experience - 12) / 5) * 0.1
        
        predicted_min = round(final_min * exp_factor)
        predicted_max = round(final_max * exp_factor)
        predicted_mid = round((predicted_min + predicted_max) / 2)
        
        # Determine confidence level
        confidence = self._calculate_confidence(profile, jd_profile)
        
        # Generate explanation
        explanation = self._generate_explanation(role.title(), level, experience, skill_premium, skills[:5])
        
        # Market context
        market_context = self._market_context(role_key, level)
        
        return {
            'predicted_range': {
                'min_lpa': predicted_min,
                'max_lpa': predicted_max,
                'midpoint_lpa': predicted_mid,
                'currency': 'INR Lakhs per annum',
            },
            'confidence': confidence,
            'level': level.capitalize(),
            'role': role.title(),
            'experience_years': experience,
            'skill_premium_applied': round(skill_premium, 1),
            'education_adjustment': round(edu_adjustment * 100, 1),
            'certification_adjustment': round(cert_adjustment * 100, 1),
            'breakdown': {
                'base_salary_range': f'₹{base_min}-{base_max} L/yr',
                'after_skill_premium': f'₹{round(premium_min)}-{round(premium_max)} L/yr',
                'after_experience': f'₹{predicted_min}-{predicted_max} L/yr',
            },
            'explanation': explanation,
            'market_context': market_context,
            'location_salary_range': None,  # Would need location data
            'percentile_estimate': {
                'p10': round(predicted_min * 0.85),
                'p50': predicted_mid,
                'p90': round(predicted_max * 1.15),
            }
        }

    def _normalize_role(self, role):
        """Normalize role string to benchmark keys."""
        role_lower = role.lower().strip()
        for key in self.SALARY_BENCHMARKS:
            if key in role_lower or role_lower in key:
                return key
        # Try common mappings
        mappings = {
            'data scientist': 'data_scientist', 'data science': 'data_scientist',
            'ml engineer': 'ml_engineer', 'machine learning': 'ml_engineer',
            'data engineer': 'data_engineer', 'software engineer': 'software_engineer',
            'frontend': 'frontend_developer', 'backend': 'backend_developer',
            'full stack': 'fullstack_developer', 'fullstack': 'fullstack_developer',
            'devops': 'devops_engineer', 'sre': 'devops_engineer',
            'product manager': 'product_manager', 'data analyst': 'data_analyst',
            'business analyst': 'business_analyst', 'business intelligence': 'business_analyst',
            'ai researcher': 'ai_researcher', 'ai research': 'ai_researcher',
            'cloud architect': 'cloud_architect',
        }
        for key, val in mappings.items():
            if key in role_lower:
                return val
        return 'data_scientist'

    def _determine_level(self, experience, skills, education):
        """Determine seniority level."""
        if experience >= 12:
            return 'lead'
        elif experience >= 7:
            return 'senior'
        elif experience >= 3:
            return 'mid'
        else:
            return 'entry'

    def _calculate_skill_premium(self, skills):
        """Calculate total skill premium percentage."""
        premium = 0
        matched_skills = set()
        for skill in skills:
            skill_lower = skill.lower()
            for key, pct in self.SKILL_PREMIUMS.items():
                if key in skill_lower or skill_lower in key:
                    if key not in matched_skills:
                        premium += pct * 0.7  # Weighted: not all skills are equally valued
                        matched_skills.add(key)
        return min(premium, 60)  # Cap at 60% premium

    def _calculate_education_adjustment(self, education):
        """Calculate salary adjustment based on education."""
        if not education:
            return 0
        
        edu_text = ' '.join(education).lower()
        if any(deg in edu_text for deg in ['phd', 'ph.d', 'doctorate']):
            return 0.15
        elif any(deg in edu_text for deg in ["master's", 'm.tech', 'msc', 'm.sc']):
            return 0.08
        elif any(deg in edu_text for deg in ['b.tech', "bachelor's", 'b.sc', 'be ']):
            return 0.03
        return 0

    def _calculate_confidence(self, profile, jd_profile):
        """Calculate confidence level of prediction."""
        confidence = 0
        factors = []
        
        # More data = higher confidence
        if profile.get('experience_years', 0) > 0:
            confidence += 20
            factors.append('experience data available')
        if len(profile.get('technical_skills', [])) >= 5:
            confidence += 15
            factors.append('sufficient skill data')
        if profile.get('education'):
            confidence += 10
            factors.append('education data available')
        if profile.get('certifications'):
            confidence += 5
            factors.append('certification data available')
        if jd_profile:
            confidence += 10
            factors.append('job role specified')
        
        # Experience range precision
        exp = profile.get('experience_years', 0)
        if 2 <= exp <= 10:
            confidence += 15
        elif exp > 10:
            confidence += 10
        else:
            confidence += 5
        
        confidence = min(confidence, 85) + 5  # Base 5% + capped at 85%
        
        if confidence >= 75:
            level = 'High'
        elif confidence >= 55:
            level = 'Medium'
        else:
            level = 'Low'
        
        return {'score': confidence, 'level': level, 'factors': factors}

    def _generate_explanation(self, role, level, experience, skill_premium, top_skills):
        """Generate human-readable salary explanation."""
        parts = []
        parts.append(f"Based on market data for {role} at {level} level")
        parts.append(f"with {experience} years of experience")
        
        if top_skills and skill_premium > 5:
            premium_skills = ', '.join(top_skills[:3])
            parts.append(f"Skills like {premium_skills} command a {skill_premium:.1f}% premium")
        
        if level in ['entry', 'mid']:
            parts.append("Significant growth potential in next 2-3 years")
        elif level == 'senior':
            parts.append("Competitive senior-level compensation reflecting deep expertise")
        
        return '. '.join(parts) + '.'

    def _market_context(self, role_key, level):
        """Provide market context for the prediction."""
        contexts = {
            'data_scientist': 'Demand for data scientists remains high with 20-30% YoY growth',
            'ml_engineer': 'ML engineering roles growing rapidly with MLOps becoming standard',
            'data_engineer': 'Data engineering salaries up 25% as real-time data becomes critical',
            'ai_researcher': 'AI research roles command premium due to generative AI boom',
        }
        return contexts.get(role_key, 'Competitive market with strong demand for technical talent')

    def compare_to_market(self, offered_salary, predicted):
        """Compare an offered salary to the predicted market range."""
        offered = offered_salary
        p_min = predicted['predicted_range']['min_lpa']
        p_max = predicted['predicted_range']['max_lpa']
        p_mid = predicted['predicted_range']['midpoint_lpa']
        
        if offered < p_min * 0.85:
            position = 'Below Market'
            assessment = 'Significantly below market rate. Candidate may decline.'
        elif offered < p_min:
            position = 'Slightly Below Market'
            assessment = 'Below typical range but within negotiation window.'
        elif offered <= p_max:
            position = 'At Market'
            assessment = 'Competitive offer aligned with market rates.'
        else:
            position = 'Above Market'
            assessment = 'Premium offer that is likely to be accepted.'
        
        diff_pct = round((offered - p_mid) / p_mid * 100, 1)
        
        return {
            'offered_salary': offered,
            'market_range': f'₹{p_min}-{p_max} L/yr',
            'market_midpoint': p_mid,
            'position': position,
            'assessment': assessment,
            'difference_from_market': f'{diff_pct:+.1f}%',
            'recommendation': 'Offer is competitive' if position in ['At Market', 'Above Market'] else 'Consider increasing offer'
        }