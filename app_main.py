import os, io, requests
from flask import Flask, jsonify, request
from google.oauth2 import service_account
import googleapiclient.discovery
import googleapiclient.http

app = Flask(__name__)
API_KEY = "youtube-shorts-api-key-2026"
SERVICE_ACCOUNT_FILE = 'key.json'
SCOPES = ['https://www.googleapis.com/auth/youtube.upload']

def get_youtube_service():
    try:
        credentials = service_account.Credentials.from_service_account_file(
            SERVICE_ACCOUNT_FILE, scopes=SCOPES)
        return googleapiclient.discovery.build('youtube', 'v3', credentials=credentials)
    except Exception as e:
        print(f'YouTube service error: {e}')
        return None

@app.route('/')
def index():
    return jsonify({'status': 'ok', 'message': 'YouTube Shorts API v3'})

@app.route('/test-auth', methods=['GET'])
def test_auth():
    if request.headers.get('X-API-Key') != API_KEY:
        return jsonify({'status': 'error', 'message': 'Invalid API key'}), 401
    youtube = get_youtube_service()
    if youtube:
        return jsonify({'status': 'ok', 'message': 'YouTube authenticated successfully!'})
    return jsonify({'status': 'error', 'message': 'Authentication failed'}), 500

@app.route('/upload-shorts', methods=['POST'])
def upload_shorts():
    if request.headers.get('X-API-Key') != API_KEY:
        return jsonify({'status': 'error', 'message': 'Invalid API key'}), 401
    try:
        data = request.get_json()
        title = data.get('title', 'Untitled')
        description = data.get('description', '')
        video_url = data.get('video_url')
        
        if not video_url:
            return jsonify({'status': 'error', 'message': 'video_url required'}), 400
        
        # Download video
        resp = requests.get(video_url, timeout=30)
        if resp.status_code != 200:
            return jsonify({'status': 'error', 'message': 'Video download failed'}), 400
        
        video_file = io.BytesIO(resp.content)
        youtube = get_youtube_service()
        
        if not youtube:
            return jsonify({'status': 'error', 'message': 'YouTube auth failed'}), 500
        
        body = {
            'snippet': {
                'title': title,
                'description': description,
                'categoryId': '22'
            },
            'status': {
                'privacyStatus': 'private',
                'selfDeclaredMadeForKids': False
            }
        }
        
        media = googleapiclient.http.MediaIoBaseUpload(video_file, 'video/mp4', resumable=True)
        request_obj = youtube.videos().insert(part='snippet,status', body=body, media_body=media)
        response = request_obj.execute()
        
        return jsonify({
            'status': 'ok',
            'message': 'Video uploaded successfully',
            'video_id': response['id'],
            'title': title
        }), 200
    except Exception as e:
        print(f'Error: {e}')
        return jsonify({'status': 'error', 'message': str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
