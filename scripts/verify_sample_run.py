"""
Verify the full system end-to-end using the built-in sample data.

Expects the Flask server to already be running (default: http://127.0.0.1:5000).

Usage:
    python app.py                        # terminal 1
    python scripts/verify_sample_run.py  # terminal 2
"""
import os
import sys
import json
import time

try:
    import requests
except ImportError:
    requests = None

if requests is None:
    sys.exit("The 'requests' package is required to run this verification script.")

BASE = os.environ.get("BASE_URL", "http://127.0.0.1:5000").rstrip("/")


def hr(char="=", n=78):
    print(char * n)


def show_ranking(result):
    """Pretty-print the ranked candidate table."""
    summary = result.get("summary", {})
    title = result.get("job_profile", {}).get("title", "Job Description")
    hr()
    print(f"SAMPLE DATA ANALYSIS  --  "
          f"{summary.get('total_candidates', 0)} candidates vs \"{title}\"")
    hr()
    header = f"{'#':<3} {'CANDIDATE':<20} {'SCORE':>6} {'EXP':>5} " \
             f"{'SKILLS':>7} {'POTENTIAL':>10}"
    print(header)
    print("-" * len(header))
    for c in result.get("ranked_candidates", []):
        profile = c.get("profile", {}) or {}
        potential = c.get("potential", {}) or {}
        print(f"{c.get('rank', '-'):<3} "
              f"{str(c.get('candidate_name', 'unknown'))[:20]:<20} "
              f"{c.get('final_score', 0):>6.1f} "
              f"{profile.get('experience_years', 0):>5} "
              f"{len(profile.get('skills', []) or []):>7} "
              f"{potential.get('potential_score', 0):>10.1f}")
    hr()


def show_reasons(result):
    print("\nEXPLAINABLE RANKINGS (top 3)")
    print("-" * 78)
    for c in result.get("ranked_candidates", [])[:3]:
        print(f"  #{c.get('rank')} {c.get('candidate_name')} "
              f"({c.get('final_score')}): {c.get('reason')}")


def show_pool_summary(result):
    s = result.get("summary", {})
    dist = s.get("score_distribution", {})
    exp = s.get("experience_distribution", {})
    print("\nHIRING DASHBOARD")
    print("-" * 78)
    print(f"  Average score ........ {s.get('average_score')}")
    print(f"  Median score ......... {s.get('median_score')}")
    print(f"  Top candidate ........ {s.get('top_candidate_name')} "
          f"({s.get('top_score')})")
    print(f"  Experience range ..... {exp.get('min_exp')} - {exp.get('max_exp')} "
          f"yrs (avg {exp.get('avg_exp')})")
    print(f"  Score tiers .......... excellent={dist.get('excellent_80_plus')} "
          f"good={dist.get('good_60_80')} moderate={dist.get('moderate_40_60')} "
          f"below40={dist.get('needs_development_below_40')}")
    top = [f"{t['skill']}({t['count']})" for t in s.get("top_skills", [])[:8]]
    print(f"  Top skills ........... {', '.join(top)}")


def check_endpoint(name, method, path, payload=None):
    """Call an endpoint and report pass/fail. Returns the parsed body or None."""
    url = f"{BASE}{path}"
    started = time.time()
    try:
        if method == "GET":
            resp = requests.get(url, timeout=120)
        elif payload is None:
            resp = requests.post(url, timeout=120)
        else:
            resp = requests.post(url, json=payload, timeout=120)
    except Exception as exc:
        print(f"  FAIL  {name:<28} connection error: {exc}")
        return None

    elapsed = int((time.time() - started) * 1000)
    body, detail = None, ""
    try:
        body = resp.json()
    except ValueError:
        body = None

    if resp.status_code == 200:
        if isinstance(body, dict) and body.get("error"):
            detail = f"error in body: {body['error']}"
        elif body is None:
            detail = f"{len(resp.content)} bytes"
        else:
            detail = "json ok"
    else:
        detail = f"HTTP {resp.status_code} "
        detail += str(body)[:100] if body else resp.text[:100].replace("\n", " ")

    failed = resp.status_code != 200 or "error" in detail
    mark = "FAIL" if failed else "PASS"
    print(f"  {mark}  {name:<28} {resp.status_code} {elapsed:>5}ms  {detail[:58]}")
    return body


