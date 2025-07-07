
import requests
from flask import Flask, request, jsonify

from aiden_halfstack_solution.src import database
from engine import ScoringEngine
import data_loader
from database import Database
import pandas as pd
import storage


app = Flask(__name__)


@app.route('/search/components', methods=['POST'])
def search():
   data = request.get_json()
   table = data['table']
   req = data["request"]
   # where do they weights go?
   weights = data["weights"]
   formats = data["format"]

   # fetch schema.table from database as a df
   # is the engine supposed to by supplied by the api?
   pd.read_sql(Database(None).execute(f"SELECT * FROM {table["schema"]}.{table['table']}"))
   # fetch corresponding dtypes of table
   dtypes = data_loader.load_dtypes(table["schema"], table["table"])
   # feed request, table df, and dtypes to score engine
   engine = ScoringEngine(req, table, dtypes)
   # What method is it supposed to call to access results?
   results = engine._score_all
   # create session id and cache the results with the id
   session_id = storage.generate_session_id()
   storage.save_request(session_id, req)
   storage.save_results(session_id, results)
   # pass results to complete request to be formatted (code reuse)
   _, results = complete_request(session_id, results, formats)
   results["session"] = session_id
   return 400, jsonify(results)


@app.route("/search/<session_id>", methods=['GET'])
def complete_request(session_id, results=None, formats=None):
   if results is None:
       results = retrieve_data(session_id)
   if formats is None:
       formats = {
           "page"     : request["page"],
           "page_num" : request["page_num"],
           "sort"     : request["sort"]
       }


   # Are we sure we want to be formatting the results? Sorting seems easy and like maye we should
   # do but page specifications seems like it should be in the view. I mean how would that even be
   # implemented here? Dict with numbers as keys?


   # formatting is applied


   return 200, jsonify(results)


def retrieve_data(session_id):
   if not validate_session(session_id):
       # not sure what this causes for http
       raise Exception("Invalid session")
   # retrieve the cached data frame of results
   return storage.load_results(session_id)


def validate_session(session_id):
   # check the cache for existence
   pass




if __name__ == "__main__":
   app.run(debug=True)