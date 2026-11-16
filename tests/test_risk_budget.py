"""Risk-tiering + budget tests — SKEL-5 MEA-2 (OC-16, OC-4).

Risk tier from manifest + AC count + structural signals; small stories
skip plan review + one reviewer. Budget enforcement at the controller
(spend cap + timeout + dispatch refusal at ceiling), NOT agent self-report.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from factory.risk import classify_risk, review_plan
from factory.budget import Budget, BudgetError


def test_small_story_skips_plan_review():
    tier = classify_risk(manifest=["src/a.ts", "src/a.test.ts"], ac_count=3,
                         structural_signals=0)
    assert tier == "small"
    plan = review_plan(tier)
    assert plan["plan_review"] is False
    assert plan["reviewers"] == 1


def test_medium_story_one_plan_review_one_reviewer():
    tier = classify_risk(manifest=["src/a.ts", "src/b.ts", "src/a.test.ts"],
                         ac_count=5, structural_signals=1)
    assert tier == "medium"
    plan = review_plan(tier)
    assert plan["plan_review"] is True
    assert plan["reviewers"] == 1


def test_large_story_full_panel():
    tier = classify_risk(manifest=[f"src/f{i}.ts" for i in range(8)],
                         ac_count=6, structural_signals=2)
    assert tier == "large"
    plan = review_plan(tier)
    assert plan["plan_review"] is True
    assert plan["reviewers"] >= 2


def test_structural_signals_force_large():
    # >=2 structural signals = stacked story = large regardless of size
    tier = classify_risk(manifest=["src/a.ts"], ac_count=2, structural_signals=2)
    assert tier == "large"


def test_many_files_force_at_least_medium():
    tier = classify_risk(manifest=[f"src/f{i}.ts" for i in range(7)],
                         ac_count=3, structural_signals=0)
    assert tier in ("medium", "large")


def test_budget_refuses_at_ceiling():
    b = Budget(spend_cap_usd=1.0, job_timeout_s=600)
    b.record_spend(0.9)
    # 0.9 + 0.2 = 1.1 > 1.0 -> must refuse
    try:
        b.check_dispatch(estimated_usd=0.2)
        assert False, "expected BudgetError"
    except BudgetError:
        pass


def test_budget_allows_under_ceiling():
    b = Budget(spend_cap_usd=1.0, job_timeout_s=600)
    b.record_spend(0.5)
    b.check_dispatch(estimated_usd=0.4)  # 0.9 <= 1.0, ok


def test_budget_timeout_enforced():
    b = Budget(spend_cap_usd=10.0, job_timeout_s=600)
    assert b.effective_timeout(requested_s=900) == 600  # capped
    assert b.effective_timeout(requested_s=300) == 300  # under cap


def test_budget_spend_accumulates():
    b = Budget(spend_cap_usd=5.0, job_timeout_s=600)
    b.record_spend(1.0)
    b.record_spend(2.0)
    assert b.spent_usd == 3.0
    assert b.remaining_usd == 2.0


def test_budget_zero_cap_refuses_all():
    b = Budget(spend_cap_usd=0.0, job_timeout_s=600)
    try:
        b.check_dispatch(estimated_usd=0.01)
        assert False
    except BudgetError:
        pass
