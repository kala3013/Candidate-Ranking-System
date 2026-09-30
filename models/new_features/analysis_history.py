"""Analysis History Manager - Persistent storage and retrieval of analysis results."""

import json
import os
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

HISTORY_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'history')


class AnalysisHistoryManager:
    """Manages persistent storage of analysis history with metadata."""

    def __init__(self):
        os.makedirs(HISTORY_DIR, exist_ok=True)
        self.index_path = os.path.join(HISTORY_DIR, 'history_index.json')
        self._ensure_index()

    def _ensure_index(self):
        """Ensure history index file exists."""
        if not os.path.exists(self.index_path):
            self._write_index([])

    def _read_index(self):
        """Read history index."""
        try:
            with open(self.index_path, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return []

    def _write_index(self, index):
        """Write history index."""
        with open(self.index_path, 'w') as f:
            json.dump(index, f, indent=2)

    def save_analysis(self, results, job_profile=None, metadata=None):
        """
        Save an analysis run to history.
        
        Args:
            results: Analysis results dict
            job_profile: Job description profile
            metadata: Additional metadata dict
            
        Returns:
            str: History entry ID
        """
        entry_id = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        candidates = results.get('ranked_candidates', [])
        summary = results.get('summary', {})
        job = job_profile or results.get('job_profile', {})
        
        # Create history entry
        entry = {
            'id': entry_id,
            'timestamp': datetime.now().isoformat(),
            'total_candidates': len(candidates),
            'role': (job or {}).get('role', 'Unknown Role'),
            'top_candidate': candidates[0]['candidate_name'] if candidates else 'N/A',
            'top_score': candidates[0]['final_score'] if candidates else 0,
            'average_score': summary.get('average_score', 0),
            'job_profile': {
                'role': (job or {}).get('role', ''),
                'required_skills': (job or {}).get('required_skills', [])[:5],
                'experience_required': (job or {}).get('experience_required', 0),
            },
            'metadata': metadata or {},
            'candidates_summary': [
                {
                    'name': c.get('candidate_name', ''),
                    'score': c.get('final_score', 0),
                    'rank': c.get('rank', 0),
                    'skill_count': len(c.get('profile', {}).get('technical_skills', [])),
                    'experience': c.get('profile', {}).get('experience_years', 0),
                }
                for c in candidates[:5]  # Store top 5 candidate summaries
            ]
        }
        
        # Save full results to individual file
        entry_path = os.path.join(HISTORY_DIR, f'{entry_id}.json')
        with open(entry_path, 'w') as f:
            json.dump(results, f, indent=2)
        
        # Update index
        index = self._read_index()
        index.insert(0, entry)
        # Keep last 50 entries
        index = index[:50]
        self._write_index(index)
        
        return entry_id

    def get_history_list(self, limit=20, offset=0):
        """
        Get paginated history list.
        
        Args:
            limit: Number of entries to return
            offset: Offset for pagination
            
        Returns:
            list: History entries
        """
        index = self._read_index()
        return index[offset:offset + limit]

    def get_history_entry(self, entry_id):
        """
        Get full analysis result for a history entry.
        
        Args:
            entry_id: History entry ID
            
        Returns:
            dict: Full analysis results or None
        """
        entry_path = os.path.join(HISTORY_DIR, f'{entry_id}.json')
        if not os.path.exists(entry_path):
            return None
        
        try:
            with open(entry_path, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return None

    def delete_history_entry(self, entry_id):
        """
        Delete a history entry.
        
        Args:
            entry_id: History entry ID
            
        Returns:
            bool: Success status
        """
        entry_path = os.path.join(HISTORY_DIR, f'{entry_id}.json')
        deleted = False
        
        if os.path.exists(entry_path):
            os.remove(entry_path)
            deleted = True
        
        # Remove from index
        index = self._read_index()
        index = [e for e in index if e['id'] != entry_id]
        self._write_index(index)
        
        return deleted

    def clear_history(self):
        """Clear all history entries."""
        index = self._read_index()
        for entry in index:
            entry_path = os.path.join(HISTORY_DIR, f"{entry['id']}.json")
            if os.path.exists(entry_path):
                os.remove(entry_path)
        
        self._write_index([])
        return True

    def get_history_stats(self):
        """Get statistics about analysis history."""
        index = self._read_index()
        
        if not index:
            return {
                'total_analyses': 0,
                'unique_roles': [],
                'total_candidates_analyzed': 0,
                'average_score': 0,
                'last_analysis': None
            }
        
        total = len(index)
        roles = list(set(e.get('role', 'Unknown') for e in index))
        total_candidates = sum(e.get('total_candidates', 0) for e in index)
        avg_score = sum(e.get('average_score', 0) for e in index) / total
        last_analysis = index[0].get('timestamp') if index else None
        
        return {
            'total_analyses': total,
            'unique_roles': roles[:10],
            'total_candidates_analyzed': total_candidates,
            'average_score': round(avg_score, 1),
            'last_analysis': last_analysis,
            'recent_analyses': [
                {
                    'id': e['id'],
                    'role': e.get('role', 'Unknown'),
                    'candidates': e.get('total_candidates', 0),
                    'timestamp': e.get('timestamp', '')
                }
                for e in index[:5]
            ]
        }