from typing import Any

from pydantic import BaseModel, Field

# Utility module to keep track of json-relevant objects used in the API

class Location(BaseModel):
    schema: str
    table: str

class SchemaList(BaseModel):
    schemas: list[str]

class TableList(BaseModel):
    schema: str
    tables: list[str]

class ColumnProfile(BaseModel):
    name: str
    dtype: str
    options: list[str] | None = None
    kwargs: dict[str, str] | None = None

class ColumnList(BaseModel):
    location: Location
    columns: list[ColumnProfile]

class ColumnSpec(BaseModel):
    name: str
    value: str | int | float
    weight: float = Field(..., gt=0)
    configs: dict[str, str | int | float | bool]

class Filter(BaseModel):
    name: str
    min_val: float | int | None = None
    max_val: float | int | None = None

class Sort(BaseModel):
    by: str = Field("overall_score")
    asc: bool = Field(False)
    score_coupling: bool = Field(True)

class Pagination(BaseModel):
    page: int = Field(1, ge=1)
    per_page: int = Field(10, ge=1, le=100)

class SearchKwargs(BaseModel):
    col_kwargs: dict[str, dict[str, Any]] | None = None
    type_kwargs: dict[str, dict[str, Any]] | None = None

class SearchRequest(BaseModel):
    location: Location
    specs: list[ColumnSpec]
    session_id: str | None = None
    kwargs: SearchKwargs | None = None

class SearchResponse(BaseModel):
    session_id: str
    values: list[dict]
    order: list[str]

class RetrieveRequest(BaseModel):
    filters: list[Filter]
    sort: Sort
    pagination: Pagination