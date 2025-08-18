import pandas as pd
from complete_backend_solution.src.json_types import SearchKwargs
from complete_backend_solution.src.scorer import SCORING_REGISTRY, SCORING_CONFIG

class ScoringEngine:
    def __init__(self,
                 request: dict,
                 candidates_df: pd.DataFrame,
                 dtypes: dict[str, str],
                 scoring_config: SearchKwargs | None):
        self.specs = request
        self.dtypes = dtypes
        self.global_maxes = {
            col: candidates_df[col].max()
            for col in dtypes
            if dtypes[col] == "number"
        }
        self.global_mins = {
            col: candidates_df[col].min()
            for col in dtypes
            if dtypes[col] == "number"
        }
        # Extract kwargs with defaults
        self.col_kwargs = {}
        self.type_kwargs = SCORING_CONFIG

        if scoring_config is not None:
            if scoring_config.col_kwargs is not None:
                self.col_kwargs = scoring_config.col_kwargs
            if scoring_config.type_kwargs is not None:
                for data_type in scoring_config.type_kwargs:
                    for k in scoring_config.type_kwargs[data_type]:
                        self.type_kwargs[data_type][k] = scoring_config.type_kwargs[data_type][k]

        self.extended_df: pd.DataFrame = self._score_all(candidates_df)

    # score a single cell against the respective requested value
    def _score_single(self, column_name, request_val, candidate_val):
        dtype = self.dtypes[column_name]
        scorer = SCORING_REGISTRY[dtype]
        all_kwargs = {}
        if dtype == "number":
            all_kwargs["max_val"] = self.global_maxes[column_name]
            all_kwargs["min_val"] = self.global_mins[column_name]
        if dtype in self.type_kwargs:
            for k in self.type_kwargs[dtype]:
                all_kwargs[k] = self.type_kwargs[dtype][k]
        if column_name in self.col_kwargs:
            for k in self.col_kwargs[column_name]:
                all_kwargs[k] = self.col_kwargs[column_name][k]

        return scorer.score(request_val, candidate_val, **all_kwargs)

    # scores an entire entry by iterating through each column
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

    # scores the entire table by iterating through each column, and then produces the extended_df with score columns
    def _score_all(self, candidates_df):
        # apply score_row to each row of df, return Series
        scored_series = candidates_df.apply(self._score_row, axis=1)

        # converts series into new df of scores
        score_df = pd.json_normalize(scored_series.tolist())

        # join score df and raw df and return
        extended_df = candidates_df.join(score_df).sort_values(by="overall_score", ascending=False)
        return extended_df