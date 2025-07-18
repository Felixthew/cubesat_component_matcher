# The goal here is to create a scoring method for each data type. When a scoring vector is being created, it will query
# the metadata table and know how to construct an appropriate score for each parameter.
from sqlalchemy import text


# current data types: number, string, list, tuple, boolean



def score_number(user_val, product_val, column_global_max, config=None):
    if user_val is None or product_val is None:
        return None

    config = config or {}
    use_global_max = config.get("numbers_use_global_max", True)

    diff = abs(user_val - product_val)
    divisor = (column_global_max if column_global_max else 1.0) if use_global_max else max(user_val, product_val)
    return max(0.0, 1.0 - diff / divisor)


def score_string(user_val, product_val, config=None):
    if user_val is None or product_val is None:
        return None

    config = config or {}
    if config.get("strings_use_fuzzy_match", False):
        from rapidfuzz import fuzz
        return fuzz.ratio(str(user_val), str(product_val)) / 100.0

    return 1.0 if str(user_val).strip().lower() == str(product_val).strip().lower() else 0.0


def score_tuple(user_val, product_val, config=None):
    pass


def score_list(user_val, product_val, config=None):
    pass

def score_boolean(user_val, product_val):
    pass



def compute_column_maxes(engine, df, table_name):
    query = """
        SELECT column_name, type
        FROM metadata.data_types
        WHERE table_name = :table_name
        AND type = 'number'
    """
    result = engine.execute(text(query), {"table_name": table_name}).fetchall()
    number_cols_in_table = [row.column_name for row in result]

    col_maxes = {col: df[col].max() for col in number_cols_in_table}
    return col_maxes