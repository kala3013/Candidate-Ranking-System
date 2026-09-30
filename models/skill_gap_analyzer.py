"""Skill Gap Analysis Module - Identifies strengths, missing skills, and learning recommendations."""

import logging

logger = logging.getLogger(__name__)

# Learning resource recommendations
LEARNING_RESOURCES = {
    'aws': [
        {'name': 'AWS Cloud Practitioner', 'provider': 'AWS', 'difficulty': 'Beginner', 'url': 'https://aws.amazon.com/certification/cloud-practitioner/'},
        {'name': 'AWS Solutions Architect', 'provider': 'AWS', 'difficulty': 'Intermediate', 'url': 'https://aws.amazon.com/certification/solutions-architect/'},
        {'name': 'AWS Certified Machine Learning', 'provider': 'AWS', 'difficulty': 'Advanced', 'url': 'https://aws.amazon.com/certification/machine-learning/'}
    ],
    'docker': [
        {'name': 'Docker for Beginners', 'provider': 'Docker', 'difficulty': 'Beginner', 'url': 'https://www.docker.com/101-tutorial/'},
        {'name': 'Docker Mastery', 'provider': 'Udemy', 'difficulty': 'Intermediate'}
    ],
    'kubernetes': [
        {'name': 'Kubernetes Fundamentals', 'provider': 'KodeKloud', 'difficulty': 'Beginner'},
        {'name': 'CKA Certification', 'provider': 'CNCF', 'difficulty': 'Advanced', 'url': 'https://www.cncf.io/certification/cka/'}
    ],
    'tensorflow': [
        {'name': 'TensorFlow Developer Certificate', 'provider': 'Google', 'difficulty': 'Intermediate', 'url': 'https://www.tensorflow.org/certificate'}
    ],
    'pytorch': [
        {'name': 'PyTorch for Deep Learning', 'provider': 'PyTorch', 'difficulty': 'Intermediate', 'url': 'https://pytorch.org/tutorials/'}
    ],
    'spark': [
        {'name': 'Apache Spark for Data Engineering', 'provider': 'Databricks', 'difficulty': 'Intermediate'},
        {'name': 'Spark with Python', 'provider': 'Udemy', 'difficulty': 'Beginner'}
    ],
    'mlops': [
        {'name': 'MLOps Fundamentals', 'provider': 'Google Cloud', 'difficulty': 'Intermediate'},
        {'name': 'MLflow Guide', 'provider': 'Databricks', 'difficulty': 'Intermediate'}
    ],
    'airflow': [
        {'name': 'Apache Airflow for Data Pipelines', 'provider': 'Astronomer', 'difficulty': 'Intermediate'}
    ],
    'deep learning': [
        {'name': 'Deep Learning Specialization', 'provider': 'DeepLearning.AI', 'difficulty': 'Intermediate', 'url': 'https://www.deeplearning.ai/courses/deep-learning-specialization/'}
    ],
    'nlp': [
        {'name': 'NLP with Transformers', 'provider': 'Hugging Face', 'difficulty': 'Intermediate', 'url': 'https://huggingface.co/learn/nlp-course'},
        {'name': 'Natural Language Processing Specialization', 'provider': 'DeepLearning.AI', 'difficulty': 'Intermediate'}
    ],
    'python': [
        {'name': 'Advanced Python', 'provider': 'Real Python', 'difficulty': 'Intermediate', 'url': 'https://realpython.com/'}
    ],
    'sql': [
        {'name': 'Advanced SQL', 'provider': 'Mode Analytics', 'difficulty': 'Intermediate', 'url': 'https://mode.com/sql-tutorial/'}
    ],
    'docker': [
        {'name': 'Docker & Kubernetes', 'provider': 'KodeKloud', 'difficulty': 'Intermediate'}
    ],
    'gcp': [
        {'name': 'Google Cloud Data Engineer', 'provider': 'Google', 'difficulty': 'Advanced', 'url': 'https://cloud.google.com/certification/data-engineer'}
    ],
    'azure': [
        {'name': 'Azure Data Scientist', 'provider': 'Microsoft', 'difficulty': 'Advanced', 'url': 'https://docs.microsoft.com/en-us/learn/certifications/azure-data-scientist/'}
    ],
    'kafka': [
        {'name': 'Apache Kafka Fundamentals', 'provider': 'Confluent', 'difficulty': 'Intermediate'}
    ]
}

