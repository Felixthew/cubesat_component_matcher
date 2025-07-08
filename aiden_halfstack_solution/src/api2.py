from fastapi import FastAPI, HTTPException, Query
import pandas as pd
from pydantic import BaseModel, Field
from engine import ScoringEngine
from database import db
import storage

app = FastAPI(title="Component Matcher")

@app.post("/search", response_model=SearchResponse, summary="Retrieve scored results given new spec requests")
def search(query: SearchRequest) -> SearchResponse:

    # prepare engine parameters
    engine_request = load_request(query.specs)
    engine_candidates_df = load_candidates(query.location)
    engine_dtypes = load_dtypes(query.location)
    engine_scoring_config = None
    # ^configs need more infrastructure established -- left to defaults for now

    # create and run the engine. let it do the heavy lifting on computing extended_df
    engine = ScoringEngine(engine_request, engine_candidates_df, engine_dtypes, engine_scoring_config)
    scored_table = engine.extended_df.to_dict(orient="records") # BOOM

    # identify/generate session id for the recall then cache session data
    sid = query.session_id or storage.generate_session_id()
    storage.save_request(sid, query.model_dump())
    storage.save_results(sid, scored_table)

    return SearchResponse(session_id=sid, results=scored_table)


@app.get("/search/{session_id}", response_model=SearchResponse,
         summary="Retrieve scored results from preexisting session, with optional filtering, sorting, and pagination")
def retrieve(query: RetrieveRequest) -> SearchResponse:
    sid = query.session_id

    # check for faulty inputs or storage
    try:
        raw_table = storage.load_results(sid)
    except ValueError:
        raise HTTPException(404, "Session not found")
    if raw_table is None:
        raise HTTPException(404, "Results not found")

    # on success, retrieve df
    df_inter = pd.DataFrame(raw_table)

    # apply preferences
    df_inter = _filter(query.filters, df_inter)
    df_inter = _sort(query.sort, df_inter)
    df_inter = _paginate(query.pagination, df_inter)

    # package and return
    result = df_inter.to_dict(orient="records")
    return SearchResponse(session_id=sid, results=result)





def _filter(filters: list[Filter], df: pd.DataFrame) -> pd.DataFrame:
    for f in filters:
        if f.min_val is not None:
            df = df[df[f.name] >= f.min_val]
        if f.max_val is not None:
            df = df[df[f.name] <= f.max_val]
    return df

def _sort(sort: Sort, df: pd.DataFrame) -> pd.DataFrame:
    return df.sort_values(sort.by, ascending=sort.asc)

def _paginate(paging: Pagination, df: pd.DataFrame) -> pd.DataFrame:
    first = paging.per_page * (paging.page - 1)
    last = first + paging.per_page
    return df.iloc[first:last]