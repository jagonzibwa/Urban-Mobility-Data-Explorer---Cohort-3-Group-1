from flask import Flask, request, jsonify
from flask_
from flask_cors import CORS
import sqlite3
import os

DB = os.path.join(os.path.dirname(__file__), 'database.sql')

app = Flask(__name__)
CORS(app)

def get_db_connection():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/api/trips', methods=['GET'])