# Default recommendations for common missing skills
DEFAULT_RECOMMENDATIONS = {
    'python': 'Take an Advanced Python course to deepen your programming skills',
    'sql': 'Practice advanced SQL queries and database optimization techniques',
    'machine learning': 'Complete a comprehensive ML course covering supervised and unsupervised learning',
    'deep learning': 'Start with Deep Learning Specialization by DeepLearning.AI',
    'nlp': 'Take the NLP with Transformers course by Hugging Face',
    'aws': 'Start with AWS Cloud Practitioner certification',
    'docker': 'Learn containerization with Docker for Beginners tutorial',
    'kubernetes': 'Get started with Kubernetes through KodeKloud fundamentals course',
    'spark': 'Learn Apache Spark for big data processing',
    'tensorflow': 'Get TensorFlow Developer Certificate',
    'pytorch': 'Master PyTorch for deep learning research',
    'mlops': 'Learn MLOps best practices and tools like MLflow',
    'airflow': 'Master Apache Airflow for workflow orchestration',
    'gcp': 'Get Google Cloud Data Engineer certification',
    'azure': 'Get Azure Data Scientist certification',
    'kafka': 'Learn Apache Kafka for real-time data streaming',
    'statistics': 'Strengthen your statistical analysis and hypothesis testing skills',
    'tableau': 'Master data visualization with Tableau',
    'power bi': 'Learn Power BI for business analytics',
    'git': 'Master version control with Git and GitHub',
    'linux': 'Learn Linux command line and shell scripting',
    'ci/cd': 'Implement CI/CD pipelines with Jenkins or GitHub Actions',
    'mongodb': 'Learn NoSQL database management with MongoDB',
    'redis': 'Master Redis for caching and real-time applications',
    'fastapi': 'Build modern APIs with FastAPI framework',
    'flask': 'Learn Flask for web application development',
    'react': 'Master React for frontend development',
    'generative ai': 'Explore generative AI and LLMs with practical projects',
    'llm': 'Learn about Large Language Models and prompt engineering',
    'rag': 'Build Retrieval-Augmented Generation systems',
    'langchain': 'Master LangChain for LLM application development'
}


