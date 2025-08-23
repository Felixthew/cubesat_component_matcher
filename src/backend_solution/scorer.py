import math
from math import prod
from abc import ABC, abstractmethod
import numpy as np
from rapidfuzz import fuzz
import src.backend_solution.json_types as jt


# Additional config options must be added in
# - the proper type method
# - the SCORING_CONFIG
# Make sure the scoring config default is the same as the method default parameters

# Additional datatypes must:
# - add a new subclass of Scorer
# - update SCORING_REGISTRY
# - update default configs in SCORING_CONFIG
# Then double check for type properties that may require attention in engine.py or data_loader.py
# (Add test cases in test/scorer_test)

class Scorer(ABC):
    @abstractmethod
    def score(self, request_val, candidate_val, **kwargs) -> float:
        """
        Computes compatibility score between the user request value and the candidate value
        :param request_val: user value
        :param candidate_val: value to be compared to
        :param kwargs: space to add type-specific configs, changing computation behavior
        :return: compatibility score for request_val and candidate_val
        """
        pass


class NumberScorer(Scorer):
    def score(self, request_val, candidate_val, use_global_extrema=True, max_val=None, min_val=None, **_) -> float:
        """
        :param use_global_extrema: normalize values against the max and min value in the dataset, otherwise against each other
        :param max_val: global max value used in above config
        :param min_val: global min value used in above config
        """

        if request_val is None or candidate_val is None:
            return 0.0

        max_val = max_val if use_global_extrema and max_val else max(request_val, candidate_val)
        min_val = min_val if use_global_extrema and min_val else min(request_val, candidate_val)
        request_val, candidate_val, max_val = _normalize_negatives(request_val, candidate_val, max_val, min_val)

        diff = abs(request_val - candidate_val)

        if max_val == 0.0:
            max_val = 1.0

        return max(0.0, 1.0 - diff / max_val)


class StringScorer(Scorer):
    def score(self, request_val, candidate_val, threshold=80, exact_match=False, contains_any=False) -> float:
        """
        :param contains_any: returns 1 if the request contains the candidate in its list.
            Must be exact match (could be changed in the future, im thinking maybe take the highest match in the list).
        :param threshold: minimum fuzz ratio [0..100] for scoring;
            ratios above the threshold are linearly mapped onto [0..1]
        :param exact_match: toggle for only succeeding the string match if they are identical.
            Equivalent to threshold=100
        """

        if request_val is None or candidate_val is None:
            return 0.0

        if contains_any:
            request_vals = list(map(lambda x: _clean_string(x), request_val.split(",")))
            return 1.0 if _clean_string(candidate_val) in request_vals else 0.0

        request_val = _clean_string(request_val)
        candidate_val = _clean_string(candidate_val)

        if exact_match or threshold == 100:
            return request_val == candidate_val

        raw_ratio = fuzz.ratio(request_val, candidate_val)
        if raw_ratio < threshold:
            return 0.0
        return (raw_ratio - threshold) / (100 - threshold)


class TupleScorer(Scorer):
    def score(self, request_val, candidate_val, product_scoring=False, normalize_to_max=True, **_) -> float:
        """
        :param product_scoring: combines tuple components multiplicatively and computes single representative values,
            otherwise computes piecewise and averages. Useful when product is significant, e.g. volume
        :param normalize_to_max: scoring models frame themselves using the input data's maximum value to normalize,
            useful when all values are near each other/on the same scale. Has no effect on product_scoring mode
        """

        if request_val is None or candidate_val is None:
            return 0.0

        request_val = _parse_collection(request_val)
        candidate_val = _parse_collection(candidate_val)

        # fail if input aren't numbers
        try:
            request_val_list = [float(x) for x in request_val]
        except (TypeError, ValueError):
            raise ValueError("Improper input")

        # return 0 if candidates aren't numbers
        try:
            candidate_val_list = [float(x) for x in candidate_val]
        except (TypeError, ValueError):
            return 0.0

        # score numbers singly as combined products
        if product_scoring:
            req_product = prod(request_val_list)
            cand_product = prod(candidate_val_list)
            return NumberScorer().score(
                req_product,
                cand_product,
                normalize_to_max,
                max(req_product, cand_product)
                # ^technically redundant
            )

        # score numbers dimensionwise and average the results
        results = []
        for req_val, cand_val in zip(sorted(request_val_list), sorted(candidate_val_list)):
            results.append(NumberScorer().score(
                req_val,
                cand_val,
                normalize_to_max,
                _union_max(request_val_list, candidate_val_list),
                _union_min(request_val_list, candidate_val_list)
            ))

        return float(np.mean(results))


class ListScorer(Scorer):
    def score(self, request_val, candidate_val, match_mode="overlap", jaccard_softener=1, **_) -> float:
        """
        :param match_mode: "jaccard" more heavily penalizes differences between sets,
            while "overlap" mode is based only on the inclusion in the requested set.
            "contains" returns a true/false for inclusion of ANY element, good for multiselect preferences
        :param jaccard_softener: slightly increases jaccard scores for fairness. NOT EXPOSED AS A CONFIG OPTION
        """
        print(match_mode)

        # return 0 for empty inputs
        if request_val is None or candidate_val is None:
            return 0.0

        req_set, cand_set = set(_parse_collection(request_val)), set(_parse_collection(candidate_val))

        # checks for inclusion anywhere once
        if match_mode == "contains":
            for val in req_set:
                if val in cand_set:
                    return 1.0
            return 0.0

        intersect = req_set & cand_set

        # disjunct sets gets full penalty
        if len(intersect) == 0:
            return 0.0

        # use overlap or jaccard arithmetic
        if match_mode == "overlap":
            return len(intersect) / len(req_set)
        return (len(intersect) + jaccard_softener) / (len(req_set | cand_set) + jaccard_softener)


