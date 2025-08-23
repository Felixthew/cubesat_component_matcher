import pytest
import src.backend_solution.scorer as sc
from abc import ABC


def _case(args: tuple, config: dict, expected) -> dict:
    # produces test case based on if it's supposed to return (expected is a score) or raise an exception
    if isinstance(expected, float):
        return {"args": args, "config": config, "returns": expected}
    else:
        return {"args": args, "config": config, "raises": expected}


class GenericScorerTester(ABC):
    SCORER = None
    CASES = [] # list of dicts: [{"args": (request, candidate), "config": {name: val, ... }, returns: val, raises: exception}, ... ]

    def run_scorer(self, case):
        scorer = self.SCORER()
        args = case.get("args", ())
        config = case.get("config")

        if "raises" in case:
            with pytest.raises(case["raises"]):
                scorer.score(*args, **config)

        else:
            returns = case["returns"]
            result = scorer.score(*args, **config)
            assert result == pytest.approx(returns, rel=1e-1)


class TestNumberScorer(GenericScorerTester):
    SCORER = sc.NumberScorer

    CASES = [
        # null args return 0
        _case((None, 10), {}, 0.0),
        _case((10, None), {}, 0.0),

        # global max rescales results
        _case((5, 15), {"use_global_max": True, "max_val": 20}, 0.5),
        _case((5, 15), {"use_global_max": False, "max_val": 20}, 0.33),

        # same but downshift into negatives
        _case((-5, 5), {"use_global_max": True, "max_val": 10}, 0.5),
        _case((-5, 5), {"use_global_max": False, "max_val": 10}, 0.33),

        # upshift with magnitude
        # TODO using some really ugly techniques (see _normalize_negatives() in scorer.py)... seeking advice
        _case((-100, 100), {"use_global_max": True, "max_val": 150}, 0.43),
        _case((-100, 100), {"use_global_max": False, "max_val": 150}, 0.33),

        # perfect match
        _case((10, 10), {}, 1.0),

        # edge
        _case((0, 0), {"use_global_max": True, "max_val": 0}, 1.0)
    ]

    @pytest.mark.parametrize("case", CASES)
    def test_score(self, case):
        self.run_scorer(case)


class TestStringScorer(GenericScorerTester):
    SCORER = sc.StringScorer

    CASES = [
        # null/nonargs return 0
        _case(("hello", None), {}, 0.0),
        _case((None, "hello"), {}, 0.0),
        _case(("", "hello"), {}, 0.0),

        # exact match disregards case and whitespace
        _case(("hello", "hello"), {"exact_match": True}, 1.0),
        _case(("hello", "hola"), {"exact_match": True}, 0.0),
        _case(("hello", "   HELlO  "), {"exact_match": True}, 1.0),

        # threshold makes appropriate chops
        # TODO not a huge fan of these scores
        _case(("hello", "hel lo"), {"threshold": 80}, 0.55),
        _case(("hello", "hola"), {"threshold": 80}, 0.0),

        # threshold edge cases
        _case(("hello", "hello"), {"threshold": 100, "exact_match": False}, 1.0),
        _case(("hello", "hel lo"), {"threshold": 0}, 0.91)
    ]

    @pytest.mark.parametrize("case", CASES)
    def test_score(self, case):
        self.run_scorer(case)

class TestTupleScorer(GenericScorerTester):
    SCORER = sc.TupleScorer

    CASES = [
        # null/nonargs return 0, exact match returns 1
        _case((None, "1, 2, 3"), {}, 0.0),
        _case(("1, 2, 3", ""), {}, 0.0),
        _case(("1, 2, 3", "1, 2, 3"), {}, 1.0),

        # reordering tuples doesn't affect score on all configs
        _case(("1, 2, 3", "4, 5, 6"), {"product_scoring": False, "normalize_to_max": False}, 0.38),
        _case(("3, 1, 2", "6, 5, 4"), {"product_scoring": False, "normalize_to_max": False}, 0.38),
        _case(("1, 2, 3", "4, 5, 6"), {"product_scoring": False, "normalize_to_max": True}, 0.5),
        _case(("3, 1, 2", "6, 5, 4"), {"product_scoring": False, "normalize_to_max": True}, 0.5),

        _case(("3, 1, 2", "4, 5, 6"), {"product_scoring": True, "normalize_to_max": False}, 0.05),
        _case(("3, 1, 2", "6, 5, 4"), {"product_scoring": True, "normalize_to_max": False}, 0.05),
        _case(("3, 1, 2", "4, 5, 6"), {"product_scoring": True, "normalize_to_max": True}, 0.05),
        _case(("3, 1, 2", "6, 5, 4"), {"product_scoring": True, "normalize_to_max": True}, 0.05),

        # "the zero test"
        _case(("0, 0", "10, 20"), {"product_scoring": False, "normalize_to_max": False}, 0.0),
        _case(("0, 0", "10, 20"), {"product_scoring": False, "normalize_to_max": True}, 0.25),
        _case(("0, 0", "10, 20"), {"product_scoring": True}, 0.0),

        # close matches
        _case(("1, 2, 4", "1, 3, 4"), {"product_scoring": False, "normalize_to_max": False}, 0.87),
        _case(("1, 2, 4", "1, 3, 4"), {"product_scoring": False, "normalize_to_max": True}, 0.92),
        _case(("1, 2, 4", "1, 3, 4"), {"product_scoring": True}, 0.66),

        # input error is thrown
        _case(("something else", "4, 5, 6"), {}, ValueError),
    ]

    @pytest.mark.parametrize("case", CASES)
    def test_score(self, case):
        self.run_scorer(case)