class SkillGapAnalyzer:
    """Analyzes skill gaps between job requirements and candidate skills."""
    
    def __init__(self):
        pass
    
    def analyze_skill_gaps(self, jd_skills, candidate_skills, preferred_skills=None):
        """
        Analyze skill gaps between job description and candidate.
        
        Args:
            jd_skills: List of required skills from JD
            candidate_skills: List of candidate's technical skills
            preferred_skills: List of preferred/nice-to-have skills
            
        Returns:
            dict: Skill gap analysis with strengths, gaps, and recommendations
        """
        jd_set = set(s.lower() for s in jd_skills)
        cand_set = set(s.lower() for s in candidate_skills)
        
        if preferred_skills:
            preferred_set = set(s.lower() for s in preferred_skills)
        else:
            preferred_set = set()
        
        # Strengths: matching skills
        strengths = sorted(jd_set.intersection(cand_set))
        
        # Missing required skills
        missing_required = sorted(jd_set - cand_set)
        
        # Missing preferred skills
        missing_preferred = sorted(preferred_set - cand_set)
        
        # Extra skills candidate has beyond JD
        extra_skills = sorted(cand_set - jd_set - preferred_set)
        
        # Generate learning recommendations for each missing skill
        recommendations = []
        for skill in missing_required + missing_preferred:
            rec = self._get_recommendation(skill)
            if rec:
                recommendations.append(rec)
        
        # Calculate coverage
        total_required = len(jd_set)
        matched_count = len(strengths)
        coverage_pct = (matched_count / total_required * 100) if total_required > 0 else 0
        
        return {
            'strengths': strengths,
            'missing_required_skills': missing_required,
            'missing_preferred_skills': missing_preferred,
            'extra_skills': extra_skills,
            'skill_coverage_pct': round(coverage_pct, 1),
            'matched_skills_count': matched_count,
            'total_required_skills': total_required,
            'learning_recommendations': recommendations,
            'improvement_areas': self._categorize_improvement_areas(missing_required, missing_preferred)
        }
    
    def _get_recommendation(self, skill):
        """Get learning recommendation for a skill."""
        skill_lower = skill.lower()
        
        # Check exact match
        if skill_lower in LEARNING_RESOURCES:
            resources = LEARNING_RESOURCES[skill_lower]
            return {
                'skill': skill,
                'type': 'course',
                'recommendation': DEFAULT_RECOMMENDATIONS.get(skill_lower, f'Learn {skill.title()}'),
                'resources': resources[:2]
            }
        
        # Check partial match
        for key, resources in LEARNING_RESOURCES.items():
            if key in skill_lower or skill_lower in key:
                return {
                    'skill': skill,
                    'type': 'course',
                    'recommendation': DEFAULT_RECOMMENDATIONS.get(key, f'Learn {skill.title()}'),
                    'resources': resources[:2]
                }
        
        # Generic recommendation
        return {
            'skill': skill,
            'type': 'general',
            'recommendation': f'Consider learning {skill.title()} through online courses and hands-on projects',
            'resources': []
        }
    
    def _categorize_improvement_areas(self, missing_required, missing_preferred):
        """Categorize missing skills into improvement areas."""
        areas = []
        
        # Cloud & Infrastructure
        cloud_skills = {'aws', 'azure', 'gcp', 'docker', 'kubernetes', 'terraform', 'jenkins'}
        cloud_missing = [s for s in missing_required + missing_preferred if s in cloud_skills]
        if cloud_missing:
            areas.append({
                'area': 'Cloud & Infrastructure',
                'missing_skills': cloud_missing,
                'priority': 'High' if any(s in missing_required for s in cloud_missing) else 'Medium'
            })
        
        # Data Engineering
        data_skills = {'spark', 'kafka', 'airflow', 'hadoop', 'etl', 'sql'}
        data_missing = [s for s in missing_required + missing_preferred if s in data_skills]
        if data_missing:
            areas.append({
                'area': 'Data Engineering',
                'missing_skills': data_missing,
                'priority': 'High' if any(s in missing_required for s in data_missing) else 'Medium'
            })
        
        # AI/ML
        ai_skills = {'deep learning', 'nlp', 'computer vision', 'reinforcement learning', 'generative ai', 'llm', 'rag', 'transformers', 'bert', 'gpt'}
        ai_missing = [s for s in missing_required + missing_preferred if s in ai_skills]
        if ai_missing:
            areas.append({
                'area': 'AI & Machine Learning',
                'missing_skills': ai_missing,
                'priority': 'High' if any(s in missing_required for s in ai_missing) else 'Medium'
            })
        
        # MLOps
        mlops_skills = {'mlops', 'mlflow', 'kubeflow', 'ci/cd', 'model deployment'}
        mlops_missing = [s for s in missing_required + missing_preferred if s in mlops_skills]
        if mlops_missing:
            areas.append({
                'area': 'MLOps & Deployment',
                'missing_skills': mlops_missing,
                'priority': 'High' if any(s in missing_required for s in mlops_missing) else 'Medium'
            })
        
        # Programming & Tools
        prog_skills = {'python', 'java', 'c++', 'git', 'linux', 'docker', 'kubernetes', 'sql'}
        prog_missing = [s for s in missing_required + missing_preferred if s not in cloud_skills and s not in data_skills and s not in ai_skills and s not in mlops_skills and s in prog_skills]
        if prog_missing:
            areas.append({
                'area': 'Programming & Tools',
                'missing_skills': prog_missing,
                'priority': 'Medium'
            })
        
        return areas


