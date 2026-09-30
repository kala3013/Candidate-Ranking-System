# Ranked Candidate Output Files

## Ranked Output Format

| File | Description |
|------|-------------|
| `submission_final.csv` | Top 100 ranked candidates for a Senior AI Engineer role |

### submission_final.csv Format

Columns: `candidate_id, rank, score, reasoning`

- **candidate_id**: Unique CAND_XXXXXXX identifier from the dataset
- **rank**: 1 (best fit) through 100
- **score**: Composite score (0.88-0.94) based on 6 weighted components
- **reasoning**: 1-2 sentence specific justification per candidate

### Scoring Components

| Component | Weight | What it measures |
|-----------|--------|------------------|
| Skill Match | 30% | AI/ML core skills, career AI signals, ML role count |
| Behavioral | 25% | Platform activity, responsiveness, availability |
| Experience | 20% | Years, title relevance, product-company experience |
| Projects | 15% | Career depth, impact indicators, progression |
| Education | 5% | Institution tier, field relevance |
| Certifications | 5% | Relevant ML/AWS/Cloud certifications |

### Keys to the ranking

1. **Real AI/ML engineers** with production retrieval/ranking experience are ranked highest
2. **Behavioral signals matter** - responsiveness, recent activity, open-to-work flags
3. **Consulting-only candidates** are penalized (per JD's explicit disqualifier)
4. **CV/Speech-only specialists** without NLP/IR exposure are deprioritized
5. **Reasoning is specific and honest** - includes concerns like notice periods