class TestListScorer(GenericScorerTester):
    SCORER = sc.ListScorer

    # using jaccard_softener = 1
    CASES = [
        # null/nonargs return 0
        _case(("", "a, b, c"), {}, 0.0),
        _case(("a, b, c", None), {}, 0.0),

        # proper exact matches
        _case(("a, b, c", "a, b, c"), {}, 1.0),
        _case(("A, b, C     ", "   c, B, a"), {}, 1.0),

        # disjunct
        _case(("a, b, c", "d, e, f"), {"match_mode": "jaccard"}, 0.0),
        _case(("a, b, c", "d, e, f"), {"match_mode": "overlap"}, 0.0),
        _case(("a, b, c", "d, e, f"), {"match_mode": "contains"}, 0.0),

        # bad match
        _case(("a, b, c", "c, d, e"), {"match_mode": "jaccard"}, 0.33),
        _case(("a, b, c", "c, d, e"), {"match_mode": "overlap"}, 0.33),
        _case(("a, b, c", "c, d, e"), {"match_mode": "contains"}, 1.0),

        # close match
        _case(("a, b, c", "b, c, d"), {"match_mode": "jaccard"}, 0.6),
        _case(("a, b, c", "b, c, d"), {"match_mode": "overlap"}, 0.67),
        _case(("a, b, c", "b, c, d"), {"match_mode": "contains"}, 1.0),

        # subsetting
        _case(("a", "a, b, c"), {"match_mode": "jaccard"}, 0.5),
        _case(("a", "a, b, c"), {"match_mode": "overlap"}, 1.0),
        _case(("a", "a, b, c"), {"match_mode": "contains"}, 1.0),
    ]

    @pytest.mark.parametrize("case", CASES)
    def test_score(self, case):
        self.run_scorer(case)


class TestBooleanScorer(GenericScorerTester):
    SCORER = sc.BooleanScorer

    CASES = [
        # XNOR gate check
        _case((0, 0), {}, 1.0),
        _case((0, 1), {}, 0.0),
        _case((1, 1), {}, 1.0)
    ]

    @pytest.mark.parametrize("case", CASES)
    def test_score(self, case):
        self.run_scorer(case)


class TestRangeScorer(GenericScorerTester):
    SCORER = sc.RangeScorer

    CASES = [
        # null returns 0
        _case((None, "0-10"), {}, 0.0),
        _case((5, None), {}, 0.0),

        # format and input errors raised
        _case((5, "0-10-20"), {}, ValueError),
        _case((5, "A-B"), {}, ValueError),
        _case((5, "A, B"), {}, ValueError),
        _case((5, "0-10"), {"decay_factor": -1.0}, ValueError),

        # containment returns 1
        _case((5, "0-10"), {}, 1.0),
        _case((5, "10-0"), {}, 1.0),

        # decays outside
        # low positive
        _case((48, "50-60"), {"decay_factor": 1.0}, 0.82),
        _case((48, "50-60"), {"decay_factor": 5.0}, 0.96),
        _case((48, "50-60"), {"decay_factor": 0.2}, 0.37),

        # high positive
        _case((30, "0-10"), {"decay_factor": 1.0}, 0.14),
        _case((30, "0-10"), {"decay_factor": 5.0}, 0.67),
        _case((30, "0-10"), {"decay_factor": 0.2}, 4.5e-5),

        # low negative
        _case((-2, "0-10"), {"decay_factor": 1.0}, 0.82),
        _case((-2, "0-10"), {"decay_factor": 5.0}, 0.96),
        _case((-2, "0-10"), {"decay_factor": 0.2}, 0.37),

        # reasonable check
        _case((48, "50-60"), {"decay_factor": 2.0}, 0.90),
        _case((48, "50-60"), {"decay_factor": 3.0}, 0.94),
        _case((48, "50-60"), {"decay_factor": 4.0}, 0.95),
        _case((48, "50-60"), {"decay_factor": 10.0}, 0.98)
    ]

    @pytest.mark.parametrize("case", CASES)
    def test_score(self, case):
        self.run_scorer(case)