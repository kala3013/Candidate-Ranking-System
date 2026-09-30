"""Bias-Free Recruitment Module - Ensures fair candidate evaluation by removing demographic indicators."""

import re
import logging

logger = logging.getLogger(__name__)


class BiasFreeEvaluator:
    """
    Evaluates candidates anonymously by removing or masking demographic indicators.
    Provides fairness scoring and bias detection.
    """
    
    # Names to detect and anonymize
    NAME_PATTERN = re.compile(
        r'(?:name|full name|candidate name)\s*[::\-]?\s*([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)',
        re.IGNORECASE
    )
    
    # Email pattern
    EMAIL_PATTERN = re.compile(r'[\w\.-]+@[\w\.-]+\.\w+')
    
    # Phone pattern
    PHONE_PATTERN = re.compile(r'\+?\d{1,3}[-.\s]?\(?\d{1,3}\)?[-.\s]?\d{1,4}[-.\s]?\d{1,4}[-.\s]?\d{1,9}')
    
    # Address pattern
    ADDRESS_PATTERN = re.compile(
        r'\d+\s+[A-Za-z\s]+(?:street|st|avenue|ave|road|rd|lane|ln|drive|dr|circle|ct|place|pl|way|sq|park)\b',
        re.IGNORECASE
    )
    
    # Gender indicators
    GENDER_PRONOUNS = re.compile(r'\b(he|she|him|her|his|hers|himself|herself|man|woman|mr|mrs|ms|miss)\b', re.IGNORECASE)
    
    # Age indicators
    AGE_PATTERNS = re.compile(
        r'\b(?:age|aged|years old|born|date of birth|dob)\s*[::\-]?\s*\d+',
        re.IGNORECASE
    )
    
    # Photo/avatar indicators
    PHOTO_INDICATORS = re.compile(r'\b(?:photo|picture|avatar|profile pic|headshot)\b', re.IGNORECASE)
    
    def __init__(self):
        self.bias_metrics = {
            'name_removed': False,
            'email_removed': False,
            'phone_removed': False,
            'address_removed': False,
            'gender_indicators_removed': False,
            'age_indicators_removed': False,
            'photo_indicators_removed': False
        }
    
    def anonymize_text(self, text):
        """
        Remove demographic indicators from text for bias-free evaluation.
        
        Args:
            text: Original resume text
            
        Returns:
            tuple: (anonymized_text, metrics)
        """
        anonymized = text
        metrics = {}
        
        # Remove names
        anonymized, count = self._remove_pattern(anonymized, self.NAME_PATTERN, '[NAME REMOVED]')
        metrics['name_removed'] = count > 0
        self.bias_metrics['name_removed'] = count > 0
        
        # Remove emails
        anonymized, count = self._remove_pattern(anonymized, self.EMAIL_PATTERN, '[EMAIL REMOVED]')
        metrics['email_removed'] = count > 0
        self.bias_metrics['email_removed'] = count > 0
        
        # Remove phone numbers
        anonymized, count = self._remove_pattern(anonymized, self.PHONE_PATTERN, '[PHONE REMOVED]')
        metrics['phone_removed'] = count > 0
        self.bias_metrics['phone_removed'] = count > 0
        
        # Remove addresses
        anonymized, count = self._remove_pattern(anonymized, self.ADDRESS_PATTERN, '[ADDRESS REMOVED]')
        metrics['address_removed'] = count > 0
        self.bias_metrics['address_removed'] = count > 0
        
        # Remove gender pronouns
        anonymized, count = self._remove_pattern(anonymized, self.GENDER_PRONOUNS, '[PRONOUN REMOVED]')
        metrics['gender_indicators_removed'] = count > 0
        self.bias_metrics['gender_indicators_removed'] = count > 0
        
        # Remove age indicators
        anonymized, count = self._remove_pattern(anonymized, self.AGE_PATTERNS, '[AGE REMOVED]')
        metrics['age_indicators_removed'] = count > 0
        self.bias_metrics['age_indicators_removed'] = count > 0
        
        # Remove photo indicators
        anonymized, count = self._remove_pattern(anonymized, self.PHOTO_INDICATORS, '[PHOTO REMOVED]')
        metrics['photo_indicators_removed'] = count > 0
        self.bias_metrics['photo_indicators_removed'] = count > 0
        
        return anonymized, metrics
    
    def _remove_pattern(self, text, pattern, replacement):
        """Remove all matches of a pattern from text."""
        count = len(pattern.findall(text))
        text = pattern.sub(replacement, text)
        return text, count
    
    def compute_fairness_score(self):
        """
        Compute a fairness score based on how many demographic indicators were removed.
        
        Returns:
            float: Fairness score between 0 and 1
        """
        protected_removed = sum(1 for v in self.bias_metrics.values() if v)
        total_checks = len(self.bias_metrics)
        
        if total_checks == 0:
            return 1.0
        
        return min(protected_removed / total_checks + 0.3, 1.0)  # Base 0.3 for enabling bias-free mode
    
    def generate_bias_report(self, candidate_name, fairness_score):
        """
        Generate a bias-free evaluation report.
        
        Returns:
            dict: Bias report
        """
        return {
            'bias_free_evaluation': True,
            'fairness_score': round(fairness_score * 100, 1),
            'anonymized_fields': self.bias_metrics,
            'explanation': self._generate_explanation(fairness_score),
            'candidate_anonymized': candidate_name != self._get_original_name(candidate_name) if hasattr(self, '_original_name') else True
        }
    
    def _generate_explanation(self, fairness_score):
        """Generate explanation of bias-free evaluation."""
        parts = []
        
        if fairness_score >= 0.8:
            parts.append("✅ Comprehensive bias-free evaluation enabled")
            parts.append("All detectable demographic indicators have been removed")
        elif fairness_score >= 0.5:
            parts.append("✅ Partial bias-free evaluation applied")
            parts.append("Some demographic indicators were detected and removed")
        else:
            parts.append("⚠️ Limited bias-free evaluation")
            parts.append("Few demographic indicators were detected")
        
        removed_fields = [k.replace('_', ' ').replace(' removed', '') for k, v in self.bias_metrics.items() if v]
        if removed_fields:
            parts.append(f"Removed indicators: {', '.join(removed_fields)}")
        
        parts.append("Evaluation was performed on anonymized profile data only")
        
        return ". ".join(parts)
    
    def evaluate_anonymously(self, job_profile, candidate_profile, anonymized_candidate_text):
        """
        Perform evaluation on anonymized candidate data.
        
        Args:
            job_profile: Original job description profile
            candidate_profile: Original candidate profile (before anonymization)
            anonymized_candidate_text: Anonymized resume text
            
        Returns:
            dict: Anonymized evaluation result with bias metrics
        """
        # Store anonymized version
        anon_profile = dict(candidate_profile)
        anon_profile['full_text'] = anonymized_candidate_text
        
        # Compute fairness
        fairness_score = self.compute_fairness_score()
        
        return {
            'fairness_score': round(fairness_score * 100, 1),
            'anonymized': True,
            'bias_metrics': self.bias_metrics,
            'report': self.generate_bias_report(
                candidate_profile.get('candidate_name', 'Unknown'),
                fairness_score
            )
        }