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


### Persisting Data (storage.py)

The purpose of these methods is to store, retrieve, and remove the session data cached during queries. After the 
initial search method is 

### Scoring Data (engine.py, scorer.py)