from pydantic import BaseModel, Field

# Utility module to keep track of json-relevant objects used in the API

class SchemaList(BaseModel):
    schemas: list[str]

class TableList(BaseModel):
    schema: str
    tables: list[str]

class ColumnProfile(BaseModel):
    name: str
    dtype: str
    options: list[str] | None = None

class ColumnList(BaseModel):
    schema: str
    table: str
    columns: list[ColumnProfile]

class Location(BaseModel):
    schema: str
    table: str

class ColumnSpec(BaseModel):
    name: str
    value: str | int | float
    weight: float = Field(..., gt=0)

class Filter(BaseModel):
    name: str
    min_val: float | int | None = None
    max_val: float | int | None = None

class Sort(BaseModel):
    by: str = Field("overall_score")
    asc: bool = Field(True)
    score_coupling: bool = Field(False)

class Pagination(BaseModel):
    page: int = Field(1, ge=1)
    per_page: int = Field(10, ge=1, le=100)

class SearchRequest(BaseModel):
    location: Location
    specs: list[ColumnSpec]
    session_id: str | None = None

class SearchResponse(BaseModel):
    session_id: str
    results: list[dict]

class RetrieveRequest(BaseModel):
    filters: list[Filter]
    sort: Sort
    pagination: Pagination