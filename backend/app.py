from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import requests
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
CORS(app)

@app.route('/')
def index():
    return send_file('../standalone.html')

@app.route('/favicon.ico')
def favicon():
    return '', 204

API_KEY = os.getenv('API_KEY')
API_BASE = os.getenv('API_BASE')
GOOGLE_SHEET_ID = os.getenv('GOOGLE_SHEET_ID')
GOOGLE_SERVICE_ACCOUNT_EMAIL = os.getenv('GOOGLE_SERVICE_ACCOUNT_EMAIL')
GOOGLE_PRIVATE_KEY = os.getenv('GOOGLE_PRIVATE_KEY', '').replace('\\n', '\n')

@app.route('/api/create-task', methods=['POST'])
def create_task():
    data = request.json
    response = requests.post(
        f"{API_BASE}/createTask",
        headers={'Content-Type': 'application/json', 'Authorization': f'Bearer {API_KEY}'},
        json=data
    )
    return jsonify(response.json())

@app.route('/api/query-task', methods=['GET'])
def query_task():
    task_id = request.args.get('taskId')
    response = requests.get(
        f"{API_BASE}/recordInfo?taskId={task_id}",
        headers={'Authorization': f'Bearer {API_KEY}'}
    )
    return jsonify(response.json())

@app.route('/api/google-auth', methods=['POST'])
def google_auth():
    import jwt
    import time
    
    now = int(time.time())
    payload = {
        'iss': GOOGLE_SERVICE_ACCOUNT_EMAIL,
        'scope': 'https://www.googleapis.com/auth/spreadsheets',
        'aud': 'https://oauth2.googleapis.com/token',
        'exp': now + 3600,
        'iat': now
    }
    
    token = jwt.encode(payload, GOOGLE_PRIVATE_KEY, algorithm='RS256')
    
    response = requests.post(
        'https://oauth2.googleapis.com/token',
        data={
            'grant_type': 'urn:ietf:params:oauth:grant-type:jwt-bearer',
            'assertion': token
        }
    )
    return jsonify(response.json())

@app.route('/api/sheets/read', methods=['GET'])
def sheets_read():
    range_name = request.args.get('range')
    token = request.headers.get('Authorization')
    
    response = requests.get(
        f"https://sheets.googleapis.com/v4/spreadsheets/{GOOGLE_SHEET_ID}/values/{range_name}?majorDimension=ROWS",
        headers={'Authorization': token}
    )
    return jsonify(response.json())

@app.route('/api/sheets/append', methods=['POST'])
def sheets_append():
    data = request.json
    token = request.headers.get('Authorization')
    sheet_name = data.get('sheet', '02_Video')
    
    response = requests.post(
        f"https://sheets.googleapis.com/v4/spreadsheets/{GOOGLE_SHEET_ID}/values/{sheet_name}:append?valueInputOption=RAW",
        headers={'Authorization': token, 'Content-Type': 'application/json'},
        json={'values': data['values']}
    )
    return jsonify(response.json())

@app.route('/api/gpt4o-create', methods=['POST'])
def gpt4o_create():
    data = request.json
    response = requests.post(
        'https://api.kie.ai/api/v1/gpt4o-image/generate',
        headers={'Content-Type': 'application/json', 'Authorization': f'Bearer {API_KEY}'},
        json=data
    )
    return jsonify(response.json())

@app.route('/api/gpt4o-query', methods=['GET'])
def gpt4o_query():
    task_id = request.args.get('taskId')
    response = requests.get(
        f'https://api.kie.ai/api/v1/gpt4o-image/record-info?taskId={task_id}',
        headers={'Authorization': f'Bearer {API_KEY}'}
    )
    return jsonify(response.json())

@app.route('/api/flux-kontext-create', methods=['POST'])
def flux_kontext_create():
    data = request.json
    response = requests.post(
        'https://api.kie.ai/api/v1/flux/kontext/generate',
        headers={'Content-Type': 'application/json', 'Authorization': f'Bearer {API_KEY}'},
        json=data
    )
    return jsonify(response.json())

@app.route('/api/flux-kontext-query', methods=['GET'])
def flux_kontext_query():
    task_id = request.args.get('taskId')
    response = requests.get(
        f'https://api.kie.ai/api/v1/flux/kontext/record-info?taskId={task_id}',
        headers={'Authorization': f'Bearer {API_KEY}'}
    )
    return jsonify(response.json())

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True, port=5000)
