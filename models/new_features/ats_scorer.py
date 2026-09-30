"""ATS Resume Scoring & Optimization Module - Evaluates resume ATS compatibility and provides optimization tips."""

import re
import logging

logger = logging.getLogger(__name__)


class ATSResumeScorer:
    """Scores resumes for ATS (Applicant Tracking System) compatibility and provides optimization tips."""

    def __init__(self):
        self.section_keywords = {
            'contact': ['email', 'phone', 'linkedin', 'github', 'portfolio', 'address'],
            'summary': ['summary', 'objective', 'profile', 'about me', 'professional summary'],
            'experience': ['experience', 'work history', 'employment', 'work experience', 'professional experience'],
            'education': ['education', 'academic', 'degree', 'university', 'college', 'school', 'bachelor', 'master', 'phd'],
            'skills': ['skills', 'technical skills', 'core competencies', 'expertise', 'technologies'],
            'projects': ['projects', 'project experience', 'key projects', 'personal projects'],
            'certifications': ['certifications', 'certificates', 'licenses', 'credentials'],
            'achievements': ['achievements', 'awards', 'honors', 'publications', 'patents']
        }
        self.action_verbs = [
            'achieved', 'improved', 'trained', 'managed', 'created', 'developed', 'led', 'increased',
            'decreased', 'reduced', 'delivered', 'implemented', 'designed', 'launched', 'established',
            'generated', 'optimized', 'transformed', 'built', 'spearheaded', 'oversaw', 'coordinated',
            'directed', 'produced', 'conducted', 'performed', 'executed', 'facilitated', 'negotiated',
            'resolved', 'strengthened', 'consolidated', 'customized', 'accelerated', 'pioneered'
        ]

    def score_resume(self, profile, full_text=''):
        """
        Score a resume for ATS compatibility.
        
        Args:
            profile: Candidate profile dict from parser
            full_text: Full resume text
            
        Returns:
            dict: ATS score with detailed breakdown and optimization tips
        """
        score = 0
        max_score = 100
        findings = []
        tips = []
        
        # 1. Section Completeness (25 points)
        section_score, section_findings, section_tips = self._check_sections(profile)
        score += section_score
        findings.extend(section_findings)
        tips.extend(section_tips)
        
        # 2. Keyword Density & Relevance (20 points)
        keyword_score, keyword_findings, keyword_tips = self._check_keywords(profile, full_text)
        score += keyword_score
        findings.extend(keyword_findings)
        tips.extend(keyword_tips)
        
        # 3. Action Verbs & Achievements (15 points)
        action_score, action_findings, action_tips = self._check_action_verbs(profile, full_text)
        score += action_score
        findings.extend(action_findings)
        tips.extend(action_tips)
        
        # 4. Quantifiable Impact (15 points)
        quant_score, quant_findings, quant_tips = self._check_quantifiable(profile, full_text)
        score += quant_score
        findings.extend(quant_findings)
        tips.extend(quant_tips)
        
        # 5. Formatting & Length (10 points)
        format_score, format_findings, format_tips = self._check_format(full_text)
        score += format_score
        findings.extend(format_findings)
        tips.extend(format_tips)
        
        # 6. Contact Info Completeness (10 points)
        contact_score, contact_findings, contact_tips = self._check_contact(profile, full_text)
        score += contact_score
        findings.extend(contact_findings)
        tips.extend(contact_tips)
        
        # 7. Customization & Tailoring (5 points)
        custom_score, custom_findings, custom_tips = self._check_customization(profile)
        score += custom_score
        findings.extend(custom_findings)
        tips.extend(custom_tips)
        
        score = min(score, max_score)
        
        # Determine ATS compatibility level
        if score >= 80:
            level = 'Excellent'
            description = 'Highly ATS-compatible resume. Strong optimization.'
        elif score >= 65:
            level = 'Good'
            description = 'Well-optimized with minor improvements possible.'
        elif score >= 50:
            level = 'Average'
            description = 'Moderate ATS compatibility. Several improvements recommended.'
        elif score >= 35:
            level = 'Below Average'
            description = 'Significant optimization needed for ATS systems.'
        else:
            level = 'Poor'
            description = 'Major restructuring needed for ATS compatibility.'
        
        return {
            'ats_score': score,
            'max_score': max_score,
            'ats_level': level,
            'description': description,
            'section_completeness': min(section_score, 25),
            'keyword_optimization': min(keyword_score, 20),
            'action_verbs_usage': min(action_score, 15),
            'quantifiable_impact': min(quant_score, 15),
            'formatting_quality': min(format_score, 10),
            'contact_info': min(contact_score, 10),
            'customization': min(custom_score, 5),
            'findings': findings[:5],
            'optimization_tips': tips[:8],
            'recommended_format': 'PDF (preferred for ATS)',
            'file_format_warning': 'Avoid images, tables, and graphics in resumes'
        }

    def _check_sections(self, profile):
        """Check for required resume sections."""
        score = 0
        findings = []
        tips = []
        
        required_sections = ['experience', 'education', 'skills']
        optional_sections = ['projects', 'certifications', 'achievements']
        
        has_exp = bool(profile.get('companies') or profile.get('experience_years', 0) > 0)
        has_edu = bool(profile.get('education'))
        has_skills = bool(profile.get('technical_skills'))
        has_projects = bool(profile.get('project_count', 0) > 0)
        has_certs = bool(profile.get('certifications'))
        
        if has_exp:
            score += 10
            findings.append('✅ Experience section present')
        else:
            tips.append('Add a detailed Work Experience section with job titles, companies, and dates')
            
        if has_edu:
            score += 8
            findings.append('✅ Education section present')
        else:
            tips.append('Include Education section with degrees, institutions, and graduation dates')
            
        if has_skills:
            score += 7
            findings.append('✅ Skills section present')
        else:
            tips.append('Add a dedicated Technical Skills section listing all relevant technologies')
            
        if has_projects:
            score += 3
            findings.append('✅ Projects section adds value')
        else:
            tips.append('Consider adding a Projects section to showcase practical work')
            
        if has_certs:
            score += 2
            findings.append('✅ Certifications listed')
            
        total_sections = sum([has_exp, has_edu, has_skills, has_projects, has_certs])
        if total_sections < 3:
            tips.append('Your resume is missing key sections. Include at least Experience, Education, and Skills.')
        
        return score, findings, tips

    def _check_keywords(self, profile, full_text):
        """Check keyword optimization."""
        score = 0
        findings = []
        tips = []
        
        text_lower = full_text.lower() if full_text else ''
        skills = [s.lower() for s in profile.get('technical_skills', [])]
        
        # Check if skills appear in resume text
        skill_mentions = 0
        for skill in skills:
            if skill in text_lower:
                skill_mentions += 1
        
        skill_coverage = skill_mentions / max(len(skills), 1)
        if skill_coverage >= 0.8:
            score += 12
            findings.append('✅ Strong keyword integration throughout resume')
        elif skill_coverage >= 0.5:
            score += 8
            findings.append('⚠️ Some skills missing from resume body text')
            tips.append('Integrate important skills naturally throughout experience descriptions, not just in skills section')
        else:
            score += 3
            tips.append('⚠️ Critical: Include key technical skills in work experience bullet points to improve keyword matching')
        
        # Check for industry buzzwords
        buzzwords = ['data-driven', 'cross-functional', 'agile', 'team player', 'results-oriented',
                     'stakeholder', 'scalable', 'pipeline', 'end-to-end', 'best practices']
        found_buzzwords = sum(1 for b in buzzwords if b in text_lower)
        if found_buzzwords >= 4:
            score += 8
            findings.append(f'✅ Good use of industry keywords ({found_buzzwords} found)')
        elif found_buzzwords >= 2:
            score += 4
            findings.append('⚠️ Moderate industry keyword usage')
            tips.append('Add more industry-relevant keywords like "data-driven", "cross-functional", "scalable"')
        else:
            tips.append('Add industry-standard keywords and phrases that match the job description')
        
        return score, findings, tips

    def _check_action_verbs(self, profile, full_text):
        """Check action verb usage."""
        score = 0
        findings = []
        tips = []
        
        text_lower = full_text.lower() if full_text else ''
        found_verbs = []
        
        for verb in self.action_verbs:
            if verb in text_lower:
                found_verbs.append(verb)
        
        count = len(found_verbs)
        if count >= 8:
            score += 15
            findings.append(f'✅ Excellent use of action verbs ({count} found)')
        elif count >= 5:
            score += 10
            findings.append(f'✅ Good action verb usage ({count} found)')
            tips.append('Start more bullet points with strong action verbs like "spearheaded", "pioneered", "accelerated"')
        elif count >= 3:
            score += 5
            findings.append('⚠️ Limited action verbs')
            tips.append('Begin each bullet point with a powerful action verb (e.g., "Developed", "Implemented", "Optimized")')
        else:
            tips.append('Critical: Use strong action verbs to start each experience bullet point')
        
        return score, findings, tips

    def _check_quantifiable(self, profile, full_text):
        """Check for quantifiable achievements."""
        score = 0
        findings = []
        tips = []
        
        text = full_text or profile.get('projects_summary', '') or ''
        
        # Look for numbers, percentages, dollar amounts
        number_patterns = [
            r'\d+%', r'\$\d+[kKmMbB]?', r'\d+x', r'\d+/\d+',
            r'increased by \d+', r'reduced by \d+', r'improved \d+',
            r'\d+ [a-z]+ users?', r'\d+ [a-z]+ customers?',
            r'\d+ [a-z]+ clients?', r'\d+ [a-z]+ projects?',
            r'\d+ [a-z]+ team'
        ]
        
        matches = 0
        for pattern in number_patterns:
            matches += len(re.findall(pattern, text, re.IGNORECASE))
        
        quant_count = profile.get('quantifiable_achievements', 0)
        total_quant = matches + quant_count
        
        if total_quant >= 5:
            score += 15
            findings.append(f'✅ Strong quantifiable achievements ({total_quant} metrics found)')
        elif total_quant >= 3:
            score += 10
            findings.append(f'✅ Good use of metrics ({total_quant} found)')
            tips.append('Add more specific numbers: "% improvement", "dollar amounts saved", "team size led"')
        elif total_quant >= 1:
            score += 5
            findings.append('⚠️ Some metrics present')
            tips.append('Quantify achievements with specific metrics: percentages, revenue impact, team sizes, time saved')
        else:
            tips.append('Critical: Add quantifiable results to experience bullet points (e.g., "Improved model accuracy by 15%")')
        
        return score, findings, tips

    def _check_format(self, full_text):
        """Check formatting quality."""
        score = 0
        findings = []
        tips = []
        
        if not full_text:
            return 3, findings, tips
        
        lines = full_text.split('\n')
        words = full_text.split()
        
        # Length check (ideal: 400-800 words)
        word_count = len(words)
        if 400 <= word_count <= 800:
            score += 4
            findings.append(f'✅ Resume length is ideal ({word_count} words)')
        elif word_count > 800:
            score += 2
            findings.append('⚠️ Resume is slightly long')
            tips.append('Consider trimming to 1-2 pages maximum for better ATS parsing')
        else:
            score += 1
            tips.append('Resume seems short. Aim for 400-800 words of quality content.')
        
        # Bullet point usage
        bullet_count = sum(1 for l in lines if l.strip().startswith(('•', '-', '*', '→')))
        if bullet_count >= 10:
            score += 3
            findings.append('✅ Good use of bullet points')
        elif bullet_count >= 5:
            score += 2
        else:
            tips.append('Use bullet points for experience entries - they are parsed better by ATS')
        
        # Line length (too long lines are bad for ATS)
        long_lines = sum(1 for l in lines if len(l) > 200)
        if long_lines < 3:
            score += 3
        else:
            tips.append('Keep lines under 200 characters for optimal ATS parsing')
        
        return score, findings, tips

    def _check_contact(self, profile, full_text):
        """Check contact information."""
        score = 0
        findings = []
        tips = []
        
        text_lower = full_text.lower() if full_text else ''
        
        # Email
        if re.search(r'[\w.+-]+@[\w-]+\.[\w.-]+', text_lower):
            score += 3
            findings.append('✅ Email address present')
        else:
            tips.append('Add a professional email address at the top of resume')
        
        # Phone
        if re.search(r'[\+\(]?[\d\-\(\s\)]{7,}', text_lower):
            score += 2
            findings.append('✅ Phone number present')
        else:
            tips.append('Include a contact phone number')
        
        # LinkedIn
        if 'linkedin' in text_lower:
            score += 3
            findings.append('✅ LinkedIn profile linked')
        else:
            tips.append('Add LinkedIn profile URL - critical for recruiter outreach')
        
        # GitHub/Portfolio
        if 'github' in text_lower or 'gitlab' in text_lower or 'bitbucket' in text_lower:
            score += 2
            findings.append('✅ GitHub/portfolio link present')
        else:
            tips.append('Include GitHub or portfolio link to showcase your work')
        
        return score, findings, tips

    def _check_customization(self, profile):
        """Check if resume appears customized."""
        score = 0
        findings = []
        tips = []
        
        skills_count = len(profile.get('technical_skills', []))
        soft_skills_count = len(profile.get('soft_skills', []))
        
        if skills_count >= 10:
            score += 2
        elif skills_count < 5:
            tips.append('Expand technical skills section with more relevant technologies')
        
        if soft_skills_count >= 3:
            score += 1
            findings.append('✅ Soft skills included')
        else:
            tips.append('Consider adding soft skills that match the job requirements')
        
        # Profile completeness
        completeness = profile.get('completeness_score', 0)
        if completeness >= 0.8:
            score += 2
            findings.append('✅ High profile completeness')
        elif completeness >= 0.5:
            score += 1
        else:
            tips.append('Complete all sections of your profile for maximum ATS score')
        
        return score, findings, tips