ENDPOINTS = [
    ("Analytics dashboard", "GET", "/api/analytics", None),
    ("Executive summary", "GET", "/api/executive-summary", None),
    ("Skill gaps #0", "GET", "/api/skill-gaps/0", None),
    ("Interview questions #0", "GET", "/api/interview-questions/0", None),
    ("Bias report #0", "GET", "/api/bias-report/0", None),
    ("Candidate summary #0", "GET", "/api/candidate-summary/0", None),
    ("Potential engine #0", "GET", "/api/potential/0", None),
    ("ATS score #0", "GET", "/api/ats-score/0", None),
    ("Salary prediction #0", "GET", "/api/salary-predict/0", None),
    ("Career path #0", "GET", "/api/career-path/0", None),
    ("Diversity analysis", "GET", "/api/diversity-analysis", None),
    ("Analysis history", "GET", "/api/history", None),
    ("Features list", "GET", "/api/features-list", None),
    ("Demo config", "GET", "/api/demo-config", None),
    ("Team fit", "POST", "/api/team-fit",
     {"candidate_index": 0, "team_culture": "startup",
      "team_skills": ["python", "machine learning", "sql"]}),
    ("Team fit compare", "POST", "/api/team-fit/compare",
     {"team_culture": "enterprise",
      "team_skills": ["python", "deep learning"]}),
    ("Compare candidates", "POST", "/api/compare", {"index1": 0, "index2": 1}),
    ("Copilot: top 3", "POST", "/api/copilot",
     {"query": "show top 3 candidates"}),
    ("Copilot: python skills", "POST", "/api/copilot",
     {"query": "who has python skills"}),
    ("Copilot: compare 1 and 2", "POST", "/api/copilot",
     {"query": "compare candidate 1 and candidate 2"}),
    ("Copilot: candidate 1 detail", "POST", "/api/copilot",
     {"query": "tell me about candidate 1"}),
    ("Copilot: pool summary", "POST", "/api/copilot",
     {"query": "summarize the candidate pool"}),
    ("Email draft #0", "POST", "/api/email-draft",
     {"candidate_index": 0, "email_type": "interview_invite"}),
    ("Salary compare", "POST", "/api/salary-compare",
     {"candidate_index": 0, "offered_salary": 140000}),
    ("Multi-job analyze", "POST", "/api/multi-job-analyze",
     {"jobs": {"ML Engineer": "Looking for machine learning engineer with Python, PyTorch, MLOps, Docker, AWS.",
               "Data Analyst": "Looking for data analyst with SQL, Python, Excel, data visualization, Tableau."}}),
    ("Export CSV", "GET", "/api/export?format=csv", None),
    ("Download results", "GET", "/api/download", None),
]


def main():
    hr("=")
    print("Candidate Ranking System -- sample data end-to-end verification")
    print(f"Target: {BASE}")
    hr("=")

    try:
        health = requests.get(f"{BASE}/api/health", timeout=30).json()
    except Exception as exc:
        sys.exit(f"Server not reachable at {BASE}: {exc}\n"
                 f"Start it first with:  python app.py")
    print(f"\nHealth: {health.get('status')} | model={health.get('model')} "
          f"| version={health.get('version')} "
          f"| {len(health.get('features', []))} features")

    print("\nRunning POST /api/analyze-sample ...")
    started = time.time()
    resp = requests.post(f"{BASE}/api/analyze-sample", timeout=600)
    print(f"Completed in {time.time() - started:.1f}s")
    if resp.status_code != 200:
        sys.exit(f"Sample analysis failed: HTTP {resp.status_code} "
                 f"{resp.text[:400]}")
    result = resp.json()
    if not result.get("ranked_candidates"):
        sys.exit(f"No candidates returned: {json.dumps(result)[:400]}")

    show_ranking(result)
    show_reasons(result)
    show_pool_summary(result)

    print("\nDOWNSTREAM ENDPOINTS (driven by the sample analysis in memory)")
    hr("-")
    failures = 0
    for name, method, path, payload in ENDPOINTS:
        if check_endpoint(name, method, path, payload) is None:
            failures += 1
    hr("-")

    hr("=")
    print(f"Endpoint checks: {len(ENDPOINTS) - failures} passed, "
          f"{failures} failed (see FAIL rows above)")
    print(f"Dashboard: {BASE}")
    hr("=")


if __name__ == "__main__":
    main()
