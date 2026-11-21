# Scoring example (synthetic)

A worked example of scoring v2 on a synthetic posting and the frozen golden-set
profile (`tests/golden/evaluate-position/profile.md`, "Maya Patel"). Company,
person and link are fictional. Rules: `plugin/schemas/score.schema.md`;
procedure: `plugin/references/evaluate-position-scoring.md`.

## What the user sees in chat

> **Flexa Money — Head of Product.** Posting looks live.
>
> | The posting asks | Your CV shows | Match |
> |---|---|---|
> | Own pricing, underwriting and activation on the card | "Designed and shipped the price-test framework on our flagship card product" | direct |
> | Consumer-credit product at growth stage | "leading the growth pricing surface at a Series B fintech" | direct |
> | BNPL card for near-prime customers | "a buy-now-pay-later card aimed at thin-file customers" | direct |
> | First Head of Product over 3 PMs | "Coached three APMs into senior PM roles in 18 months" | transferable — you've coached, not yet run a PM team |
> | The most technical product person in the room | "I read product code, do my own SQL, and write specs founders trust" | direct |
>
> One thing to check: they require the right to work in the UK, and I don't know yours.
> Strong company: Series B, 4x growth.
>
> File it as is, change how I rated it, or drop it?

No numbers, no tier code, no evidence-class names reach the user (TONE.md).

## The assessment Claude fills

```json
{
  "scoring_version": 2,
  "role": {"company": "Flexa Money", "position": "Head of Product", "link": "https://example.com/jobs/flexa-hop"},
  "eligibility": [
    {"requirement": "Requires relocation outside EMEA", "source": "hard_filter", "status": "PASS", "jd_quote": "Hybrid: 2 days/week in our London Bridge office"},
    {"requirement": "More than 8 direct reports (GM scope)", "source": "hard_filter", "status": "PASS", "jd_quote": "3 PMs, reporting to the CEO"},
    {"requirement": "Crypto-native companies (out of scope by preference)", "source": "hard_filter", "status": "NOT_APPLICABLE", "jd_quote": "not stated"},
    {"requirement": "More than 500 employees AND enterprise/sales-led AND no PLG signal", "source": "hard_filter", "status": "PASS", "jd_quote": "~60 people"},
    {"requirement": "Right to work in the UK", "source": "jd", "status": "UNKNOWN", "jd_quote": "Applicants must have the right to work in the UK", "note": "the profile doesn't state work authorisation"}
  ],
  "warnings": [],
  "dimensions": {
    "role_responsibility": {"score": 92, "requirement": "Own the credit-card surface end to end — pricing experiments, underwriting flows, activation", "explanation": "Pricing, underwriting and activation are each a proof point.", "evidence": [{"quote": "Designed and shipped the price-test framework on our flagship card product", "source": "profile"}, {"quote": "Led the integration of a new credit bureau into the underwriting flow", "source": "profile"}], "evidence_class": "EXPLICIT", "confidence": "high"},
    "skills_experience": {"score": 85, "requirement": "Shipped consumer-credit product at growth stage", "explanation": "Growth-stage consumer-credit work is the core of the profile.", "evidence": [{"quote": "leading the growth pricing surface at a Series B fintech", "source": "profile"}], "evidence_class": "EXPLICIT", "confidence": "high"},
    "domain": {"score": 95, "requirement": "BNPL card for near-prime UK customers", "explanation": "Same product category.", "evidence": [{"quote": "a buy-now-pay-later card aimed at thin-file customers", "source": "profile"}], "evidence_class": "EXPLICIT", "confidence": "high"},
    "seniority_ownership": {"score": 75, "requirement": "First Head of Product, own the product org of 3 PMs", "explanation": "Lead PM with mentoring, not yet a Head of a PM team.", "evidence": [{"quote": "Coached three APMs into senior PM roles in 18 months", "source": "profile"}], "evidence_class": "TRANSFERABLE", "confidence": "medium"},
    "competitive_advantage": {"score": 90, "requirement": "The most technical product person in the room", "explanation": "The moat is exactly this.", "evidence": [{"quote": "I read product code, do my own SQL, and write specs founders trust", "source": "profile"}], "evidence_class": "EXPLICIT", "confidence": "high"}
  },
  "attractiveness": {"level": "high", "factors": ["Series B led by a tier-one fund", "4x YoY revenue growth", "founder close to product"], "sources": ["posting"]}
}
```

## What `score.py compute` returns

```json
{
  "scoring_version": 2,
  "fit_score": 88.1,
  "fit_tier": "P0",
  "attractiveness": "high",
  "tier": "P0",
  "eligibility": "needs_review",
  "failed": [],
  "pending": [
    "Right to work in the UK"
  ],
  "warnings": [],
  "evidence_confidence": "high",
  "confirmed_gaps": [],
  "missing_evidence": [],
  "weights": {
    "role_responsibility": 30.0,
    "skills_experience": 25.0,
    "domain": 20.0,
    "seniority_ownership": 15.0,
    "competitive_advantage": 10.0
  },
  "thresholds": {
    "p0": 80,
    "p1": 65
  }
}
```

Fit 88.1 (P0 on its own); a strong company can't lift past P0; the unknown
right-to-work requirement makes it **needs review** — filed as P0 with the
question in the brief's Open questions, not blocked.

## What `score.py record` writes

`companies/Flexa Money/score-2026-11-21.json` (never edited) and, in `meta.md`:

```yaml
scoring_version: 2
fit_score: 88.1
tier: P0
eligibility: needs_review
evidence_confidence: high
predicted_tier: P0        # set once
initial_fit_score: 88.1   # set once
```

If the user later says "make it P1 — the team is too small to grow into",
`score.py override … --tier P1 --reason "team too small to grow into"` adds
`tier_override: P1`, the reason and the date; `predicted_tier` stays P0, so
`funnel.py --by-tier` can still tell whether the system's call was right.