class ATSOptimizationEngine:
    """Provides ATS optimization recommendations based on job description match."""
    
    def __init__(self):
        self.ats_scorer = ATSResumeScorer()
    
    def optimize_for_job(self, profile, jd_skills, jd_profile):
        """
        Generate ATS optimization recommendations tailored to a specific job.
        
        Args:
            profile: Candidate profile
            jd_skills: Required skills from job description
            jd_profile: Full job description profile
            
        Returns:
            dict: Targeted optimization recommendations
        """
        # Get base ATS score
        ats_result = self.ats_scorer.score_resume(profile)
        
        # Find missing high-value keywords from JD
        missing_skills = []
        jd_skills_lower = [s.lower() for s in jd_skills]
        candidate_skills_lower = [s.lower() for s in profile.get('technical_skills', [])]
        
        for skill in jd_skills_lower:
            if skill not in candidate_skills_lower:
                missing_skills.append(skill)
        
        # Generate job-specific tips
        job_tips = []
        if missing_skills:
            job_tips.append(f"Add these missing keywords from the job description: {', '.join(missing_skills[:5])}")
        
        role = (jd_profile.get('role', '') or '').lower()
        if role:
            job_tips.append(f"Tailor your professional summary to highlight {role} experience")
        
        job_title = jd_profile.get('role', '')
        if job_title:
            job_tips.append(f"Ensure your current/past job titles are relevant to '{job_title}'")
        
        required_exp = jd_profile.get('experience_required', 0)
        candidate_exp = profile.get('experience_years', 0)
        if required_exp > 0 and candidate_exp < required_exp:
            job_tips.append(f"Highlight relevant internship, project, or academic experience to compensate for the {required_exp}+ year requirement")
        
        return {
            'ats_score': ats_result['ats_score'],
            'ats_level': ats_result['ats_level'],
            'general_tips': ats_result['optimization_tips'],
            'job_specific_tips': job_tips,
            'missing_keywords': missing_skills,
            'score_breakdown': {
                'section_completeness': ats_result['section_completeness'],
                'keyword_optimization': ats_result['keyword_optimization'],
                'action_verbs': ats_result['action_verbs_usage'],
                'quantifiable_impact': ats_result['quantifiable_impact'],
                'formatting': ats_result['formatting_quality'],
                'contact_info': ats_result['contact_info']
            }
        }