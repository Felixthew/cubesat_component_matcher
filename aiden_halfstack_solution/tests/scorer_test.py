import pytest
import aiden_halfstack_solution.src.scorer as sc
from abc import ABC


# def _case(args: tuple, config: dict, expected: float = None, raises: Exception = None) -> dict:
#     if not raises:
#         return {"args": args, "config": config, "expected": expected}
#     else:
#         return {"args": args, "config": config, "raises": raises}


def _case(args: tuple, config: dict, expected: float | Exception ) -> dict:
    # produces test case based on if it's supposed to return (expected is a score) or raise an exception
    if isinstance(expected, float):
        return {"args": args, "config": config, "returns": expected}
    # elif isinstance(expected, Exception):
    #     return {"args": args, "config": config, "raises": expected}
    # else:
    #     raise ValueError("Expected is not score nor error")

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
            assert result == pytest.approx(returns, rel=1e-2)


class TestNumberScorer(GenericScorerTester):
    SCORER = sc.NumberScorer

    CASES = [
        _case((None, 10), {}, 0.0),
        _case((10, None), {}, 0.0),

        _case((10, 5), {"use_global_max": True, "max_val": 20}, 0.75),
        _case((10, 5), {"use_global_max": False, "max_val": 20}, 0.5),

        _case((10, 10), {}, 1.0)
    ]

    @pytest.mark.parametrize("case", CASES)
    def test_score(self, case):
        self.run_scorer(case)


class TestStringScorer(GenericScorerTester):
    SCORER = sc.StringScorer

    CASES = [
        _case(("hello", None), {}, 0.0),
        _case((None, "hello"), {}, 0.0),
        _case(("", "hello"), {}, 0.0),

        _case(("hello", "hello"), {"exact_match": True}, 1.0),
        _case(("hello", "hola"), {"exact_match": True}, 0.0),
        _case(("hello", "   HELlO  "), {"exact_match": True}, 1.0),

        _case(("hello", "hel lo"), {"threshold": 80}, 0.55),
        _case(("hello", "hola"), {"threshold": 80}, 0.0),

        _case(("hello", "hello"), {"threshold": 100, "exact_match": False}, 1.0),
        _case(("hello", "hel lo"), {"threshold": 0}, 0.91)
    ]

    @pytest.mark.parametrize("case", CASES)
    def test_score(self, case):
        self.run_scorer(case)


class TestTupleScorer(GenericScorerTester):
    SCORER = sc.TupleScorer

    CASES = [
        _case((None, "1, 2, 3"), {}, 0.0),
        _case(("1, 2, 3", ""), {}, 0.0),

        _case(("1, 2, 3", "1, 2, 3"), {}, 1.0),

        _case(("0, 0, 0", "10, 10, 10"), {"distance_mode": "euclidean", "tolerance": 20}, 1.0),
        _case(("0, 0, 0", "10, 10, 10"), {"distance_mode": "euclidean", "tolerance": 10}, 0.27),

        _case(("0, 0, 0", "10, 10, 10"), {"distance_mode": "manhattan", "tolerance": 30}, 1.0),
        _case(("0, 0, 0", "10, 10, 10"), {"distance_mode": "manhattan", "tolerance": 20}, 0.5),

        _case(("1, 2, 3", "4, 5"), {}, ValueError),
        _case(("something else", "4, 5, 6"), {}, ValueError),
    ]

    @pytest.mark.parametrize("case", CASES)
    def test_score(self, case):
        self.run_scorer(case)


class TestListScorer(GenericScorerTester):
    SCORER = sc.ListScorer

    CASES = [

    ]

    @pytest.mark.parametrize("case", CASES)
    def test_score(self, case):
        self.run_scorer(case)


class TestBooleanScorer(GenericScorerTester):
    SCORER = sc.BooleanScorer

    CASES = [

    ]

    @pytest.mark.parametrize("case", CASES)
    def test_score(self, case):
        self.run_scorer(case)