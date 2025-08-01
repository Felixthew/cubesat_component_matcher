from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
import complete_backend_solution.src.json_types as jt
from complete_backend_solution.src.engine import ScoringEngine
import complete_backend_solution.src.storage as storage
import complete_backend_solution.src.data_loader as dl
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
    # [item["table_name"] for item in tables])

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
        jt.ColumnProfile(name=name, dtype=dtype, options=dl.list_choices(location, name, dtype))
        for name, dtype in dtype_rows.items()
    ]
    return jt.ColumnList(schema=solution, table=system, columns=param_list)


@app.post("/search", response_model=jt.SearchResponse, summary="Retrieve scored results given new spec requests")
def search(query: jt.SearchRequest) -> jt.SearchResponse:

    # prepare engine parameters
    engine_request = dl.load_request(query.specs)
    engine_candidates_df = dl.load_candidates(query.location)
    engine_dtypes = dl.get_dtypes(query.location.schema, query.location.table)
    engine_scoring_config = None
    # ^configs need more infrastructure established -- left to defaults for now

    # create and run the engine. let it do the heavy lifting on computing extended_df
    engine = ScoringEngine(engine_request, engine_candidates_df, engine_dtypes, engine_scoring_config)
    # I changed this to Json to get rid of the NaNs, hopefully that is all good
    json_str = engine.extended_df.to_json(orient='records', date_format='iso', force_ascii=False)
    scored_table = json.loads(json_str) # BOOM
    original_columns = engine.extended_df.columns.tolist()

    # identify/generate session id for the recall then cache session data
    sid = query.session_id or storage.generate_session_id()
    storage.save_request(sid, query.model_dump())
    storage.save_results(sid, {
        'data': scored_table,
        'column_order': original_columns
    })

    return jt.SearchResponse(session_id=sid, results=scored_table)


@app.post("/search/{session_id}", response_model=jt.SearchResponse,
         summary="Retrieve scored results from preexisting session, with optional filtering, sorting, and pagination")
def retrieve(session_id: str, query: jt.RetrieveRequest) -> jt.SearchResponse:
    sid = session_id

    # check for faulty inputs or storage
    try:
        raw_table = storage.load_results(sid)
    except ValueError:
        raise HTTPException(404, "Session not found")
    if raw_table is None:
        raise HTTPException(404, "Results not found")

    # on success, retrieve df
    df_inter = _order_cols(query, raw_table)

    # apply preferences
    df_inter = _filter(query.filters, df_inter)
    df_inter = _sort(query.sort, df_inter)
    df_inter = _paginate(query.pagination, df_inter)

    # prune old session data
    storage.prune_expired_sessions()

    # package and return
    result = df_inter.to_dict(orient="records")
    return jt.SearchResponse(session_id=sid, results=result)


def _order_cols(query, raw_table):
    if query.sort.score_coupling:
        columns = raw_table['column_order']

        score_columns = set(col for col in columns if col.endswith('_score'))
        value_columns = [col for col in columns if not col.endswith('_score')]

        column_order = []
        for val_col in value_columns:
            column_order.append(val_col)
            if val_col + '_score' in score_columns:
                column_order.append(val_col + '_score')
                score_columns.remove(val_col + '_score')
        column_order += score_columns
        df_inter = pd.DataFrame(raw_table['data'])[column_order]
    else:
        df_inter = pd.DataFrame(raw_table['data'])[raw_table['column_order']]
    return df_inter


def _filter(filters: list[jt.Filter], df: pd.DataFrame) -> pd.DataFrame:
    for f in filters:
        if f.min_val is not None:
            df = df[df[f.name] >= f.min_val]
        if f.max_val is not None:
            df = df[df[f.name] <= f.max_val]
    return df

def _sort(sort: jt.Sort, df: pd.DataFrame) -> pd.DataFrame:
    return df.sort_values(sort.by, ascending=sort.asc)

def _paginate(paging: jt.Pagination, df: pd.DataFrame) -> pd.DataFrame:
    first = paging.per_page * (paging.page - 1)
    last = first + paging.per_page
    return df.iloc[first:last]

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)