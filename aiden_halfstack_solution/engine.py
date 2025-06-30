import pandas as pd
from sqlalchemy.testing.suite.test_reflection import metadata

from scorer import SCORING_REGISTRY, SCORING_CONFIG



class ScoringEngine:
    def __init__(self,
                 request: dict,
                 candidates_df: pd.DataFrame,
                 dtypes: dict[str, str],
                 scoring_config = SCORING_CONFIG):
        self.dtypes = dtypes
        self.specs = {col["name"]: col for col in request["columns"]}
        self.config = scoring_config
        self.global_maxes = {
            col: candidates_df[col].max()
            for col in dtypes
            if dtypes[col] == "number"
        }
        self.extended_df = self._score_all(candidates_df, request)

    def _score_single(self, column_name, request_val, candidate_val):
        dtype = self.dtypes[column_name]
        scorer = SCORING_REGISTRY[dtype]

        # can lead the way for column-specific kwargs, forced or user-specified
        type_kwargs = self.config[dtype]
        all_kwargs = {**type_kwargs, "max_val": self.global_maxes[column_name]}

        return scorer.score(request_val, candidate_val, all_kwargs)

    def _score_row(self, row_df: pd.DataFrame):
        score_summary = {
            "overall": 0.0,
            "by_col": {
                col: 0.0
                for col in row_df.keys()
            }}

        for col, val in row_df:
            # score_summary["by_col"][col] = registry[col].score(Scorer, self.specs[col]["value"], )