class CandidatePotentialEngine:
    """Evaluates candidate potential beyond experience - focusing on growth trajectory and learning ability."""
    
    def __init__(self):
        pass
    
    def compute_potential(self, candidate_profile):
        """
        Compute candidate potential score based on non-experience factors.
        
        Factors:
        - Project quality & diversity
        - Certification count & relevance
        - Skill breadth & depth
        - Educational excellence
        - Career progression signals
        - Behavioral signals (leadership, impact, publications)
        
        Returns:
            dict: Potential analysis with scores and growth prediction
        """
        profile = candidate_profile
        
        # 1. Project Quality (30%)
        project_score = 0
        project_count = profile.get('project_count', 0)
        projects_text = profile.get('projects_summary', '')
        quant_achievements = profile.get('quantifiable_achievements', 0)
        
        if project_count > 0:
            project_score = min(project_count * 0.10, 0.5)
            if quant_achievements > 0:
                project_score += min(quant_achievements * 0.08, 0.3)
            if len(projects_text) > 100:
                project_score += 0.10
            if len(projects_text) > 300:
                project_score += 0.10
        project_score = min(project_score, 1.0) * 0.30
        
        # 2. Skill Breadth & Depth (25%)
        skill_score = 0
        skills = profile.get('technical_skills', [])
        if skills:
            skill_score += min(len(skills) * 0.04, 0.5)
        soft_skills = profile.get('soft_skills', [])
        if soft_skills:
            skill_score += min(len(soft_skills) * 0.05, 0.3)
        skill_score += 0.10  # Base for having any skills
        skill_score = min(skill_score, 1.0) * 0.25
        
        # 3. Certifications (15%)
        cert_score = 0
        certs = profile.get('certifications', [])
        if certs:
            cert_score = min(len(certs) * 0.25, 1.0)
        else:
            cert_score = 0.1  # Minimal score if no certs
        cert_score = cert_score * 0.15
        
        # 4. Educational Excellence (15%)
        edu_score = 0
        education = profile.get('education', [])
        edu_levels = {'High School': 1, 'Diploma': 2, "Bachelor's": 3, "Master's": 4, 'PhD': 5}
        max_level = 0
        for edu in education:
            level = edu_levels.get(edu.strip(), 0)
            max_level = max(max_level, level)
        
        if max_level >= 5:
            edu_score = 1.0
        elif max_level >= 4:
            edu_score = 0.8
        elif max_level >= 3:
            edu_score = 0.6
        elif max_level >= 2:
            edu_score = 0.4
        else:
            edu_score = 0.2
        edu_score = edu_score * 0.15
        
        # 5. Career Progression & Growth Signals (15%)
        growth_score = 0
        behavioral = profile.get('behavioral_signals', {})
        
        # Leadership signals indicate growth
        if behavioral.get('leadership_count', 0) > 0:
            growth_score += min(behavioral['leadership_count'] * 0.15, 0.4)
        
        # Publications show research capability
        if behavioral.get('publication_count', 0) > 0:
            growth_score += min(behavioral['publication_count'] * 0.15, 0.3)
        
        # Impact evidence shows real-world results
        if behavioral.get('impact_count', 0) > 0:
            growth_score += min(behavioral['impact_count'] * 0.10, 0.2)
        
        # Presentation/communication skills
        if behavioral.get('presentation_count', 0) > 0:
            growth_score += min(behavioral['presentation_count'] * 0.10, 0.1)
        
        growth_score = min(growth_score, 1.0) * 0.15
        
        # Calculate final potential score
        total_potential = project_score + skill_score + cert_score + edu_score + growth_score
        potential_pct = round(total_potential * 100, 1)
        
        # Determine growth probability
        growth_probability = self._calculate_growth_probability(potential_pct, profile)
        
        # Future skill acquisition prediction
        future_skills = self._predict_future_skills(profile)
        
        return {
            'potential_score': potential_pct,
            'project_quality_score': round(project_score / 0.30 * 100, 1) if project_score > 0 else 0,
            'skill_diversity_score': round(skill_score / 0.25 * 100, 1) if skill_score > 0 else 0,
            'certification_score': round(cert_score / 0.15 * 100, 1) if cert_score > 0 else 0,
            'education_excellence_score': round(edu_score / 0.15 * 100, 1) if edu_score > 0 else 0,
            'growth_trajectory_score': round(growth_score / 0.15 * 100, 1) if growth_score > 0 else 0,
            'future_growth_probability': growth_probability,
            'predicted_future_skills': future_skills,
            'explanation': self._generate_potential_explanation(potential_pct, growth_probability, profile)
        }
    
    def _calculate_growth_probability(self, potential_pct, profile):
        """Calculate probability of future growth."""
        factors = []
        
        # Potential score factor
        if potential_pct >= 80:
            factors.append(0.95)
        elif potential_pct >= 70:
            factors.append(0.85)
        elif potential_pct >= 60:
            factors.append(0.70)
        elif potential_pct >= 40:
            factors.append(0.50)
        else:
            factors.append(0.30)
        
        # Have publications (research orientation)
        behavioral = profile.get('behavioral_signals', {})
        if behavioral.get('publication_count', 0) > 0:
            factors.append(0.90)
        
        # Have leadership experience
        if behavioral.get('leadership_count', 0) > 0:
            factors.append(0.85)
        
        # Multiple companies (diverse experience)
        companies = profile.get('companies', [])
        if len(companies) >= 2:
            factors.append(0.80)
        
        # Advanced degree
        education = profile.get('education', [])
        if any('phd' in e.lower() or 'ph.d' in e.lower() for e in education):
            factors.append(0.90)
        elif any("master's" in e.lower() or 'm.tech' in e.lower() for e in education):
            factors.append(0.75)
        
        # Calculate probability
        if factors:
            probability = sum(factors) / len(factors)
        else:
            probability = 0.5
        
        if probability >= 0.8:
            return 'High'
        elif probability >= 0.5:
            return 'Medium'
        else:
            return 'Low'
    
    def _predict_future_skills(self, profile):
        """Predict skills the candidate is likely to acquire based on current profile."""
        current_skills = set(s.lower() for s in profile.get('technical_skills', []))
        predicted = []
        
        skill_paths = {
            'python': ['fastapi', 'django', 'pytest', 'airflow'],
            'tensorflow': ['tfx', 'tflite', 'mlops'],
            'pytorch': ['torchserve', 'lightning', 'onnx'],
            'aws': ['sagemaker', 'lambda', 'dynamodb', 'terraform'],
            'docker': ['kubernetes', 'helm', 'istio', 'docker-swarm'],
            'sql': ['postgresql', 'mysql', 'sqlalchemy', 'dbt'],
            'nlp': ['llm', 'rag', 'langchain', 'bert', 'gpt'],
            'machine learning': ['deep learning', 'mlops', 'feature-store'],
            'deep learning': ['transformers', 'generative-ai', 'rlhf'],
        }
        
        for skill, future_skills in skill_paths.items():
            if skill in current_skills:
                for fs in future_skills:
                    if fs not in current_skills:
                        predicted.append(fs)
        
        return predicted[:5]  # Return top 5 predictions
    
    def _generate_potential_explanation(self, potential_pct, growth_probability, profile):
        """Generate human-readable explanation for potential score."""
        parts = []
        
        if potential_pct >= 80:
            parts.append("Exceptional candidate with high growth potential")
        elif potential_pct >= 60:
            parts.append("Strong potential with room for advancement")
        elif potential_pct >= 40:
            parts.append("Moderate potential - showing positive growth trajectory")
        else:
            parts.append("Early stage career - significant development needed")
        
        behavioral = profile.get('behavioral_signals', {})
        if behavioral.get('publication_count', 0) > 0:
            parts.append(f"Published {behavioral['publication_count']} research works")
        if behavioral.get('leadership_count', 0) > 0:
            parts.append("Demonstrates leadership capability")
        
        skills = profile.get('technical_skills', [])
        if len(skills) >= 8:
            parts.append("Broad and diverse technical skill set")
        elif len(skills) >= 4:
            parts.append("Growing technical expertise")
        
        parts.append(f"Future growth probability: {growth_probability}")
        
        return ". ".join(parts)