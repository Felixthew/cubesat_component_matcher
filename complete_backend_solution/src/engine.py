import pandas as pd
from scorer import SCORING_REGISTRY, SCORING_CONFIG

class ScoringEngine:
    def __init__(self,
                 request: dict,
                 candidates_df: pd.DataFrame,
                 dtypes: dict[str, str],
                 scoring_config: dict | None):
        self.specs = request
        self.dtypes = dtypes
        self.config = scoring_config or SCORING_CONFIG
        self.global_maxes = {
            col: candidates_df[col].max()
            for col in dtypes
            if dtypes[col] == "number"
        }
        self.extended_df: pd.DataFrame = self._score_all(candidates_df)

    def _score_single(self, column_name, request_val, candidate_val):
        dtype = self.dtypes[column_name]
        scorer = SCORING_REGISTRY[dtype]

        # can lead the way for column-specific kwargs, forced or user-specified
        type_kwargs = self.config[dtype]
        all_kwargs = {**type_kwargs, "max_val": self.global_maxes[column_name]}

        return scorer.score(request_val, candidate_val, all_kwargs)

    def _score_row(self, row: pd.Series) -> dict:
        # safety against passing a df
        if isinstance(row, pd.DataFrame):
            row = row.squeeze(axis=0)

        # initialize summary dict
        score_summary = {}
        weighted_sum = 0.0
        total_weight = 0.0

        # for each entry in the request table:
        for col, data in self.specs.items():
            # parse columnwise data in request
            request_val = data["value"]
            request_weight = data["weight"]

            # compute single column score and store in unique score_summary entry
            raw_score = self._score_single(col, request_val, row[col])
            score_summary[f"{col}_score"] = raw_score

            # weight score and add to aggregate score
            if raw_score is not None:
                weighted_sum += raw_score * request_weight
                total_weight += request_weight

        # normalize aggregate and return
        # return format: {"overall_score": x, "col1_score": y, ...}
        score_summary["overall_score"] = weighted_sum / total_weight if total_weight else 0.0
        return score_summary

    def _score_all(self, candidates_df):
        # apply score_row to each row of df, return Series
        scored_series = candidates_df.apply(self._score_row, axis=1)

        # converts series into new df of scores
        score_df = pd.json_normalize(scored_series.tolist())

        # join score df and raw df and return
        extended_df = candidates_df.join(score_df)
        return extended_df

    # def filter(self, filters: dict[str, dict[str, float]]) -> pd.DataFrame:
    #     """
    #     Filters the extended dataframe by upper and lower numerical bounds.
    #     :param filters: {column_name: {"min": x, "max": y}, ...}
    #     :return: copy of extended dataframe with applied bounds
    #     """
    #
    #     # limits filtering to data typed as "number"
    #     for col in filters.keys():
    #         if self.dtypes[col] != "number":
    #             raise ValueError("Attempting to filter by min/max on non-number")
    #
    #     # copies extended df for easy + safe return
    #     df_copy = self.extended_df.copy()
    #
    #     # if a min and/or max was passed in the filters, redefines the copy df to only include values above/below the min/max
    #     for col, bounds in filters.items():
    #         if "min" in bounds:
    #             df_copy = df_copy[df_copy[col] >= bounds["min"]]
    #         if "max" in bounds:
    #             df_copy = df_copy[df_copy[col] <= bounds["max"]]
    #     return df_copy
    #
    # def sort(self, by: str, ascending: bool = True):
    #     """
    #     Sorts the extended dataframe by certain score parameters, and by ascending or descending order.
    #     :param by: "overall" or by explicit column name, including {col} and {col_score}
    #     :param ascending: determines direction of sort
    #     :return: copy of extended dataframe with applied ordering
    #     """
    #     return self.extended_df.sort_values(by=by, ascending=ascending)