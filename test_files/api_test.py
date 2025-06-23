import os
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from sqlalchemy import create_engine, text
from filter_algo_test import get_schemas, get_systems, get_parameters

app = Flask(__name__)
CORS(app)
engine = create_engine("postgresql://postgres:PzcglEfINUtMgDzqZAtEhvVexsfWIrZT@switchyard.proxy.rlwy.net:12039/railway")

@app.route("/")
def serve_homepage():
    return send_from_directory(directory=os.path.abspath(".."), path="ui_test.html")
@app.route("/schemas", methods=["GET"])
def list_schemas():
    return jsonify(get_schemas(engine))

@app.route("/systems", methods=["GET"])
def list_tables():
    schema = request.args.get("schema")
    return jsonify(get_systems(engine, schema))

@app.route("/parameters", methods=["GET"])
def list_columns():
    schema = request.args.get("schema")
    table = request.args.get("table")
    return jsonify(get_parameters(engine, schema, table))

if __name__ == "__main__":
    app.run(debug=True)