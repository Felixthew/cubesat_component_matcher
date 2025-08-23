## Backend Info

The following will be my attempt at a comprehensive overview of the project as it exists in August 2025.
The entire backend project is split into four processes: retrieving data, persisting data, scoring data, and the API. 

### API (api.py, json_types.py)

The API is necessarily the logic controller for the other processes. There are three general operations that these
methods execute: establishing the initial search scope (the "preliminary search"), retrieving freshly-scored results
(the "scoring"), and reformatting already-scored results via filtering, sorting, and pagination (the "reslice").  

Briefly about json_types.py: we used pydantic's BaseModels to keep the json payloads organized. Looking at the file 
should make things obvious about their structure. I will note which operations below utilize which objects. The 
Location object is generally used everywhere as an address for a table, as it contains schema and table info that can
be queried to.

The preliminary search is composed of get_solutions(), get_systems(), and get_params(). These each represent a different
level of specificity the frontend team would need. The current database structure uses schema to categorize solution 
types (e.g. propulsion, thermal, GNC) and tables to represent particular systems within them (e.g. star trackers, sun
sensors). get_params() then has the task of passing up column-specific information, including the column name, the
column datatype, and any exposable data they may need (see documentation on get_choices() in data_loader.py for 
details -- right now its just *string* and *list*). All three of these methods interface directly with data_loader.py as
a way to access the database, and each return one of the json-friendly objects SchemaList, TableList, or ColumnList 
respectively. ColumnList also utilizes ColumnProfile to store the aforementioned column-specific information used to 
construct the user's form.

The scoring operation accesses the meat and potatoes of the project: the scoring engine. This is contained completely 
within the search() method. search() accepts a SearchRequest object containing an address (Location), a list of 
ColumnSpec, and optionally a session id. ColumnSpec contains the user's request columnwise with a name, value, and
weight. Session ids are crucial in storage.py and the reslicing operation. search()'s primary responsibility is to 
accept the user's request, generate a new session id, instantiate the engine, cache the results, and return the 
newly-scored table in its default ordering (descending by overall score). This method interacts with engine.py for the
engine, data_loader.py for the engine parameters, and storage.py for the session caching.

The retrieve() method represents the reslicing operation. Reslicing occurs when an existing session id is passed 
alongside sorting preferences in a RetrieveRequest object. The session id is used to recall an existing scored table
(from search() and via storage.py) and then do up to three reslicing operations on it, based on the three other 
parameters in RetrieveRequest: filtering, sorting, and paging. Filtering allows for columns to be cropped from the 
result based on minimum or maximum parameters. This is intended to be used on the score columns (e.g. only show 
overall scores >0.8 and cost scores >0.7), but can also be used on any columns of datatype *number*. Sorting simply 
determines the column to order results by and if results are descending or ascending. Pagination includes values for 
the current page number and how many results should show per page. These all have default values listed in 
json_types.py. retrieve() returns the same SearchResponse object as search(), including details about the session id and
the scored and sliced results.

### Retrieving Data (data_loader.py, database.py)

Here is the primary way of extracting information from the database. Database.py is ultimately a utility module that 
allows for easy execution of raw SQL strings. In hindsight, switching this to a Core or ORM model might be more secure
or efficient, but we chose to use raw strings. In this module, there is the global variable DB_URL, where you input the
database connection string, and then there is a Database object that represents that connection. The global variable db 
at the bottom is an instantiated Database using the supplied connection string. This allows for the
```
from database import db
db.execute(...)
```
seen in data_loader.py and storage.py to handle database queries.

Dataloader.py is the access point for the raw data used in the API to instantiate the engine or respond to the 
preliminary search requests (get_solutions(), etc). This includes retrieving from the database (via database.py) info 
about specific column datatypes, the full candidate system table, all schema, all tables in a given schema,  or the 
exposable options for a given column. The exposable options method, list_choices(), is intended to give the frontend 
team the ability to limit the number of free response boxes they give the end user. It collects and returns all the 
possible options that exist in the column, which is used in get_params() in api.py. We think this allows the request 
form to use dropdowns instead of free responses. That method has pretty chunky documentation itself so check it out for 
more info. Right now, there are only two exposable datatypes: *string* and *list*, as shown in the global variable
EXPOSABLE_DTYPES.

