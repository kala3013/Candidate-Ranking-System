"""AI Interview Question Generator - Generates personalized interview questions based on candidate profile."""

import logging

logger = logging.getLogger(__name__)


class InterviewQuestionGenerator:
    """Generates personalized interview questions based on job and candidate profiles."""
    
    def __init__(self):
        pass
    
    def generate_questions(self, jd_profile, candidate_profile, skill_gaps=None):
        """
        Generate personalized interview questions.
        
        Args:
            jd_profile: Parsed job description
            candidate_profile: Parsed candidate profile
            skill_gaps: Optional skill gap analysis results
            
        Returns:
            dict: Categorized interview questions
        """
        questions = {
            'technical_skills': self._generate_skill_questions(jd_profile, candidate_profile, skill_gaps),
            'project_discussion': self._generate_project_questions(candidate_profile),
            'experience_based': self._generate_experience_questions(candidate_profile, jd_profile),
            'behavioral': self._generate_behavioral_questions(candidate_profile),
            'skill_gap_probing': self._generate_skill_gap_questions(skill_gaps),
            'role_specific': self._generate_role_specific_questions(jd_profile, candidate_profile)
        }
        
        # Flatten to get total count
        all_questions = []
        for category, qs in questions.items():
            for q in qs:
                q['category'] = category.replace('_', ' ').title()
                all_questions.append(q)
        
        return {
            'categorized': questions,
            'all_questions': all_questions,
            'total_count': len(all_questions)
        }
    
    def _generate_skill_questions(self, jd_profile, candidate_profile, skill_gaps=None):
        """Generate technical skill assessment questions."""
        questions = []
        jd_skills = jd_profile.get('required_skills', [])
        candidate_skills = set(s.lower() for s in candidate_profile.get('technical_skills', []))
        
        # Questions for skills the candidate claims
        primary_skills = [s for s in jd_skills if s.lower() in candidate_skills]
        for skill in primary_skills[:5]:
            questions.append({
                'question': f"Can you describe your experience with {skill.title()} in production environments? Walk us through a specific project where you used it.",
                'focus': 'hands-on',
                'difficulty': 'intermediate'
            })
            questions.append({
                'question': f"What are the best practices for implementing {skill.title()} at scale? What challenges have you faced?",
                'focus': 'depth',
                'difficulty': 'advanced'
            })
        
        # Questions for skills the candidate is missing
        if skill_gaps:
            missing = skill_gaps.get('missing_required_skills', [])
            for skill in missing[:3]:
                questions.append({
                    'question': f"Do you have any experience with {skill.title()}? If not, how would you approach learning it for this role?",
                    'focus': 'adaptability',
                    'difficulty': 'beginner'
                })
        
        # Advanced concept questions
        advanced_topics = self._get_advanced_topics(jd_skills)
        for topic in advanced_topics[:2]:
            questions.append({
                'question': f"Can you explain your understanding of {topic}? How have you applied it in your work?",
                'focus': 'theoretical',
                'difficulty': 'advanced'
            })
        
        return questions
    
    def _generate_project_questions(self, candidate_profile):
        """Generate project discussion questions."""
        questions = []
        projects_text = candidate_profile.get('projects_summary', '')
        project_count = candidate_profile.get('project_count', 0)
        
        if projects_text:
            # Extract project descriptions
            project_lines = [l.strip() for l in projects_text.split('\n') if l.strip() and not l.strip().startswith(('Skills', 'Education'))]
            
            for i, proj in enumerate(project_lines[:4]):
                questions.append({
                    'question': f"Regarding the project: '{proj[:100]}...' — What was your specific role and contribution?",
                    'focus': 'ownership',
                    'difficulty': 'intermediate'
                })
                questions.append({
                    'question': f"What technical challenges did you face in this project and how did you overcome them?",
                    'focus': 'problem-solving',
                    'difficulty': 'intermediate'
                })
                questions.append({
                    'question': f"How did you measure the success/impact of this project? What metrics did you use?",
                    'focus': 'impact',
                    'difficulty': 'advanced'
                })
        
        # General project questions
        questions.append({
            'question': "Walk me through a project you're most proud of. What made it successful?",
            'focus': 'achievement',
            'difficulty': 'intermediate'
        })
        questions.append({
            'question': "Tell me about a project that failed or didn't meet expectations. What did you learn?",
            'focus': 'resilience',
            'difficulty': 'behavioral'
        })
        
        return questions
    
    def _generate_experience_questions(self, candidate_profile, jd_profile):
        """Generate experience-based questions."""
        questions = []
        exp_years = candidate_profile.get('experience_years', 0)
        required_exp = jd_profile.get('experience_required', 0)
        
        if exp_years > 0:
            questions.append({
                'question': "How has your role evolved over your career? Can you describe your career progression?",
                'focus': 'growth',
                'difficulty': 'behavioral'
            })
            
            if exp_years < required_exp:
                questions.append({
                    'question': f"With {exp_years} years of experience, how do you plan to compensate for the gap to meet the {required_exp}+ years this role typically requires?",
                    'focus': 'compensation',
                    'difficulty': 'challenging'
                })
            
            questions.append({
                'question': "Describe a situation where you had to work with cross-functional teams. How did you handle differing priorities?",
                'focus': 'collaboration',
                'difficulty': 'behavioral'
            })
            
            questions.append({
                'question': "What's the most complex technical problem you've solved professionally? Walk us through your approach.",
                'focus': 'technical-depth',
                'difficulty': 'advanced'
            })
        
        return questions
    
    def _generate_behavioral_questions(self, candidate_profile):
        """Generate behavioral and soft-skill questions."""
        base_questions = [
            {
                'question': "Tell me about a time you disagreed with a team member about a technical approach. How did you resolve it?",
                'focus': 'conflict-resolution',
                'difficulty': 'behavioral'
            },
            {
                'question': "Describe a situation where you had to learn a new technology quickly. How did you approach it?",
                'focus': 'learning-ability',
                'difficulty': 'behavioral'
            },
            {
                'question': "Tell me about a time you made a mistake in a project. How did you handle it?",
                'focus': 'accountability',
                'difficulty': 'behavioral'
            },
            {
                'question': "How do you stay updated with the latest developments in your field?",
                'focus': 'continuous-learning',
                'difficulty': 'cultural'
            },
            {
                'question': "Describe a situation where you mentored or helped a colleague grow professionally.",
                'focus': 'mentorship',
                'difficulty': 'behavioral'
            },
            {
                'question': "How do you handle tight deadlines and multiple priorities? Give a specific example.",
                'focus': 'time-management',
                'difficulty': 'behavioral'
            }
        ]
        
        # Customize based on profile
        soft_skills = candidate_profile.get('soft_skills', [])
        if 'leadership' in soft_skills:
            base_questions.append({
                'question': "You have demonstrated leadership skills. How do you adapt your leadership style for different team members?",
                'focus': 'leadership',
                'difficulty': 'advanced'
            })
        if 'communication' in soft_skills:
            base_questions.append({
                'question': "How do you communicate complex technical concepts to non-technical stakeholders?",
                'focus': 'communication',
                'difficulty': 'intermediate'
            })
        
        return base_questions
    
    def _generate_skill_gap_questions(self, skill_gaps):
        """Generate questions probing skill gaps."""
        questions = []
        if not skill_gaps:
            return questions
        
        missing = skill_gaps.get('missing_required_skills', [])
        preferred = skill_gaps.get('missing_preferred_skills', [])
        all_missing = missing + preferred
        
        for skill in all_missing[:4]:
            questions.append({
                'question': f"The role requires {skill.title()}. Do you have any exposure to it? How would you approach gaining proficiency?",
                'focus': 'skill-development',
                'difficulty': 'probing'
            })
        
        if missing:
            questions.append({
                'question': f"We notice you haven't listed {', '.join(missing[:3])} which are important for this role. Would you be willing to upskill in these areas?",
                'focus': 'upskilling',
                'difficulty': 'probing'
            })
        
        return questions
    
    def _generate_role_specific_questions(self, jd_profile, candidate_profile):
        """Generate role-specific and domain questions."""
        questions = []
        domain = jd_profile.get('domain', 'General')
        responsibilities = jd_profile.get('responsibilities', '')
        
        # Domain-specific questions
        questions.append({
            'question': f"What experience do you have in the {domain} domain? How does your background align?",
            'focus': 'domain-expertise',
            'difficulty': 'intermediate'
        })
        
        questions.append({
            'question': f"What do you think are the biggest challenges in {domain} today? How would you address them?",
            'focus': 'strategic-thinking',
            'difficulty': 'advanced'
        })
        
        # Responsibilities-based questions
        if responsibilities:
            key_areas = responsibilities.split('\n')[:3]
            for area in key_areas:
                if area.strip():
                    questions.append({
                        'question': f"The role involves: '{area[:100]}'. Can you describe your experience with this type of work?",
                        'focus': 'role-alignment',
                        'difficulty': 'intermediate'
                    })
        
        # Seniority level check
        questions.append({
            'question': "Where do you see yourself in 3-5 years? How does this role fit into your career trajectory?",
            'focus': 'career-alignment',
            'difficulty': 'cultural'
        })
        
        return questions
    
    def _get_advanced_topics(self, skills):
        """Generate advanced topic questions based on required skills."""
        topic_map = {
            'python': 'Python memory management and performance optimization',
            'machine learning': 'Bias-variance tradeoff and model selection strategies',
            'deep learning': 'Attention mechanisms and transformer architectures',
            'nlp': 'Modern NLP paradigms and transfer learning',
            'aws': 'Cloud architecture patterns and cost optimization',
            'docker': 'Container orchestration and microservices patterns',
            'kubernetes': 'Kubernetes scheduling and resource management',
            'sql': 'Query optimization and database indexing strategies',
            'spark': 'Spark execution plans and optimization techniques',
            'tensorflow': 'TensorFlow graph optimization and distributed training',
            'pytorch': 'PyTorch JIT compilation and custom CUDA kernels'
        }
        
        topics = []
        for skill in skills:
            skill_lower = skill.lower()
            if skill_lower in topic_map:
                topics.append(topic_map[skill_lower])
            # Check partial matches
            for key, topic in topic_map.items():
                if key in skill_lower or skill_lower in key:
                    if topic not in topics:
                        topics.append(topic)
        
        return topics[:5]