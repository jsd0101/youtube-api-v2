import os
from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/')
def home():
    return {"message": "API is running"}, 200

@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "ok", "message": "App is running"}), 200

@app.route('/test-auth', methods=['GET'])
def test_auth():
    access_token = os.getenv('OAUTH_ACCESS_TOKEN', 'Not set')
    refresh_token = os.getenv('OAUTH_REFRESH_TOKEN', 'Not set')
    return jsonify({
        "access_token_set": bool(access_token != 'Not set'),
        "refresh_token_set": bool(refresh_token != 'Not set')
    }), 200

# Gunicorn이 이 부분을 무시하므로, if __name__ == '__main__' 블록은 제거됨
# Procfile에서 gunicorn이 app 객체를 직접 로드함
