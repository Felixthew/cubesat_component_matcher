from abc import ABC, abstractmethod
from math import sqrt
from rapidfuzz import fuzz

from upload_table import remove_table


# Additional config options must be added in
# 1) the proper type method
# 2) the SCORING_REGISTRY
# 3) the SCORING_CONFIG
# Make sure the scoring config default is the same as the method default parameters

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
    def score(self, request_val, candidate_val, use_global_max=True, max_val=None, **_) -> float:
        """
        :param use_global_max: normalize values against the max value in the dataset, otherwise against each other
        :param max_val: global max value used in above config
        """
        if request_val is None or candidate_val is None:
            return 0.0

        diff = abs(request_val - candidate_val)
        max_val = max_val if use_global_max and max_val else max(request_val, candidate_val)
        return max(0.0, 1.0 - diff / max_val)


class StringScorer(Scorer):
    def score(self, request_val, candidate_val, threshold=80, exact_match=False) -> float:
        """
        :param threshold: minimum fuzz ratio [0..100] for scoring; ratios above the threshold are linearly mapped onto [0..1]
        :param exact_match: toggle for only succeeding the string match if they are identical. Equivalent to threshold=100
        """
        if request_val is None or candidate_val is None:
            return 0.0

        request_val = _clean_string(request_val)
        candidate_val = _clean_string(candidate_val)

        if exact_match or threshold == 100:
            return request_val == candidate_val

        raw_ratio = fuzz.ratio(request_val, candidate_val)
        if raw_ratio < threshold:
            return 0.0
        return (raw_ratio - threshold) / (100 - threshold)


class TupleScorer(Scorer):
    def score(self, request_val, candidate_val, distance_mode="euclidean", tolerance=10.0, **_) -> float:
        """
        :param distance_mode: euclidean distance is more sensitive to large differences in a single dimension; manhattan difference treats all dimensions equally
        :param tolerance: assures a perfect match within the tolerance, and gradually decays outside of it. Higher tolerance recommended for manhattan searches
        """

        if request_val is None or candidate_val is None:
            return 0.0

        request_val = _parse(request_val)
        candidate_val = _parse(candidate_val)

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

        # fail for unmatched dimensions
        n = len(request_val_list)
        if n != len(candidate_val_list):
            raise ValueError("Improper input")


        # distance calculation by mode
        if distance_mode == "manhattan":
            dist = sum(abs(request_val_list[i] - candidate_val_list[i]) for i in range(n))
        else:
            dist = sqrt(sum((request_val_list[i] - candidate_val_list[i])**2 for i in range(n)))

        # return 1 if within tolerance threshold
        if dist <= tolerance:
            return 1.0

        # decay score over distance
        excess = dist - tolerance
        return max(0.0, 1 - excess / tolerance)


class ListScorer(Scorer):
    def score(self, request_val, candidate_val, match_mode="jaccard", **_) -> float:
        """
        :param match_mode: jaccard more heavily penalizes differences between sets, while overlap mode just checks for inclusion
        """

        if request_val is None or candidate_val is None:
            return 0.0

        set_r, set_c = set(request_val), set(candidate_val)

        if not set_r or not set_c:
            return 0.0

        intersect = set_r & set_c
        if match_mode == "overlap":
            return len(intersect) / len(set_r)
        return len(intersect) / len(set_r | set_c)


class BooleanScorer(Scorer):
    def score(self, request_val, candidate_val, **_) -> float:
        return 1.0 if bool(request_val) == bool(candidate_val) else 0.0


def _clean_string(val: str):
    return val.strip().lower()

def _parse(vals: str):
    return _clean_string(vals).split(", ")


# add new type methods here for engine iteration
SCORING_REGISTRY = {
    "number": NumberScorer(),
    "string": StringScorer(),
    "tuple": TupleScorer(),
    "list": ListScorer(),
    "boolean": BooleanScorer()
}

# add new default configs here
SCORING_CONFIG = {
    "number": {"use_global_max": True},
    "string": {"threshold": 80, "exact_match": False},
    "tuple": {"distance_mode": "euclidean", "tolerance": 10.0},
    "list": {"match_mode": "jaccard"},
    "boolean": {}
}