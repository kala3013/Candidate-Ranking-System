"""Recruiter Copilot - LLM-powered chat assistant for recruiter queries.
Provides intelligent answers about candidates, rankings, and hiring decisions."""

import re
import logging
from collections import Counter

logger = logging.getLogger(__name__)


class RecruiterCopilot:
    """
    AI-powered recruiter assistant that can answer questions about candidates.
    Uses pattern matching and ranking data to provide intelligent responses.
    """
    
    def __init__(self):
        self.conversation_history = []

    @staticmethod
    def _profile(candidate):
        """Return the sanitized profile dict for a ranked candidate.

        The API contract (see app.py::_process_and_return_results) exposes the
        parsed resume under the key ``profile``. Older builds emitted
        ``candidate_profile``, so both are accepted to stay backwards safe.
        """
        if not isinstance(candidate, dict):
            return {}
        prof = candidate.get('profile')
        if prof is None:
            prof = candidate.get('candidate_profile')
        return prof if isinstance(prof, dict) else {}

    @staticmethod
    def _score(candidate):
        """Return a candidate's final score as a float in [0, 1]."""
        try:
            return float(candidate.get('final_score') or 0)
        except (TypeError, ValueError):
            return 0.0

    @staticmethod
    def _name(candidate):
        """Return a candidate's display name."""
        return candidate.get('candidate_name') or 'Unknown Candidate'

    @staticmethod
    def _skills(candidate):
        """Return the candidate's technical skills as a lowercased list."""
        prof = RecruiterCopilot._profile(candidate)
        skills = prof.get('technical_skills') or []
        return [str(s).lower() for s in skills]

    def process_query(self, query, ranked_results, jd_profile):
        """
        Process a recruiter's natural language query about candidates.
        
        Args:
            query: Natural language question from recruiter
            ranked_results: List of ranked candidate results
            jd_profile: Parsed job description profile
            
        Returns:
            dict: Response with answer and context
        """
        query_lower = query.lower().strip()
        
        # Store in history
        self.conversation_history.append({'role': 'user', 'content': query})
        
        # Determine query type and generate response.
        # The safety net guarantees the API always returns a usable answer
        # instead of surfacing a raw 500 to the chat UI.
        try:
            response = self._classify_and_respond(query_lower, ranked_results, jd_profile)
        except Exception as exc:  # pragma: no cover - defensive
            logger.exception("Copilot failed to handle query %r: %s", query, exc)
            response = {
                'type': 'error',
                'answer': (
                    "🤔 I couldn't process that question just now. "
                    "Try rephrasing it, e.g. 'Show top 3 candidates' or 'Who should we hire?'"
                ),
                'error': str(exc)
            }
        
        self.conversation_history.append({'role': 'assistant', 'content': response['answer']})
        
        return response
    
    def _classify_and_respond(self, query, ranked_results, jd_profile):
        """Classify query type and generate appropriate response."""

        # NOTE: ordering matters. Broad "pool level" intents are tested BEFORE
        # the specific-candidate matcher, otherwise phrases like
        # "summarize the candidate pool" are captured by the
        # ``candidate\s+(\w+)`` pattern and answered with "candidate not found".

        # Check for comparison query
        if self._is_comparison_query(query):
            return self._handle_comparison(query, ranked_results)

        # Check for top candidates query
        if self._is_top_candidates_query(query):
            return self._handle_top_candidates(query, ranked_results)

        # Check for hiring recommendation
        if self._is_hiring_recommendation_query(query):
            return self._handle_hiring_recommendation(ranked_results, jd_profile)

        # Check for summary / overview query (BEFORE specific-candidate)
        if self._is_summary_query(query):
            return self._handle_summary(ranked_results, jd_profile)

        # Check for analytics/stats query
        if self._is_analytics_query(query):
            return self._handle_analytics(ranked_results)

        # Check for skill gap / missing skills query
        if self._is_missing_skills_query(query):
            return self._handle_missing_skills_query(query, ranked_results, jd_profile)

        # Check for skill-based query
        if self._is_skill_query(query):
            return self._handle_skill_query(query, ranked_results)

        # Check for specific candidate query (LAST - most greedy pattern)
        if self._is_specific_candidate_query(query):
            return self._handle_specific_candidate(query, ranked_results)

        # Default: general assistance
        return self._handle_general(ranked_results, jd_profile)
    
    def _is_comparison_query(self, query):
        """Check if query is about comparing candidates."""
        patterns = [
            r'compare\s+(candidate\s*[a-z0-9]|#?\d+)',
            r'difference\s+between',
            r'versus|vs\.?\s+',
            r'which\s+candidate\s+is\s+better',
            r'compare\s+(\w+\s+){0,2}and\s+(\w+\s+){0,2}'
        ]
        return any(re.search(p, query) for p in patterns)
    
    def _is_top_candidates_query(self, query):
        """Check if query is about top/ranked candidates."""
        patterns = [
            r'(?:show|list|find|get|who\s+are)\s+(?:the\s+)?(?:top|best|ranked|leading)',
            r'who\s+is\s+(?:the\s+)?(?:best|top|number\s+one)',
            r'(?:top|first)\s+\d+\s+candidates?',
            r'highest\s+(?:ranked|scoring|rated)'
        ]
        return any(re.search(p, query) for p in patterns)
    
    def _is_skill_query(self, query):
        """Check if query is about candidates with specific skills."""
        patterns = [
            r'(?:show|list|find|get)\s+candidates?\s+(?:with|having|who\s+know|skilled\s+in)',
            r'who\s+(?:has|have|knows)\s+.*(?:python|sql|aws|ml|nlp|docker|kubernetes|tensorflow)',
            r'candidates?\s+(?:with|having|skilled\s+in)\s+\w+'
        ]
        # Also check for skill name presence
        skills_pattern = r'\b(python|sql|aws|docker|kubernetes|tensorflow|pytorch|nlp|machine learning|deep learning|spark|kafka|tableau|power bi)\b'
        has_skill = re.search(skills_pattern, query, re.IGNORECASE)
        
        return any(re.search(p, query, re.IGNORECASE) for p in patterns) or (has_skill is not None and 'skill' in query)
    
    def _is_missing_skills_query(self, query):
        """Check if query is about candidates with skill gaps."""
        patterns = [
            r'(?:who|which\s+candidates?)\s+(?:lack|miss|don\'t\s+have|without|missing|is\s+missing)',
            r'skill\s+gaps?',
            r'missing\s+skills?',
            r'skills?\s+(?:is|are)\s+missing',
            r'(?:which|what)\s+skills?\s+(?:is|are)\s+missing\s+the\s+most',
            r'missing\s+the\s+most',
            r'lack(?:s|ing)?\s+the\s+most',
            r'candidates?\s+(?:lacking|missing|without)\s+(?:the\s+)?(?:required\s+)?skills?'
        ]
        return any(re.search(p, query, re.IGNORECASE) for p in patterns)
    
    def _is_hiring_recommendation_query(self, query):
        """Check if query is about hiring recommendation."""
        patterns = [
            r'(?:whom|who)\s+should\s+(?:we\s+)?hire',
            r'hiring\s+recommendation',
            r'who\s+do\s+you\s+recommend',
            r'recommend(?:ed)?\s+candidate',
            r'best\s+(?:fit|choice|pick)',
            r'who\s+should\s+we\s+(?:interview|shortlist)'
        ]
        return any(re.search(p, query, re.IGNORECASE) for p in patterns)
    
    def _is_summary_query(self, query):
        """Check if query is about summary/overview of the whole pool."""
        patterns = [
            r'(?:give|show|provide)\s+(?:me\s+)?(?:a\s+)?(?:summary|overview)',
            r'summari[sz]e\s+(?:the\s+|all\s+|me\s+)?(?:candidate|pool|results|rankings)',
            r'summary\s+of\s+(?:the\s+|all\s+)?(?:candidate|pool|results|rankings)',
            r'tell\s+me\s+about\s+(?:the\s+)?(?:candidates|results|rankings)\s*(?:pool)?\s*$',
            r'overview\s+of\s+(?:the\s+)?(?:candidate|pool)',
            r'what\s+(?:can\s+you\s+)?tell\s+me',
            r'overall\s+(?:picture|view|summary)'
        ]
        return any(re.search(p, query, re.IGNORECASE) for p in patterns)
    
    def _is_specific_candidate_query(self, query):
        """Check if query is about one specific candidate.

        Deliberately narrow: it must resolve to an actual candidate, either by
        name or by a rank/ordinal reference ("candidate 1", "the second one").
        """
        patterns = [
            r'(?:tell|show)\s+me\s+about\s+[\w\'-]+',
            r'candidate\s*#?\s*(\d+)\b',
            r'\brank(?:ed)?\s*#?\s*(\d+)\b',
            r'\b(\d+)(?:st|nd|rd|th)\s+(?:ranked\s+)?candidate\b',
            r'\b(first|second|third|fourth|fifth|top|best|worst)\s+(?:ranked\s+)?candidate\b',
            r'what\s+about\s+(\w+)',
            r'(\w+)\'s\s+(?:profile|score|details|ranking)'
        ]
        if not any(re.search(p, query, re.IGNORECASE) for p in patterns):
            return False

        # Guard: the bare word "candidate(s)" is a pool question, not a
        # specific-candidate question ("summarize the candidate pool"). Only
        # allow it when a rank/ordinal reference disambiguates the request.
        if re.search(r'\bcandidates?\b', query, re.IGNORECASE) and not re.search(
            r'candidate\s*#?\s*\d+|\d+(?:st|nd|rd|th)\s+(?:ranked\s+)?candidate|'
            r'(?:first|second|third|fourth|fifth|top|best|worst)\s+(?:ranked\s+)?candidate',
            query, re.IGNORECASE
        ):
            return False

        return True
    
    def _is_analytics_query(self, query):
        """Check if query is about analytics/stats."""
        patterns = [
            r'(?:average|avg|mean)\s+(?:candidate\s+)?(?:score|fit|match|rating)',
            r'(?:what|whats|what\'s)\s+(?:the\s+)?(?:average|avg|mean)',
            r'statistics|stats|analytics',
            r'how\s+many\s+candidates',
            r'distribution|breakdown',
            r'skill\s+(?:coverage|distribution|frequency)',
            r'experience\s+(?:distribution|level|range)'
        ]
        return any(re.search(p, query, re.IGNORECASE) for p in patterns)
    
    def _handle_comparison(self, query, ranked_results):
        """Compare two candidates."""
        if not ranked_results:
            return {
                'type': 'comparison',
                'answer': "No candidates to compare. Please analyze candidates first."
            }

        # Extract names/identifiers
        candidates = self._extract_candidate_names(query, ranked_results)
        
        if len(candidates) >= 2:
            c1 = next((c for c in ranked_results if candidates[0].lower() in self._name(c).lower()), None)
            c2 = next((c for c in ranked_results if candidates[1].lower() in self._name(c).lower()), None)
            
            if c1 and c2 and c1 is not c2:
                return {
                    'type': 'comparison',
                    'answer': self._build_comparison_text(c1, c2),
                    'candidates': [self._name(c1), self._name(c2)]
                }
            elif c1:
                # Compare with top candidate
                c2 = ranked_results[0]
                return {
                    'type': 'comparison',
                    'answer': self._build_comparison_text(c1, c2),
                    'candidates': [self._name(c1), self._name(c2)]
                }
        
        # Default: compare top 2
        if len(ranked_results) >= 2:
            return {
                'type': 'comparison',
                'answer': self._build_comparison_text(ranked_results[0], ranked_results[1]),
                'candidates': [self._name(ranked_results[0]), self._name(ranked_results[1])]
            }
        
        return {
            'type': 'comparison',
            'answer': "Not enough candidates to compare. Please upload at least 2 resumes."
        }
    
    def _handle_top_candidates(self, query, ranked_results):
        """Show top N candidates."""
        # Extract number
        num_match = re.search(r'top\s+(\d+)', query)
        n = int(num_match.group(1)) if num_match else 3
        
        n = min(n, len(ranked_results))
        
        if n == 0:
            return {
                'type': 'top_candidates',
                'answer': "No candidates available to rank."
            }
        
        lines = [f"🏆 **Top {n} Candidates:**"]
        for i in range(n):
            c = ranked_results[i]
            skills = ', '.join(self._profile(c).get('technical_skills', [])[:5]) or 'Not listed'
            lines.append(f"   #{c.get('rank', i + 1)} **{self._name(c)}** — {self._score(c)*100:.1f}% fit")
            lines.append(f"      Skills: {skills}")
        
        return {
            'type': 'top_candidates',
            'answer': '\n'.join(lines),
            'count': n
        }
    
    def _handle_skill_query(self, query, ranked_results):
        """Find candidates with specific skills."""
        # Extract skill from query
        skill_names = ['python', 'sql', 'aws', 'docker', 'kubernetes', 'tensorflow', 'pytorch', 
                       'nlp', 'machine learning', 'deep learning', 'spark', 'kafka', 'tableau', 
                       'power bi', 'flask', 'fastapi', 'react', 'angular', 'java', 'scala']
        
        found_skills = [s for s in skill_names if s in query.lower()]
        
        if not found_skills:
            return {
                'type': 'skill_query',
                'answer': "I can help find candidates with specific skills. Try: 'Show candidates with Python' or 'Find candidates skilled in AWS'"
            }
        
        skill = found_skills[0]
        matching = [c for c in ranked_results if skill in self._skills(c)]
        
        if not matching:
            return {
                'type': 'skill_query',
                'answer': f"No candidates found with {skill.title()} skills."
            }
        
        lines = [f"📋 **Candidates with {skill.title()}:** ({len(matching)} found)"]
        for c in matching[:5]:
            lines.append(f"   #{c.get('rank', '?')} **{self._name(c)}** — {self._score(c)*100:.1f}% overall")
        
        return {
            'type': 'skill_query',
            'answer': '\n'.join(lines),
            'skill': skill,
            'count': len(matching)
        }
    
    def _handle_missing_skills_query(self, query, ranked_results, jd_profile=None):
        """Find candidates missing certain skills, or the most-missing skill."""
        skill_names = ['python', 'sql', 'aws', 'docker', 'kubernetes', 'tensorflow', 'pytorch',
                       'nlp', 'machine learning', 'deep learning', 'spark', 'kafka']

        # "which skill is missing the most" needs a pool-wide aggregate, not a
        # per-candidate "who lacks X" filter.
        wants_aggregate = bool(re.search(
            r'(?:which|what)\s+skills?\s+(?:is|are)\s+missing\s+the\s+most|'
            r'missing\s+the\s+most|lack(?:s|ing)?\s+the\s+most',
            query, re.IGNORECASE))

        found_skills = [s for s in skill_names if s in query.lower() and not wants_aggregate]

        if not found_skills:
            return self._handle_skill_gap_aggregate(ranked_results, jd_profile)

        skill = found_skills[0]
        lacking = [c for c in ranked_results if skill not in self._skills(c)]
        
        if not lacking:
            return {
                'type': 'missing_skills',
                'answer': f"All candidates have {skill.title()} skills."
            }
        
        lines = [f"📊 **Candidates lacking {skill.title()}:** ({len(lacking)} found)"]
        for c in lacking[:5]:
            lines.append(f"   #{c.get('rank', '?')} **{self._name(c)}** — {self._score(c)*100:.1f}% overall")
        
        return {
            'type': 'missing_skills',
            'answer': '\n'.join(lines),
            'skill': skill,
            'count': len(lacking)
        }
    
    def _handle_skill_gap_aggregate(self, ranked_results, jd_profile=None):
        """Summarise which required skills the pool is missing most often."""
        if not ranked_results:
            return {
                'type': 'missing_skills',
                'answer': "No skill gap data available. Analyze candidates first."
            }

        # Prefer the per-candidate skill_gaps computed during analysis.
        missing_counter = Counter()
        per_candidate = []

        for c in ranked_results:
            gaps = c.get('skill_gaps') or {}
            # Key names produced by SkillGapAnalyzer.analyze_skill_gaps, with
            # fallbacks for other shapes.
            missing = (
                gaps.get('missing_required_skills')
                or gaps.get('missing_skills')
                or gaps.get('missing_required')
                or gaps.get('missing')
                or []
            )
            # Preferred-skill gaps are secondary; only used when nothing required.
            if not missing:
                missing = gaps.get('missing_preferred_skills') or []

            missing = [str(s) for s in missing if s]
            for skill in missing:
                missing_counter[skill.lower()] += 1
            per_candidate.append((c, missing))

        if not missing_counter:
            # Everyone covers the required skills. Fall back to the skills the
            # pool has least coverage of, using the JD requirements when known.
            jd_skills = [
                str(s).lower() for s in ((jd_profile or {}).get('required_skills') or [])
            ]
            if jd_skills:
                for skill in jd_skills:
                    holders = sum(1 for c in ranked_results if skill in self._skills(c))
                    missing_counter[skill] = total - holders

        if not missing_counter:
            return {
                'type': 'missing_skills',
                'answer': (
                    "✅ No significant skill gaps detected — the pool covers the "
                    "role's required skills. Ask about a specific skill instead, "
                    "e.g. 'Who lacks Kubernetes experience?'"
                )
            }

        total = len(ranked_results)
        top_gaps = missing_counter.most_common(5)

        lines = ["🔍 **Most Missing Skills Across the Pool:**"]
        for skill, count in top_gaps:
            pct = count / total * 100
            lines.append(f"   • {skill.title()}: missing in {count}/{total} candidates ({pct:.0f}%)")

        # Also surface the candidates with the largest gaps.
        per_candidate.sort(key=lambda x: len(x[1]), reverse=True)
        biggest = [(c, m) for c, m in per_candidate if m][:3]
        if biggest:
            lines.append("")
            lines.append("**Candidates with the largest gaps:**")
            for c, missing in biggest:
                lines.append(
                    f"   #{c.get('rank', '?')} **{self._name(c)}** — missing: {', '.join(missing[:4])}"
                )

        return {
            'type': 'missing_skills',
            'answer': '\n'.join(lines),
            'top_missing_skills': [{'skill': s, 'count': n} for s, n in top_gaps]
        }
    
    def _handle_hiring_recommendation(self, ranked_results, jd_profile):
        """Generate hiring recommendation."""
        if not ranked_results:
            return {
                'type': 'recommendation',
                'answer': "No candidates available to evaluate."
            }
        
        top = ranked_results[0]
        role = (jd_profile or {}).get('role', 'the role')
        top_name = self._name(top)
        top_score = self._score(top)
        reason = str(top.get('reason', '') or 'Strong overall match across the required dimensions.')
        
        lines = [
            f"🎯 **Hiring Recommendation for {role.title()}**",
            "",
            f"**Top Pick: #{top.get('rank', 1)} {top_name}** — {top_score*100:.1f}% fit",
            "",
            f"**Why this candidate:**"
        ]
        lines.append(f"   {reason}")
        
        # Additional candidates if close match
        if len(ranked_results) > 1 and self._score(ranked_results[1]) >= top_score * 0.9:
            alt = ranked_results[1]
            lines.append(f"\n**Also Consider: #{alt.get('rank', 2)} {self._name(alt)}** — {self._score(alt)*100:.1f}% fit")
        
        # Interview recommendation
        lines.append(f"\n**Recommended Action:** Interview {top_name} to assess practical skills and cultural fit.")
        
        return {
            'type': 'recommendation',
            'answer': '\n'.join(lines),
            'top_candidate': top_name,
            'top_score': top_score
        }
    
    def _handle_summary(self, ranked_results, jd_profile):
        """Provide overall summary."""
        if not ranked_results:
            return {
                'type': 'summary',
                'answer': "No candidates have been analyzed yet. Upload resumes and a job description to get started."
            }
        
        total = len(ranked_results)
        scores = [self._score(c) for c in ranked_results]
        avg = sum(scores) / total * 100
        top = ranked_results[0]
        jd = jd_profile or {}
        role = jd.get('role') or 'the position'
        top_score = self._score(top) * 100
        last_score = self._score(ranked_results[-1]) * 100
        required = jd.get('required_skills') or []
        skills_line = f"**Skills to evaluate:** {', '.join(required[:5])}" if required else ""
        
        lines = [
            f"📊 **Candidate Ranking Summary**",
            f"",
            f"**Role:** {role.title()}",
            f"**Total Candidates:** {total}",
            f"**Average Fit Score:** {avg:.1f}%",
            f"**Score Range:** {top_score:.1f}% — {last_score:.1f}%",
            f"",
            f"**Top Candidate:** {self._name(top)} ({top_score:.1f}%)",
            skills_line,
            f"",
            f"**Distribution:**",
            f"   Excellent (80%+): {sum(1 for s in scores if s >= 0.8)}",
            f"   Good (60-80%): {sum(1 for s in scores if 0.6 <= s < 0.8)}",
            f"   Moderate (40-60%): {sum(1 for s in scores if 0.4 <= s < 0.6)}",
            f"   Needs Development (<40%): {sum(1 for s in scores if s < 0.4)}"
        ]
        
        return {
            'type': 'summary',
            'answer': '\n'.join(lines),
            'total': total,
            'avg_score': avg
        }
    
    def _handle_specific_candidate(self, query, ranked_results):
        """Show details for a specific candidate."""
        if not ranked_results:
            return {
                'type': 'specific_candidate',
                'answer': "No candidates have been analyzed yet."
            }

        # Reuse the shared resolver so rank/ordinal/name queries all work.
        found = self._extract_candidate_names(query, ranked_results)
        query_lower = query.lower()
        matched = None
        if found:
            target = found[0].lower()
            matched = next(
                (c for c in ranked_results if target in self._name(c).lower()), None
            )

        if not matched:
            return {
                'type': 'specific_candidate',
                'answer': "I couldn't find that candidate. Available candidates: "
                          + ', '.join(self._name(c) for c in ranked_results[:5])
            }

        profile = self._profile(matched)
        scores = matched.get('scores') or {}
        skills = ', '.join(profile.get('technical_skills', [])[:7]) or 'Not listed'
        exp = profile.get('experience_years', 0) or 0
        education = ', '.join(profile.get('education', []) or []) or 'Not listed'
        score_pct = self._score(matched) * 100

        lines = [
            f"👤 **{self._name(matched)}** | Rank #{matched.get('rank', '?')} | {score_pct:.1f}% Fit",
            f"",
            f"**📊 Scores:**",
            f"   Skill Match: {(scores.get('skill_match') or 0)*100:.0f}%",
            f"   Experience: {(scores.get('experience_match') or 0)*100:.0f}%",
            f"   Semantic Fit: {(scores.get('semantic_similarity') or 0)*100:.0f}%",
            f"   Projects: {(scores.get('project_relevance') or 0)*100:.0f}%",
            f"   {(scores.get('behavioral_score') or 0)*100:.0f}% Behavioral",
            f"",
            f"**💼 Experience:** {exp} years",
            f"**🔧 Skills:** {skills}",
            f"**🎓 Education:** {education}",
            f"",
            f"**💡 Why:** {str(matched.get('reason', ''))[:200]}"
        ]

        skill_gaps = matched.get('skill_gaps') or {}
        missing = (
            skill_gaps.get('missing_required_skills')
            or skill_gaps.get('missing_skills')
            or skill_gaps.get('missing_required')
            or []
        )
        if missing:
            lines.insert(-2, f"**⚠️ Skill gaps:** {', '.join(missing[:6])}")

        return {
            'type': 'specific_candidate',
            'answer': '\n'.join(lines),
            'candidate': self._name(matched)
        }
    
    def _handle_analytics(self, ranked_results):
        """Provide analytics and statistics."""
        if not ranked_results:
            return {
                'type': 'analytics',
                'answer': "No data available. Analyze candidates first."
            }
        
        total = len(ranked_results)
        scores = [self._score(c) * 100 for c in ranked_results]
        
        # Skill frequency analysis
        all_skills = []
        for c in ranked_results:
            all_skills.extend(self._skills(c))
        
        skill_counts = Counter(all_skills)
        top_skills = skill_counts.most_common(5)
        
        lines = [
            f"📈 **Recruitment Analytics**",
            f"",
            f"**Score Statistics:**",
            f"   Mean: {sum(scores)/total:.1f}%",
            f"   Median: {sorted(scores)[total//2]:.1f}%",
            f"   Std Dev: {(sum((s - sum(scores)/total)**2 for s in scores)/total)**0.5:.1f}",
            f"   Highest: {max(scores):.1f}%",
            f"   Lowest: {min(scores):.1f}%",
            f"",
            f"**Top Skills Among Candidates:**",
        ]
        for skill, count in top_skills:
            lines.append(f"   • {skill.title()}: {count}/{total} candidates ({count/total*100:.0f}%)")
        
        return {
            'type': 'analytics',
            'answer': '\n'.join(lines)
        }
    
    def _handle_general(self, ranked_results, jd_profile):
        """Handle general queries with helpful suggestions."""
        n = len(ranked_results)
        suggestions = [
            "🔍 **Try these queries:**",
            "",
            "• 'Show top 5 candidates' — See highest-ranked profiles",
            "• 'Compare Candidate A and Candidate B' — Side-by-side comparison",
            "• 'Show candidates with Python' — Filter by skill",
            "• 'Who lacks AWS skills?' — Find skill gaps",
            "• 'Who should we hire?' — Get recommendation",
            "• 'Give me a summary' — Overall ranking overview",
            f"• 'Tell me about [name]' — Specific candidate details",
            "",
            f"📊 Currently have **{n} ranked candidates** ready for analysis."
        ]
        
        return {
            'type': 'general',
            'answer': '\n'.join(suggestions)
        }
    
    def _extract_candidate_names(self, query, ranked_results):
        """Extract candidate names/identifiers from a query.

        Resolves, in order of reliability:
          * explicit ranks: ``#3``, ``rank 3``, ``candidate 2``
          * ordinals:       ``first``, ``second``, ``3rd``
          * name substrings (full name or first/last token of 3+ chars)
        """
        candidates = []
        query_lower = query.lower()

        def add(cand):
            if cand is None:
                return
            name = self._name(cand)
            if name not in candidates:
                candidates.append(name)

        # 1) Explicit rank references
        rank_refs = re.findall(
            r'(?:#|rank(?:ed)?\s*#?\s*|candidate\s*#?\s*)(\d+)\b', query_lower)
        # 2) Ordinals ("the second candidate", "3rd candidate")
        ordinal_words = {
            'first': 1, 'top': 1, 'best': 1,
            'second': 2, 'third': 3, 'fourth': 4, 'fifth': 5,
            'worst': None,  # resolved positionally below
        }
        for word, pos in ordinal_words.items():
            if re.search(rf'\b{word}\s+(?:ranked\s+)?candidate\b', query_lower) and pos:
                rank_refs.append(str(pos))
        for num in re.findall(r'\b(\d+)(?:st|nd|rd|th)\s+(?:ranked\s+)?candidate\b', query_lower):
            rank_refs.append(num)
        if re.search(r'\bworst\s+(?:ranked\s+)?candidate\b', query_lower) and ranked_results:
            rank_refs.append(str(len(ranked_results)))

        for rank_str in rank_refs:
            try:
                rank = int(rank_str)
            except (TypeError, ValueError):
                continue
            if 1 <= rank <= len(ranked_results):
                add(ranked_results[rank - 1])

        if candidates:
            return candidates[:2]

        # 3) Fall back to matching candidate names mentioned in the query
        for c in ranked_results:
            name = self._name(c)
            full = name.lower()
            if full and full in query_lower:
                add(c)
                continue
            for part in full.split():
                # Require 3+ chars to avoid matching noise words like "kim"
                if len(part) > 2 and part in query_lower:
                    add(c)
                    break

        return candidates[:2]
    
    def _build_comparison_text(self, c1, c2):
        """Build text comparing two candidates."""
        p1 = self._profile(c1)
        p2 = self._profile(c2)
        s1 = c1.get('scores') or {}
        s2 = c2.get('scores') or {}
        sc1, sc2 = self._score(c1), self._score(c2)
        n1, n2 = self._name(c1), self._name(c2)

        def pct(scores, key):
            return f"{(scores.get(key) or 0)*100:.0f}%"
        
        lines = [
            f"⚖️ **Candidate Comparison**",
            f"",
            f"**#{c1.get('rank', '?')} {n1}** vs **#{c2.get('rank', '?')} {n2}**",
            f"",
            f"| Dimension | {n1[:14]} | {n2[:14]} |",
            f"|---|---|---|",
            f"| **Overall** | {sc1*100:.1f}% | {sc2*100:.1f}% |",
            f"| **Skill Match** | {pct(s1, 'skill_match')} | {pct(s2, 'skill_match')} |",
            f"| **Experience** | {pct(s1, 'experience_match')} | {pct(s2, 'experience_match')} |",
            f"| **Semantic** | {pct(s1, 'semantic_similarity')} | {pct(s2, 'semantic_similarity')} |",
            f"| **Projects** | {pct(s1, 'project_relevance')} | {pct(s2, 'project_relevance')} |",
            f"| **Experience** | {p1.get('experience_years', 0) or 0} yrs | {p2.get('experience_years', 0) or 0} yrs |",
            f"| **Skills** | {len(p1.get('technical_skills') or [])} | {len(p2.get('technical_skills') or [])} |",
            f"| **Projects** | {p1.get('project_count', 0) or 0} | {p2.get('project_count', 0) or 0} |",
            f"",
            f"**Verdict:** ",
        ]

        winner, loser = (c1, c2) if sc1 > sc2 else (c2, c1)
        diff = abs(sc1 - sc2) * 100
        lines.append(f"**{self._name(winner)}** leads by {diff:.1f} percentage points overall.")
        lines.append(f"Key advantage: {str(loser.get('reason', ''))[:150]}")

        return '\n'.join(lines)
    
    def get_conversation_context(self):
        """Get conversation history for context."""
        return self.conversation_history[-10:]  # Last 10 messages
    
    def clear_history(self):
        """Clear conversation history."""
        self.conversation_history = []