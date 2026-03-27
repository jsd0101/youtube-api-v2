import os
from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok', 'message': 'App is running'}), 200

@app.route('/test-auth', methods=['GET'])
def test_auth():
    access_token = os.getenv('OAUTH_ACCESS_TOKEN', 'Not set')
    refresh_token = os.getenv('OAUTH_REFRESH_TOKEN', 'Not set')
    return jsonify({
        'access_token_set': bool(access_token != 'Not set'),
        'refresh_token_set': bool(refresh_token != 'Not set')
    }), 200

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
