import scoring_procedures as scoring

class ScoringEngine:
    def __init__(self, metadata, weights, max_vals=None, config=None):
        self.metadata = metadata
        self.weights = weights
        self.max_vals = max_vals or {}
        self.config = config or {
            "numbers_use_global_max": True,
            "strings_use_fuzzy_match": False,
            "exclude_null_user_inputs": True,
            "penalize_missing_product_data": True
        }
        self.strategy_map = {
            "numeric": scoring.score_number,
            "string": scoring.score_string,
            "list": scoring.score_list,
            "tuple": scoring.score_tuple,
            "boolean": scoring.score_boolean
        }

    def score_row(self, user_input, row):
        score = 0.0
        total_weight = 0.0

        for col, user_val in user_input.items():
            datatype = self.metadata.get(col)
            product_val = row.get(col)
            weight = self.weights.get(col, 1.0)

            if self.config["exclude_null_user_inputs"] and user_val is None:
                continue

            scorer = self.strategy_map.get(datatype)
            if not scorer:
                continue

            # Handle numeric separately since it uses column_max
            if datatype == "numeric":
                raw_score = scorer(user_val, product_val, self.max_vals.get(col, 1))
            else:
                raw_score = scorer(user_val, product_val)

            if raw_score is None:
                if self.config["penalize_missing_product_data"] and product_val is None:
                    score += 0.0 * weight
                    total_weight += weight
                continue

            score += raw_score * weight
            total_weight += weight

        return score / total_weight if total_weight else 0.0