"""Career Path Prediction Module - Predicts career trajectory and growth milestones for candidates."""

import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class CareerPathPredictor:
    """Predicts career progression paths, timelines, and milestones for candidates."""

    # Career progression paths for common roles
    CAREER_PATHS = {
        'data_scientist': [
            {'title': 'Junior Data Scientist', 'years': 0, 'skills': ['python', 'sql', 'statistics', 'machine learning']},
            {'title': 'Data Scientist', 'years': 2, 'skills': ['python', 'sql', 'machine learning', 'deep learning', 'nlp']},
            {'title': 'Senior Data Scientist', 'years': 5, 'skills': ['deep learning', 'nlp', 'mlops', 'cloud', 'leadership']},
            {'title': 'Lead Data Scientist', 'years': 8, 'skills': ['architecture', 'strategy', 'team management', 'mlops']},
            {'title': 'Principal Data Scientist', 'years': 12, 'skills': ['research', 'thought leadership', 'cross-functional']},
            {'title': 'Director of Data Science', 'years': 15, 'skills': ['executive', 'strategy', 'org building', 'vision']},
        ],
        'ml_engineer': [
            {'title': 'Junior ML Engineer', 'years': 0, 'skills': ['python', 'ml', 'sql', 'git']},
            {'title': 'ML Engineer', 'years': 2, 'skills': ['python', 'tensorflow', 'pytorch', 'mlops', 'docker']},
            {'title': 'Senior ML Engineer', 'years': 5, 'skills': ['mlops', 'kubernetes', 'distributed systems', 'cloud']},
            {'title': 'Lead ML Engineer', 'years': 8, 'skills': ['architecture', 'ml infrastructure', 'team lead']},
            {'title': 'Principal ML Engineer', 'years': 12, 'skills': ['research', 'platform design', 'mentorship']},
            {'title': 'Director of ML', 'years': 15, 'skills': ['strategy', 'org leadership', 'innovation']},
        ],
        'data_engineer': [
            {'title': 'Junior Data Engineer', 'years': 0, 'skills': ['sql', 'python', 'etl', 'data modeling']},
            {'title': 'Data Engineer', 'years': 2, 'skills': ['spark', 'airflow', 'cloud', 'data warehousing']},
            {'title': 'Senior Data Engineer', 'years': 5, 'skills': ['kafka', 'streaming', 'architecture', 'cloud infra']},
            {'title': 'Lead Data Engineer', 'years': 8, 'skills': ['data architecture', 'team lead', 'strategy']},
            {'title': 'Principal Data Engineer', 'years': 12, 'skills': ['platform design', 'data mesh', 'thought leadership']},
            {'title': 'Director of Data Engineering', 'years': 15, 'skills': ['org building', 'strategy', 'executive']},
        ],
        'software_engineer': [
            {'title': 'Junior Software Engineer', 'years': 0, 'skills': ['programming', 'algorithms', 'git', 'testing']},
            {'title': 'Software Engineer', 'years': 2, 'skills': ['system design', 'apis', 'databases', 'cloud']},
            {'title': 'Senior Software Engineer', 'years': 5, 'skills': ['architecture', 'scalability', 'mentorship', 'design patterns']},
            {'title': 'Staff Engineer', 'years': 8, 'skills': ['technical leadership', 'cross-team', 'innovation']},
            {'title': 'Principal Engineer', 'years': 12, 'skills': ['org-wide impact', 'strategy', 'thought leadership']},
            {'title': 'Engineering Director', 'years': 15, 'skills': ['executive', 'org building', 'vision']},
        ],
        'devops_engineer': [
            {'title': 'Junior DevOps Engineer', 'years': 0, 'skills': ['linux', 'scripting', 'ci/cd', 'docker']},
            {'title': 'DevOps Engineer', 'years': 2, 'skills': ['kubernetes', 'terraform', 'monitoring', 'cloud']},
            {'title': 'Senior DevOps Engineer', 'years': 5, 'skills': ['infrastructure', 'security', 'automation', 'sre']},
            {'title': 'Lead DevOps Engineer', 'years': 8, 'skills': ['platform engineering', 'team lead', 'strategy']},
            {'title': 'Principal DevOps Engineer', 'years': 12, 'skills': ['architecture', 'devops culture', 'innovation']},
            {'title': 'Director of Infrastructure', 'years': 15, 'skills': ['executive', 'org building', 'strategy']},
        ],
        'product_manager': [
            {'title': 'Associate Product Manager', 'years': 0, 'skills': ['analytics', 'user research', 'agile', 'communication']},
            {'title': 'Product Manager', 'years': 2, 'skills': ['strategy', 'roadmapping', 'stakeholder management', 'a/b testing']},
            {'title': 'Senior Product Manager', 'years': 5, 'skills': ['leadership', 'cross-functional', 'data-driven', 'mentorship']},
            {'title': 'Group Product Manager', 'years': 8, 'skills': ['portfolio management', 'team building', 'executive communication']},
            {'title': 'Director of Product', 'years': 12, 'skills': ['org leadership', 'vision', 'strategy', 'p&l']},
            {'title': 'VP of Product', 'years': 15, 'skills': ['executive', 'company strategy', 'board communication']},
        ],
    }

    # Skill acquisition timelines (years to learn)
    SKILL_ACQUISITION_TIME = {
        'python': 0.5, 'sql': 0.3, 'machine learning': 1.0, 'deep learning': 1.5,
        'nlp': 1.0, 'computer vision': 1.5, 'aws': 0.8, 'gcp': 0.8, 'azure': 0.8,
        'docker': 0.3, 'kubernetes': 0.8, 'terraform': 0.5, 'spark': 0.8,
        'kafka': 0.5, 'airflow': 0.5, 'mlops': 1.0, 'tensorflow': 0.8,
        'pytorch': 0.8, 'react': 0.8, 'typescript': 0.5, 'fastapi': 0.3,
        'leadership': 2.0, 'system design': 1.0, 'architecture': 1.5,
    }

    def __init__(self):
        pass

    def predict_career_path(self, profile, jd_profile=None):
        """
        Predict career path for a candidate.
        
        Args:
            profile: Candidate profile dict
            jd_profile: Job description profile (optional)
            
        Returns:
            dict: Career path prediction with milestones and timeline
        """
        experience = profile.get('experience_years', 0)
        skills = [s.lower() for s in profile.get('technical_skills', [])]
        education = profile.get('education', [])
        
        # Determine current role
        role = (jd_profile.get('role', '') if jd_profile else '') or 'data_scientist'
        role_key = self._normalize_role(role)
        
        # Get career path for role
        path = self.CAREER_PATHS.get(role_key, self.CAREER_PATHS['data_scientist'])
        
        # Find current position in path
        current_idx = 0
        for i, stage in enumerate(path):
            if experience >= stage['years']:
                current_idx = i
        
        current_stage = path[current_idx]
        
        # Calculate readiness for next role
        next_stages = []
        for i in range(current_idx + 1, len(path)):
            stage = path[i]
            years_to_reach = max(0, stage['years'] - experience)
            
            # Calculate skill readiness
            missing_skills = [s for s in stage['skills'] if s not in skills]
            skill_readiness = max(0, 1 - len(missing_skills) / max(len(stage['skills']), 1))
            
            # Calculate time to acquire missing skills
            time_to_acquire = sum(self.SKILL_ACQUISITION_TIME.get(s, 0.5) for s in missing_skills)
            
            # Total estimated time
            estimated_time = max(years_to_reach, time_to_acquire)
            
            next_stages.append({
                'title': stage['title'],
                'years_from_now': round(estimated_time, 1),
                'years_experience_needed': stage['years'],
                'skill_readiness': round(skill_readiness * 100, 1),
                'missing_skills': missing_skills,
                'time_to_acquire_skills': round(time_to_acquire, 1),
                'estimated_date': (datetime.now() + timedelta(days=estimated_time * 365)).strftime('%B %Y'),
                'readiness_level': 'High' if skill_readiness >= 0.7 else 'Medium' if skill_readiness >= 0.4 else 'Low'
            })
        
        # Generate skill development plan
        development_plan = self._generate_development_plan(skills, next_stages)
        
        # Career velocity score
        velocity = self._calculate_career_velocity(profile, current_idx, experience)
        
        # Alternative career paths
        alternatives = self._suggest_alternative_paths(profile, role_key)
        
        return {
            'current_role': current_stage['title'],
            'current_experience': experience,
            'career_path': path,
            'current_position': current_idx + 1,
            'total_stages': len(path),
            'next_stages': next_stages,
            'development_plan': development_plan,
            'career_velocity': velocity,
            'alternative_paths': alternatives,
            'skill_gaps_for_next_role': next_stages[0]['missing_skills'] if next_stages else [],
            'readiness_for_next_role': next_stages[0]['readiness_level'] if next_stages else 'N/A',
            'estimated_time_to_next_role': next_stages[0]['years_from_now'] if next_stages else 0,
            'long_term_projection': self._long_term_projection(next_stages, current_stage['title']),
            'learning_path': self._generate_learning_path(next_stages, skills)
        }

    def _normalize_role(self, role):
        """Normalize role string to career path keys."""
        role_lower = role.lower().strip()
        for key in self.CAREER_PATHS:
            if key in role_lower or role_lower in key:
                return key
        mappings = {
            'data scientist': 'data_scientist', 'data science': 'data_scientist',
            'ml engineer': 'ml_engineer', 'machine learning': 'ml_engineer',
            'data engineer': 'data_engineer', 'software engineer': 'software_engineer',
            'devops': 'devops_engineer', 'sre': 'devops_engineer',
            'product manager': 'product_manager',
        }
        for key, val in mappings.items():
            if key in role_lower:
                return val
        return 'data_scientist'

    def _generate_development_plan(self, current_skills, next_stages):
        """Generate a skill development plan."""
        plan = []
        for stage in next_stages[:3]:
            if stage['missing_skills']:
                plan.append({
                    'target_role': stage['title'],
                    'skills_to_learn': stage['missing_skills'],
                    'estimated_time': stage['time_to_acquire_skills'],
                    'priority': 'High' if stage['readiness_level'] == 'Low' else 'Medium',
                    'focus_areas': self._categorize_skills(stage['missing_skills'])
                })
        return plan

    def _categorize_skills(self, skills):
        """Categorize skills into focus areas."""
        categories = {
            'Cloud & Infrastructure': ['aws', 'azure', 'gcp', 'docker', 'kubernetes', 'terraform'],
            'ML & AI': ['machine learning', 'deep learning', 'nlp', 'computer vision', 'tensorflow', 'pytorch'],
            'Data Engineering': ['spark', 'kafka', 'airflow', 'hadoop', 'flink'],
            'Software Engineering': ['system design', 'architecture', 'design patterns', 'testing'],
            'Leadership': ['leadership', 'team management', 'mentorship', 'strategy'],
            'MLOps': ['mlops', 'mlflow', 'kubeflow', 'ci/cd'],
        }
        
        result = []
        for category, cat_skills in categories.items():
            matched = [s for s in skills if s in cat_skills]
            if matched:
                result.append({'category': category, 'skills': matched})
        return result

    def _calculate_career_velocity(self, profile, current_idx, experience):
        """Calculate career progression velocity."""
        score = 0
        factors = []
        
        # Skill acquisition rate
        skills = profile.get('technical_skills', [])
        if len(skills) >= 10:
            score += 30
            factors.append('rapid skill acquisition')
        elif len(skills) >= 6:
            score += 20
            factors.append('good skill diversity')
        
        # Certification pursuit
        certs = profile.get('certifications', [])
        if len(certs) >= 3:
            score += 20
            factors.append('active certification pursuit')
        elif len(certs) >= 1:
            score += 10
        
        # Education level
        education = profile.get('education', [])
        edu_text = ' '.join(education).lower() if education else ''
        if 'phd' in edu_text:
            score += 20
            factors.append('advanced degree')
        elif "master's" in edu_text:
            score += 10
        
        # Experience vs position
        if current_idx > 0 and experience > 0:
            progression_rate = current_idx / max(experience, 1)
            if progression_rate > 0.3:
                score += 20
                factors.append('fast career progression')
            elif progression_rate > 0.2:
                score += 10
        
        # Behavioral signals
        behavioral = profile.get('behavioral_signals', {})
        if behavioral.get('leadership_count', 0) > 0:
            score += 10
            factors.append('leadership demonstrated')
        if behavioral.get('publication_count', 0) > 0:
            score += 10
            factors.append('research contributions')
        
        score = min(score, 100)
        
        if score >= 75:
            level = 'Fast Track'
            description = 'Exceptional career growth trajectory'
        elif score >= 55:
            level = 'Steady Growth'
            description = 'Consistent career progression'
        elif score >= 35:
            level = 'Moderate'
            description = 'Average career progression pace'
        else:
            level = 'Early Stage'
            description = 'Building career foundation'
        
        return {
            'score': score,
            'level': level,
            'description': description,
            'factors': factors
        }

    def _suggest_alternative_paths(self, profile, current_role):
        """Suggest alternative career paths based on skills."""
        skills = [s.lower() for s in profile.get('technical_skills', [])]
        alternatives = []
        
        path_mappings = [
            ('ml_engineer', ['python', 'tensorflow', 'pytorch', 'ml', 'deep learning']),
            ('data_engineer', ['sql', 'spark', 'airflow', 'kafka', 'etl']),
            ('software_engineer', ['python', 'java', 'javascript', 'react', 'system design']),
            ('devops_engineer', ['docker', 'kubernetes', 'terraform', 'ci/cd', 'linux']),
            ('product_manager', ['analytics', 'communication', 'leadership', 'strategy']),
            ('ai_researcher', ['research', 'publication', 'deep learning', 'nlp', 'mathematics']),
        ]
        
        for path_key, required_skills in path_mappings:
            if path_key == current_role:
                continue
            match_count = sum(1 for s in required_skills if s in skills)
            match_pct = match_count / len(required_skills)
            if match_pct >= 0.4:
                path = self.CAREER_PATHS.get(path_key, [])
                alternatives.append({
                    'role': path_key.replace('_', ' ').title(),
                    'skill_match': round(match_pct * 100, 1),
                    'entry_title': path[0]['title'] if path else 'Entry Level',
                    'feasibility': 'High' if match_pct >= 0.7 else 'Medium' if match_pct >= 0.5 else 'Low'
                })
        
        return sorted(alternatives, key=lambda x: x['skill_match'], reverse=True)[:3]

    def _long_term_projection(self, next_stages, current_title):
        """Generate long-term career projection text."""
        if not next_stages:
            return f"Continue building expertise in {current_title} role"
        
        final_role = next_stages[-1]['title'] if next_stages else current_title
        total_time = sum(s['years_from_now'] for s in next_stages)
        
        return {
            'projected_final_role': final_role,
            'estimated_years_to_final': round(total_time, 1),
            'estimated_date': (datetime.now() + timedelta(days=total_time * 365)).strftime('%B %Y'),
            'milestones': [{'role': s['title'], 'by': s['estimated_date']} for s in next_stages]
        }

    def _generate_learning_path(self, next_stages, current_skills):
        """Generate a structured learning path."""
        if not next_stages:
            return []
        
        learning_path = []
        all_missing = []
        for stage in next_stages:
            for skill in stage['missing_skills']:
                if skill not in all_missing:
                    all_missing.append(skill)
        
        # Order by acquisition time (shortest first for quick wins)
        all_missing.sort(key=lambda s: self.SKILL_ACQUISITION_TIME.get(s, 0.5))
        
        for i, skill in enumerate(all_missing[:8]):
            time = self.SKILL_ACQUISITION_TIME.get(skill, 0.5)
            learning_path.append({
                'step': i + 1,
                'skill': skill,
                'estimated_time_months': round(time * 12, 1),
                'phase': 'Foundation' if i < 3 else 'Intermediate' if i < 6 else 'Advanced',
                'priority': 'High' if i < 3 else 'Medium'
            })
        
        return learning_path