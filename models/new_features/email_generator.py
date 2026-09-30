"""Email Draft Generator Module - Creates recruiter email templates for candidate outreach."""

import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class EmailDraftGenerator:
    """Generates professional recruiter email drafts for various scenarios."""

    def __init__(self):
        pass

    def generate_interview_invite(self, candidate_name, role, company="Your Company"):
        """Generate interview invitation email."""
        return {
            'subject': f'Interview Invitation: {role} at {company}',
            'body': f'''Hi {candidate_name},

I hope this email finds you well!

We were impressed by your profile and the experience you bring, particularly in your work with data science and machine learning. After reviewing your background, we would love to invite you for an interview to discuss the {role} position at {company}.

Interview Details:
• Position: {role}
• Duration: 45-60 minutes
• Format: Video call (link will be shared upon confirmation)

Please let me know your availability over the next week, and I'll coordinate a time that works best for you.

Looking forward to speaking with you!

Best regards,
[Your Name]
Talent Acquisition Team
{company}''',
            'type': 'interview_invite',
            'tone': 'professional_warm'
        }

    def generate_offer_letter_draft(self, candidate_name, role, company="Your Company"):
        """Generate offer letter draft."""
        return {
            'subject': f'Offer Letter: {role} at {company}',
            'body': f'''Dear {candidate_name},

Congratulations! We are delighted to extend an offer for the position of {role} at {company}.

We were thoroughly impressed with your skills, experience, and enthusiasm throughout the interview process. We believe you will be a valuable addition to our team.

Position Details:
• Role: {role}
• Location: [Location]
• Start Date: [Start Date]

Attached is the official offer letter with complete terms and conditions, including compensation details, benefits, and other employment terms.

This offer is valid until [Offer Expiry Date]. To accept, please sign the attached offer letter and return it by the specified date.

Should you have any questions or need clarifications, please don't hesitate to reach out.

We look forward to welcoming you to the team!

Warm regards,
[Your Name]
[Your Title]
{company}''',
            'type': 'offer_letter',
            'tone': 'formal_celebratory'
        }

    def generate_rejection_email(self, candidate_name, role, company="Your Company"):
        """Generate rejection email with constructive feedback."""
        return {
            'subject': f'Update on your application for {role} at {company}',
            'body': f'''Dear {candidate_name},

Thank you for your interest in the {role} position at {company} and for taking the time to interview with us.

After careful consideration, we have decided to move forward with other candidates whose experience more closely matches our current requirements. This was a difficult decision, as we were impressed with many aspects of your background.

We encourage you to apply for future positions that match your skills and experience. We will keep your profile in our talent database for future opportunities.

We wish you all the best in your job search and future endeavors.

Best regards,
[Your Name]
Talent Acquisition Team
{company}''',
            'type': 'rejection',
            'tone': 'professional_respectful'
        }

    def generate_follow_up(self, candidate_name, role, company="Your Company"):
        """Generate follow-up email after interview."""
        return {
            'subject': f'Following up: {role} position at {company}',
            'body': f'''Hi {candidate_name},

I hope you're doing well! I wanted to follow up regarding your recent interview for the {role} position at {company}.

We really enjoyed learning more about your background and technical expertise. Your experience with [specific skill/project] was particularly impressive.

We are currently in the final stages of our evaluation process and expect to have an update for you within the next [timeframe].

In the meantime, please feel free to reach out if you have any questions about the role or our team.

Looking forward to being in touch soon!

Best regards,
[Your Name]
Talent Acquisition Team
{company}''',
            'type': 'follow_up',
            'tone': 'friendly_professional'
        }

    def generate_assessment_invite(self, candidate_name, role, company="Your Company"):
        """Generate technical assessment / take-home assignment email."""
        return {
            'subject': f'Technical Assessment: {role} at {company}',
            'body': f'''Hi {candidate_name},

Thanks for your interest in the {role} role at {company}!

As a next step in our hiring process, we'd like you to complete a technical assessment. This will help us better understand your problem-solving approach and technical capabilities.

Assessment Details:
• Duration: Approximately 2-3 hours
• Format: Take-home assignment
• Deadline: [Date, typically 5-7 days from now]

You will receive the assessment details in a separate email shortly. The assessment should be completed independently and submitted via [submission method].

If you have any questions about the process, feel free to reach out. We look forward to reviewing your work!

Best regards,
[Your Name]
Talent Acquisition Team
{company}''',
            'type': 'assessment',
            'tone': 'professional_encouraging'
        }

    def generate_custom_email(self, candidate_name, role, company, context, tone='professional'):
        """Generate a custom email based on context."""
        templates = {
            'screening': {
                'subject': f'Screening Call: {role} at {company}',
                'body': f'''Hi {candidate_name},

Thank you for applying to the {role} position at {company}.

We would like to schedule a brief screening call to learn more about your background and discuss the role in more detail. This will be a 15-20 minute conversation.

Please let me know your availability for a quick call this week.

Looking forward to connecting!

Best regards,
[Your Name]
Talent Acquisition Team
{company}'''
            },
            'references': {
                'subject': f'References Request: {role} at {company}',
                'body': f'''Hi {candidate_name},

Great speaking with you! We're moving forward in the process and would like to request professional references.

Could you please provide 2-3 references who can speak to your professional experience and skills? Please include their name, title, company, email, and phone number.

Thank you and looking forward to the next steps!

Best regards,
[Your Name]
Talent Acquisition Team
{company}'''
            },
            'hold': {
                'subject': f'Status Update: {role} position at {company}',
                'body': f'''Dear {candidate_name},

I wanted to provide a brief update on your application for the {role} position.

We are still in the process of evaluating candidates and your application remains under active consideration. We expect to have a decision within the next [timeframe].

We appreciate your patience and will keep you posted on any updates.

Best regards,
[Your Name]
Talent Acquisition Team
{company}'''
            }
        }
        
        template = templates.get(context, templates['screening'])
        return {
            'subject': template['subject'],
            'body': template['body'],
            'type': f'custom_{context}',
            'tone': tone
        }

    def bulk_generate_outreach(self, candidates, role, company="Your Company"):
        """Generate outreach emails for multiple candidates."""
        emails = []
        for candidate in candidates:
            name = candidate.get('candidate_name', candidate.get('name', 'Candidate'))
            email = self.generate_interview_invite(name, role, company)
            emails.append({
                'candidate_name': name,
                'candidate_id': candidate.get('candidate_id', ''),
                'email': email
            })
        return emails