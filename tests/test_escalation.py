"""Escalation adjudication tests — anchored on the REAL round-8 case."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from factory.escalation import adjudicate

# Copilot's actual round-8 wording.
ROUND8 = ("Human assessment is needed because concurrent cross-tab submissions "
          "can silently lose a task despite both reporting success, and existing "
          "tests cover only sequential writes.")


def test_round8_is_agent_resolvable_once_proven():
    """The real case: reviewer claimed human need; evidence overrides it."""
    a = adjudicate(summary=ROUND8, klass="concurrency-lost-update",
                   reproduced=True, fix_verified=True)
    assert a.needs_human is False
    assert a.reviewer_claimed_human is True
    assert "overridden by evidence" in a.reason
    assert any("reproduced" in e for e in a.evidence)


def test_claim_alone_never_forces_escalation():
    a = adjudicate(summary=ROUND8, klass="concurrency-lost-update")
    assert a.needs_human is False
    assert a.reviewer_claimed_human is True
    assert "run a probe" in a.reason


def test_reproduced_but_unverified_stays_with_agent():
    a = adjudicate(summary=ROUND8, klass="concurrency-lost-update",
                   reproduced=True)
    assert a.needs_human is False
    assert "verify the fix" in a.reason


def test_irreversible_always_needs_human():
    a = adjudicate(summary="delete all user records", klass="state-integrity",
                   reproduced=True, fix_verified=True, irreversible=True)
    assert a.needs_human is True
    assert a.decision_class == "irreversible-action"


def test_scope_change_always_needs_human():
    a = adjudicate(summary="add undo support", klass="state-integrity",
                   reproduced=True, fix_verified=True, changes_scope=True)
    assert a.needs_human is True
    assert a.decision_class == "scope-change"


def test_product_preference_needs_human():
    a = adjudicate(summary="should completed tasks sort to the bottom?",
                   klass="product-behavior")
    assert a.needs_human is True


def test_cost_tradeoff_needs_human():
    a = adjudicate(summary="switch to a paid API for better accuracy",
                   klass="cost-tradeoff")
    assert a.needs_human is True


def test_mechanical_classes_do_not_need_human():
    for k in ("contrast-text", "untrusted-boundary", "silent-mutation",
              "stale-live-region", "test-gap"):
        a = adjudicate(summary="defect", klass=k, reproduced=True,
                       fix_verified=True)
        assert a.needs_human is False, k


def test_unclassified_is_triaged_not_silently_closed():
    a = adjudicate(summary="the widget feels off", klass="other")
    assert a.needs_human is True
    assert a.decision_class == "unclassified"


def test_reproducible_wording_without_class_is_still_agent_work():
    a = adjudicate(summary="null entry crashes the render",
                   reproduced=True, fix_verified=True)
    assert a.needs_human is False


def test_as_dict_is_serializable():
    d = adjudicate(summary=ROUND8, klass="concurrency-lost-update",
                   reproduced=True, fix_verified=True).as_dict()
    assert set(d) == {"needs_human", "reason", "decision_class",
                      "reviewer_claimed_human", "evidence"}