#### About the Database

All of the database querying and API work relies on the current organizational structure of the database. It can be 
changed, but the db.execute() SQL commands will have to be altered to reflect it, as will the json_type object Location.
As is, this is the structure we chose:

- Schema "solutions" (e.g. platforms, propulsion, deorbit)
  - Table "systems" (e.g. ESPA class satellites, chemical propulsion, deployable booms)
    - Row "products" (e.g. NASA Exo-Brake, HPS NABEO-1)
- Schema for metadata ("Metadata")
  - Table: "data_types"
    - Stores datatype info for every column of every table of every schema
  - Table: "session_data"
    - Stores requests and results from searches for several purposes. See "Persisting Data" below for more info

This structure ensures each solution schema is completely self-contained and easily uploadable from any directory of
Excel spreadsheets. The Metadata schema is critical for datatype retrieval and the API's reslicing.

### Persisting Data (storage.py)

This is where session data is controlled. Since retrieve() in api.py is just a reslice, it doesn't actually query the 
database again (that would be costly) -- it retrieves the cached results of the associated search() and manipulates it.
This means that storage.py is responsible for the methods called in search() and retrieve() in order to add the correct
data to the metadata.session_data table.

Each session_data entry has four properties: session_id, request_data, results_data, and created_at. session_id is the
primary key generated during a search, and used during a retrieval to access the previously-stored results data for 
reslicing. request_data and results_data are cached at the end of a search and are the JSON payloads in each direction 
of a query. The request is saved really only for auditing right now and isn't necessary for function, but the results 
saved are the raw ones computed by the engine. This is absolutely critical for any reslicing to exist in its current 
form. Lastly, created_at allows for pruning. To keep the database thin, the method prune_expired_sessions() is called 
sneakily during every search() call. The thought was that search() would be called less frequently that retrieve(), and
will always necessarily create a fresh session entry before pruning the old ones. The global variable 
DEFAULT_EXPIRATION_TIME_HOURS controls how long session data can last before pruning. It is currently set to 168 -- one
week. storage.py interfaces with api.py and database.py.

### Scoring Data (engine.py, scorer.py)

In terms of functionality, this is the meat and potatoes of the project. The engine and scorer run all of the logic once
supplied with a request and a candidate table. The engine completes its task during instantiation. It is constructed, 
and then the instance variable extended_df is the scored table ready for jsonification and return. It hinges on a single
call from the scoring function _score_all(), which iterates through calling _score_row(), which finally iterates through
calling _score_single(). More info on the scoring methodology is below. The engine has several parameters computed in 
api.py via data_loader.py and results in even more instance variables after parsing:

#### Parameters
-  request: dict in the form of {"Mass (kg)": {"value": 100, "weight": 0.5}, ...}. This is constructed by 
data_loader.load_request() in api.search(). As shown, this contains all of the info from the user's JSON payload.
- candidates_df: Pandas Dataframe of the selected table. The table of product "candidates" is selected given location
data in api.py via data_loader.load_candidates().
- dtypes: dict in the form of {"Mass (kg)": "number", "Manufacturer": "string", ...}. This is pulled from the 
metadata.data_types table, generated during file upload. data_loader.get_dtypes() retrieves this dict from the database.
This method has built-in caching to reduce query costs with functools' lru_cache.
- scoring_configs: json_types.SearchKwarg containing two properties: col_kwargs and type_kwargs. These are passed in
directly from the request payload as well. More detailed info on configs will be below and in README_frontend.md.

#### Properties
- specs: the request argument. This is iterated through in _score_row() to each individual _score_single() call.
- dtypes: the dtypes argument. This is used in _score_single() to verify which scorer will be used.
- global_maxes, global_mins: these are an ugly, regrettable exception to the compartmentalization that otherwise exists.
These are here to prevent continuous DB queries or DF lookups during the score-crunching of the datatype *number*. This
will be elaborated upon in the section about scoring.
- col_kwargs: dict that holds the config settings for particular rows. If the scoring_configs parameter contains no
column-specific config requests, it will be empty and default to typewide kwargs.
- type_kwargs: 