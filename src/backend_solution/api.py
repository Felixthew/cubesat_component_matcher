from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from src.backend_solution.json_types import KwargProfile
from src.backend_solution.scorer import SCORING_KWARGS
import pandas as pd
import src.backend_solution.json_types as jt
from src.backend_solution.engine import ScoringEngine
import src.backend_solution.storage as storage
import src.backend_solution.data_loader as dl
import json

app = FastAPI(title="Component Matcher")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/options", response_model=jt.SchemaList,
         summary="Lists all solution types to choose from, e.g. propulsion")
def get_solutions() -> jt.SchemaList:
    return jt.SchemaList(schemas=dl.list_schema())

@app.get("/options/{solution}", response_model=jt.TableList,
         summary="Lists all system types to choose from, e.g. chemical propulsion")
def get_systems(solution: str) -> jt.TableList:
    tables = dl.list_tables(solution)
    if not tables:
        raise HTTPException(404, "No existing systems in request solution category")
    return jt.TableList(schema=solution, tables=tables)

@app.get("/options/{solution}/{system}", response_model=jt.ColumnList,
         summary="Lists all parameters of a given system, e.g. thrust")
def get_params(solution: str, system: str) -> jt.ColumnList:
    # retrieves cached dtype data
    dtype_rows = dl.get_dtypes(solution, system)
    location = jt.Location(schema=solution, table=system)

    # except if null result
    if dtype_rows is None:
        raise HTTPException(404, f"{system} in {solution} not found")

    # construct list of json-friendly col-dtype entries and return
    param_list = [
        jt.ColumnProfile(name=name,
                         dtype=dtype,
                         options=dl.list_choices(location, name, dtype),
                         kwargs=SCORING_KWARGS[dtype])
        for name, dtype in dtype_rows.items()
    ]
    return jt.ColumnList(location=location, columns=param_list)

@app.get("/kwargs", response_model=dict[str,list[jt.KwargProfile]],
         summary="Lists all scoring kwargs by type")
def get_params() -> dict[str, list[KwargProfile]]:
    return SCORING_KWARGS

@app.post("/search", response_model=jt.SearchResponse, summary="Retrieve scored results given new spec requests")
def search(query: jt.SearchRequest) -> jt.SearchResponse:
    # prepare engine parameters
    engine_request = dl.load_request(query.specs)
    engine_candidates_df = dl.load_candidates(query.location)
    engine_dtypes = dl.get_dtypes(query.location.schema, query.location.table)
    engine_scoring_config = query.kwargs if query.kwargs else None

    # create and run the engine. let it do the heavy lifting on computing extended_df
    engine = ScoringEngine(engine_request, engine_candidates_df, engine_dtypes, engine_scoring_config)
    # I changed this to Json to get rid of the NaNs, hopefully that is all good
    json_str = engine.extended_df.to_json(orient='records', date_format='iso', force_ascii=False)
    scored_table = json.loads(json_str) # BOOM
    original_columns = engine.extended_df.columns.tolist()

    # identify/generate session id for the recall then cache session data
    sid = query.session_id or storage.generate_session_id()
    storage.save_request(sid, query.model_dump())

    # prune old session data
    storage.prune_expired_sessions()

    # package and store results then return
    results = jt.SearchResponse(session_id=sid, values=scored_table, order=original_columns)
    storage.save_results_bm(results)
    # storage.save_results_bm(results)
    return results

    # storage.save_results(sid, {
    #     'data': scored_table,
    #     'column_order': original_columns
    # })
    #
    # return jt.SearchResponse(session_id=sid, values=scored_table)


@app.post("/search/{session_id}", response_model=jt.SearchResponse,
         summary="Retrieve scored results from preexisting session, with optional filtering, sorting, and pagination")
def retrieve(session_id: str, query: jt.RetrieveRequest) -> jt.SearchResponse:
    sid = session_id

    # check for faulty inputs or storage
    try:
        raw_results = storage.load_results(sid)
    except ValueError:
        raise HTTPException(404, "Session not found")
    if raw_results is None:
        raise HTTPException(404, "Results not found")

    # on success, retrieve df
    df_inter = _order_cols(query, raw_results)

    # apply preferences
    df_inter = _filter(query.filters, df_inter)
    df_inter = _sort(query.sort, df_inter)
    df_inter = _paginate(query.pagination, df_inter)

    # package and return
    result = df_inter.to_dict(orient="records")
    # i don't like order being forced pase to the user, i'd rather make it optional field just for behind the scenes
    return jt.SearchResponse(session_id=sid, values=result, order=raw_results["order"])


def _order_cols(query: jt.RetrieveRequest, raw_results: dict):
    if query.sort.score_coupling:
        columns = raw_results["order"]

        score_columns = set(col for col in columns if col.endswith('_score'))
        value_columns = [col for col in columns if not col.endswith('_score')]

        column_order = ["overall_score"]
        for val_col in value_columns:
            column_order.append(val_col)
            score_col = f"{val_col}_score"
            if score_col in score_columns:
                column_order.append(score_col)
                score_columns.remove(score_col)
        df_inter = pd.DataFrame(raw_results["values"])[column_order]
    else:
        df_inter = pd.DataFrame(raw_results["values"])[raw_results['column_order']]
    return df_inter


def _filter(filters: list[jt.Filter], df: pd.DataFrame) -> pd.DataFrame:
    for f in filters:
        try:
            if f.min_val is not None:
                df = df[df[f.name] >= f.min_val]
            if f.max_val is not None:
                df = df[df[f.name] <= f.max_val]
        except TypeError:
            continue
            # raise ValueError("Column is not numerically comparable")
            # ^ decide to propagate type error or just make it harmless to pass strings etc in the filter
    return df

def _sort(sort: jt.Sort, df: pd.DataFrame) -> pd.DataFrame:
    return df.sort_values(by=sort.by, ascending=sort.asc)

def _paginate(paging: jt.Pagination, df: pd.DataFrame) -> pd.DataFrame:
    first = paging.per_page * (paging.page - 1)
    last = first + paging.per_page
    return df.iloc[first:last]

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)