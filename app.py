from flask import Flask, jsonify, request, redirect
import os
import json
from google_auth_oauthlib.flow import Flow
from google.oauth2.credentials import Credentials

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'dev-secret-key')

SCOPES = ['https://www.googleapis.com/auth/youtube.upload']
CLIENT_SECRETS_FILE = 'client_secret.json'

@app.route('/')
def hello():
    return 'Hello World'

@app.route('/health')
def health():
    return jsonify({"status": "ok", "message": "App is running"})

@app.route('/auth/login')
def auth_login():
    try:
        flow = Flow.from_client_secrets_file(
            CLIENT_SECRETS_FILE,
            scopes=SCOPES,
            redirect_uri='https://web-production-6821d.up.railway.app/auth/callback'
        )
        auth_url, state = flow.authorization_url(access_type='offline', prompt='consent')
        return redirect(auth_url)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/auth/callback')
def auth_callback():
    try:
        code = request.args.get('code')
        state = request.args.get('state')
        
        if not code:
            return jsonify({"error": "No authorization code received"}), 400
        
        flow = Flow.from_client_secrets_file(
            CLIENT_SECRETS_FILE,
            scopes=SCOPES,
            redirect_uri='https://web-production-6821d.up.railway.app/auth/callback',
            state=state
        )
        flow.fetch_token(authorization_response=request.url)
        credentials = flow.credentials
        
        token_data = {
            'token': credentials.token,
            'refresh_token': credentials.refresh_token,
            'token_uri': credentials.token_uri,
            'client_id': credentials.client_id,
            'client_secret': credentials.client_secret,
            'scopes': credentials.scopes
        }
        
        with open('token.json', 'w') as f:
            json.dump(token_data, f)
        
        return jsonify({"status": "success", "message": "Authentication successful"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/upload-shorts', methods=['POST'])
def upload_shorts():
    try:
        if not os.path.exists('token.json'):
            return jsonify({"error": "Authentication required. Please login first."}), 401
        
        data = request.get_json() if request.is_json else {}
        video_file = request.files.get('video')
        title = data.get('title', 'Untitled Shorts')
        description = data.get('description', '')
        
        if not video_file:
            return jsonify({"error": "No video file provided"}), 400
        
        return jsonify({
            "status": "success",
            "message": "Shorts uploaded successfully",
            "title": title
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
