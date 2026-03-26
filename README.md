## Project Purpose
NASA Ames Research Center internally maintains many Excel spreadsheets containing data about the current
state-of-the-art components for SmallSats (satellites >180kg, often with COTS components), detailing the vendor,
its technical specifications, where it can be found, etc. This data can be of interest to universities, governments,
or other companies that are searching for particular components for their own SmallSats.
This project, last updated in August 2025, aims to complete three tasks with relation to these spreadsheets:
- upload properly-formatted spreadsheets into a PostgreSQL database for centralized access
- provide API access to component data based on request parameters
- design and implement custom logic in order to rank component data based on similarity to the aforementioned request


For example, an end user may be interested in purchasing a battery pack with a specific energy of 100 Wh/kg and a
TRL of 7. What would be the closest "match" to such a request, based on the existing products in the database?
As of now, its Ibeos' 28V Modular Battery with a match score of 81% (109.8 Wh/kg and TRL 9). Further retrieval
preferences can also be specified, such as the scoring mode per column, the number of results to return, the return
order, plus basic numeric sorting and filtering. Check out this AI-generated [mock website](http://129.159.89.217:8000)
demonstrating the core backend logic with a demo portion of the real database.


Due to its nature as a summer internship project, it was developed with future contribution and project inheritance
in mind. In-depth explanations of all subsystems and the complete control pipeline (gauged toward future backend
contributors) can be found in `backend_info.md`. For frontend developers that wish to use the API provided here,
check out `frontend_info.md`, which explains the complete interface, relevant design assumptions, and recommendations
on how to limit end user engagement with the retrieval system.


## Project Structure


```
src/
   backend_solution/               all code related to database managment, request scoring, and web API
   upload_data/                    all code related to uploading formatted Excel data to database
static/                             html for demo website
tests/                              all test data
   component_data_TEST/            segment of real data (potentially outdated) to test in database
   test_requests/                  json payload requests to check program behavior
   test_results/                   corresponding json results for each request
   api_test.py                     tests for each API feature using the above json files
   scorer_test.py                  unit tests for internal scoring logic per datatype
backend_info.md                     in-depth information about all files and interactions in src/backend_solution
frontend_info.md                    in-depth information about web API and program usage
README.md                           you are here!
requirements.txt                    list of all library dependencies
upload_table_instructions.md        directions on spreadsheet formatting and instructions for proper upload to database
```

