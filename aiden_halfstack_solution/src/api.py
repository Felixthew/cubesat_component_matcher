
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
   weights = request["weights"]
   formats = request["format"]

   # fetch schema.table from database as a df

   pd.read_sql(Database(None).execute(f"SELECT * FROM {table["schema"]}.{table['table']}"))
   dtypes = data_loader.load_dtypes(table["schema"], table["table"])
   # fetch corresponding dtypes of table
   # feed request, table df, and dtypes to score engine
   engine = ScoringEngine(req, table, dtypes)
   results = engine._score_all
   # create session id and cache the results with the id
   session_id = storage.generate_session_id()
   storage.save_request(session_id, req)
   storage.save_results(session_id, results)
   # pass results to complete request to be formatted (code reuse)
   return complete_request(session_id, results, formats)




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




   # not sure if jsonify handles dataframes well


   # formatting is applied


   return jsonify(results)


def retrieve_data(session_id):
   if not validate_session(session_id):
       raise Exception("Invalid session")
   # retrieve the cached data frame of results
   pass


def validate_session(session_id):
   # check the cache for existence
   pass




if __name__ == "__main__":
   app.run(debug=True)