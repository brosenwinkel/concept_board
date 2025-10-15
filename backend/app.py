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
GOOGLE_DRIVE_FOLDER_ID = os.getenv('GOOGLE_DRIVE_FOLDER_ID', 'root')
ANTHROPIC_API_KEY = os.getenv('ANTHROPIC_API_KEY')

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
        'scope': 'https://www.googleapis.com/auth/spreadsheets https://www.googleapis.com/auth/drive.file',
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
        f"https://sheets.googleapis.com/v4/spreadsheets/{GOOGLE_SHEET_ID}/values/{sheet_name}:append?valueInputOption=USER_ENTERED",
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

@app.route('/api/enhance-prompt', methods=['POST'])
def enhance_prompt():
    data = request.json
    prompt = data.get('prompt', '')
    has_reference = data.get('hasReference', False)
    
    if has_reference:
        instruction = f'Enhance this image generation prompt by adding more visual details, lighting, composition, and artistic style. IMPORTANT: Add "Use Reference Image as Character" at the beginning of the enhanced prompt. The model should use the character from the reference image and place them in the new scene. Retain all specific instructions from the original prompt. Return ONLY the enhanced prompt with no explanations. Original prompt: {prompt}'
    else:
        instruction = f'Enhance this image generation prompt by adding more visual details, lighting, composition, and artistic style. Return ONLY the enhanced prompt with no explanations, introductions, or additional text. Original prompt: {prompt}'
    
    response = requests.post(
        'https://api.anthropic.com/v1/messages',
        headers={
            'x-api-key': ANTHROPIC_API_KEY,
            'anthropic-version': '2023-06-01',
            'content-type': 'application/json'
        },
        json={
            'model': 'claude-sonnet-4-20250514',
            'max_tokens': 1024,
            'messages': [{
                'role': 'user',
                'content': instruction
            }]
        }
    )
    
    result = response.json()
    enhanced = result['content'][0]['text']
    return jsonify({'enhanced': enhanced})

@app.route('/api/generate-video-prompt', methods=['POST'])
def generate_video_prompt():
    data = request.json
    prompt = data.get('prompt', '')
    
    response = requests.post(
        'https://api.anthropic.com/v1/messages',
        headers={
            'x-api-key': ANTHROPIC_API_KEY,
            'anthropic-version': '2023-06-01',
            'content-type': 'application/json'
        },
        json={
            'model': 'claude-sonnet-4-20250514',
            'max_tokens': 512,
            'messages': [{
                'role': 'user',
                'content': f'Based on this image prompt, create a video animation prompt that describes how to animate this image using depth of field, parallax effects, camera movements, and other cinematic techniques specific to the scene. Return ONLY the video prompt with no explanations. Image prompt: {prompt}'
            }]
        }
    )
    
    result = response.json()
    video_prompt = result['content'][0]['text']
    return jsonify({'videoPrompt': video_prompt})

@app.route('/api/describe-image', methods=['POST'])
def describe_image():
    import base64
    data = request.json
    image_data = data.get('imageData', '')
    
    response = requests.post(
        'https://api.anthropic.com/v1/messages',
        headers={
            'x-api-key': ANTHROPIC_API_KEY,
            'anthropic-version': '2023-06-01',
            'content-type': 'application/json'
        },
        json={
            'model': 'claude-sonnet-4-20250514',
            'max_tokens': 1024,
            'messages': [{
                'role': 'user',
                'content': [
                    {
                        'type': 'image',
                        'source': {
                            'type': 'base64',
                            'media_type': 'image/jpeg',
                            'data': image_data
                        }
                    },
                    {
                        'type': 'text',
                        'text': 'Describe this image in detail, focusing on the visual elements, composition, lighting, mood, and any notable features. Keep the description concise but comprehensive.'
                    }
                ]
            }]
        }
    )
    
    result = response.json()
    description = result['content'][0]['text']
    return jsonify({'description': description})

@app.route('/uploads/<path:filename>')
def serve_upload(filename):
    from pathlib import Path
    upload_dir = Path('/app/uploads')
    return send_file(upload_dir / filename)

@app.route('/api/video/upload', methods=['POST'])
def video_upload():
    import base64
    from pathlib import Path
    
    data = request.json
    file_data = base64.b64decode(data['fileData'])
    
    # Save to local uploads directory
    upload_dir = Path('/app/uploads')
    upload_dir.mkdir(exist_ok=True)
    
    file_path = upload_dir / data['filename']
    with open(file_path, 'wb') as f:
        f.write(file_data)
    
    return jsonify({
        'success': True,
        'filename': data['filename'],
        'path': str(file_path),
        'url': f'/uploads/{data["filename"]}'
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True, port=5000)