class BooleanScorer(Scorer):
    def score(self, request_val, candidate_val, **_) -> float:
        return 1.0 if bool(request_val) == bool(candidate_val) else 0.0


class RangeScorer(Scorer):
    def score(self, request_val, candidate_val, decay_factor=1.0, **kwargs) -> float:
        """
        NOTE: request_val is a SINGLE NUMBER (int, float), not a range itself
        :param decay_factor: values between 0 and 1 make the decay more rapid, values over 1 slow it down
        """

        # negative decay factor will result in scores larger than 1.0 outside of the bounds
        if decay_factor < 0:
            raise ValueError("Decay Factor cannot be negative")

        if request_val is None or candidate_val is None:
            return 0.0

        low, high = _parse_range(candidate_val)

        # if the request is contained in the range, return 1.0
        if low <= request_val <= high:
            return 1.0

        # else exponentially decay score
        diff = low - request_val if request_val < low else request_val - high
        return math.exp(-diff / (10 * decay_factor))


def _clean_string(val: str) -> str:
    return val.strip().lower()


def _parse_collection(vals: str) -> list[str]:
    return [_clean_string(val) for val in vals.split(",")]


def _parse_range(val: str) -> tuple[float, float]:
    range_elements = val.split("-")

    # handle bad formatting
    if len(range_elements) != 2:
        raise ValueError("Improper range format")
    try:
        min, max = float(range_elements[0]), float(range_elements[1])
    except TypeError:
        raise ValueError("Not a number range")
    except IndexError:
        raise ValueError("Improper range format")

    # order
    if min > max:
        min, max = max, min

    return min, max


def _union_max(vals1: list[float | int], vals2: list[float | int]) -> float | int:
    return max(max(vals1), max(vals2))


def _union_min(vals1: list[float | int], vals2: list[float | int]) -> float | int:
    return min(min(vals1), min(vals2))


def _normalize_negatives(
        val1: int | float,
        val2: int | float,
        max: int | float,
        min: int | float
) -> tuple[int | float, int | float, int | float]:
    if min < 0:
        delta = abs(min)
        val1 += delta
        val2 += delta
        max += delta
    return val1, val2, max


# add new type methods here for engine iteration
SCORING_REGISTRY = {
    "number": NumberScorer(),
    "string": StringScorer(),
    "tuple": TupleScorer(),
    "list": ListScorer(),
    "boolean": BooleanScorer(),
    "range": RangeScorer()
}

# add new default configs here
SCORING_CONFIG = {
    "number": {"use_global_max": True},
    "string": {"threshold": 80, "exact_match": False},
    "tuple": {"product_scoring": False, "normalize_to_max": True},
    "list": {"match_mode": "overlap"},
    "boolean": {},
    "range": {"decay_factor": 1.0}
}

SCORING_KWARGS = {
    "number": [
        jt.KwargProfile(
            name="use_global_max", dtype="Boolean", default=True,
            description="Normalize values against the max and min value in the dataset, otherwise against each other. Must also pass global max and min."
        ),
        jt.KwargProfile(
            name="max_val", dtype="Float", default="auto calculated",
            description="Global max value used in use global max config"
        ),
        jt.KwargProfile(
            name="min_val", dtype="Float", default="auto calculated",
            description="Global min value used in use global max config"
        )
    ],
    "string": [
        jt.KwargProfile(
            name="threshold", dtype="Int", default=80,
            description="Minimum fuzz ratio [0..100] for scoring; ratios above the threshold are linearly mapped onto [0..1]"
        ),
        jt.KwargProfile(
            name="exact_match", dtype="Boolean", default=False,
            description="Toggle for only succeeding the string match if they are identical. Equivalent to threshold=100"
        ),
        jt.KwargProfile(
            name="contains_any", dtype="Boolean", default=False,
            description="Returns full match if the request contains the candidate in its list. Request must be comma-separated list. Must be exact match"
        )
    ],
    "tuple": [
        jt.KwargProfile(
            name="product_scoring", dtype="Boolean", default=False,
            description="Combines tuple components multiplicatively and computes single representative values, otherwise computes piecewise and averages. Useful when product is significant, e.g. volume"
        ),
        jt.KwargProfile(
            name="normalize_to_max", dtype="Boolean", default=True,
            description="Scoring models frame themselves using the input data's maximum value to normalize, useful when all values are near each other/on the same scale. Has no effect on product_scoring mode"
        )
    ],
    "list": [
        jt.KwargProfile(
            name="match_mode", dtype="String", default="overlap",
            description="'jaccard' more heavily penalizes differences between sets, while 'overlap' mode is based only on the inclusion in the requested set. 'contains' returns a true/false for inclusion of ANY element, good for multiselect preferences",
            options=["overlap", "jaccard", "contains"]
        )
    ],
    "boolean": [
        # No kwargs listed for "boolean" type; empty list
    ],
    "range": [
        jt.KwargProfile(
            name="decay_factor", dtype="Float", default=1.0,
            description="Values between 0 and 1 make the score outside of the range decay more rapidly (less tolerant), values over 1 slow it down (more tolerant)"
        )
    ]
}
