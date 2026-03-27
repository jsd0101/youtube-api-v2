from flask import Flask, request, jsonify
import requests
import os
import json
from datetime import datetime
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload

# ==================== 1. Service Account 로드 ====================
def load_service_account():
    """key.json에서 Service Account 자격증명 로드"""
    try:
        if os.path.exists('key.json'):
            with open('key.json', 'r') as f:
                service_account_info = json.load(f)
            print('✅ Service Account (key.json)이 로드되었습니다')
            return service_account_info
        else:
            print('⚠️ key.json 파일을 찾을 수 없습니다')
            return None
    except Exception as e:
        print(f'⚠️ Service Account 로드 실패: {e}')
        return None

# ==================== 2. 설정 ====================
app = Flask(__name__)
API_KEY = os.getenv('API_KEY', 'youtube-shorts-api-key-2026')
YOUTUBE_SCOPES = ['https://www.googleapis.com/auth/youtube.upload']
SERVICE_ACCOUNT_INFO = load_service_account()

# ==================== 3. YouTube 서비스 생성 ====================
def get_youtube_service():
    """Service Account를 사용하여 YouTube API 클라이언트 생성"""
    try:
        if not SERVICE_ACCOUNT_INFO:
            return None, 'Service Account 정보를 찾을 수 없습니다'
        
        # Service Account 자격증명 생성
        credentials = service_account.Credentials.from_service_account_info(
            SERVICE_ACCOUNT_INFO,
            scopes=YOUTUBE_SCOPES
        )
        
        # YouTube 서비스 빌드
        youtube = build('youtube', 'v3', credentials=credentials, static_discovery=False)
        print('✅ YouTube 서비스가 생성되었습니다')
        return youtube, None
    except Exception as e:
        error_msg = f'YouTube 서비스 생성 실패: {str(e)}'
        print(error_msg)
        return None, error_msg

# ==================== 4. 동영상 다운로드 ====================
def download_video(video_url, output_path='temp_video.mp4'):
    """URL에서 동영상 다운로드"""
    try:
        response = requests.get(video_url, timeout=60)
        response.raise_for_status()
        with open(output_path, 'wb') as f:
            f.write(response.content)
        print(f'✅ 동영상 다운로드 완료: {output_path}')
        return output_path, None
    except Exception as e:
        error_msg = f'동영상 다운로드 실패: {str(e)}'
        print(error_msg)
        return None, error_msg

# ==================== 5. YouTube에 업로드 ====================
def upload_to_youtube(youtube_service, title, description, video_path):
    """동영상을 YouTube Shorts로 업로드"""
    try:
        if not os.path.exists(video_path):
            return None, f'파일을 찾을 수 없습니다: {video_path}'
        
        # 동영상 메타데이터
        body = {
            'snippet': {
                'title': title,
                'description': description,
                'categoryId': '22'  # People & Blogs
            },
            'status': {
                'privacyStatus': 'public'
            }
        }
        
        # 파일 업로드
        print(f'📤 YouTube에 업로드 중: {title}')
        media = MediaFileUpload(video_path, mimetype='video/mp4', resumable=True)
        request = youtube_service.videos().insert(
            part='snippet,status',
            body=body,
            media_body=media
        )
        response = request.execute()
        
        video_id = response.get('id')
        print(f'✅ YouTube 업로드 완료: {video_id}')
        return video_id, None
    except HttpError as e:
        error_msg = f'YouTube 업로드 실패 (HTTP {e.resp.status}): {str(e)}'
        print(error_msg)
        return None, error_msg
    except Exception as e:
        error_msg = f'YouTube 업로드 실패: {str(e)}'
        print(error_msg)
        return None, error_msg

# ==================== 6. Flask 라우트 ====================

@app.route('/', methods=['GET'])
def index():
    """헬스 체크 및 정보"""
    return jsonify({
        'service': 'YouTube Shorts Auto Upload API',
        'version': '3.0',
        'status': 'running',
        'auth_method': 'Service Account',
        'endpoints': {
            '/': 'Health check',
            '/health': 'Simple health status',
            '/test-auth': 'Test authentication',
            '/upload-shorts': 'Upload video (POST)'
        }
    }), 200

@app.route('/health', methods=['GET'])
def health():
    """간단한 헬스 체크"""
    return jsonify({'status': 'ok'}), 200

@app.route('/test-auth', methods=['GET'])
def test_auth():
    """인증 상태 테스트"""
    # API 키 검증
    api_key = request.headers.get('X-API-Key')
    if not api_key or api_key != API_KEY:
        return jsonify({
            'success': False,
            'error': 'Unauthorized - Invalid or missing API key'
        }), 401
    
    # YouTube 서비스 생성 테스트
    youtube, error = get_youtube_service()
    if error:
        return jsonify({
            'success': False,
            'error': error
        }), 401
    
    return jsonify({
        'success': True,
        'message': 'Authentication successful',
        'auth_method': 'Service Account',
        'service_account_loaded': SERVICE_ACCOUNT_INFO is not None
    }), 200

@app.route('/upload-shorts', methods=['POST'])
def upload_shorts():
    """
    YouTube Shorts 업로드 엔드포인트
    
    요청 예시:
    {
        "title": "My YouTube Short",
        "description": "A test short video",
        "video_url": "https://example.com/video.mp4"
    }
    """
    # API 키 검증
    api_key = request.headers.get('X-API-Key')
    if not api_key or api_key != API_KEY:
        return jsonify({
            'success': False,
            'error': 'Unauthorized - Invalid or missing API key'
        }), 401
    
    # JSON 파싱
    try:
        data = request.get_json()
        title = data.get('title', 'Untitled')
        description = data.get('description', '')
        video_url = data.get('video_url')
        
        if not video_url:
            return jsonify({
                'success': False,
                'error': 'Missing required field: video_url'
            }), 400
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Invalid JSON: {str(e)}'
        }), 400
    
    # YouTube 서비스 생성
    youtube, error = get_youtube_service()
    if error:
        return jsonify({
            'success': False,
            'error': error
        }), 401
    
    # 동영상 다운로드
    temp_video_path = f'temp_video_{int(datetime.now().timestamp())}.mp4'
    video_path, dl_error = download_video(video_url, temp_video_path)
    if dl_error:
        return jsonify({
            'success': False,
            'error': dl_error
        }), 400
    
    # YouTube에 업로드
    video_id, upload_error = upload_to_youtube(youtube, title, description, video_path)
    
    # 임시 파일 삭제
    try:
        if os.path.exists(video_path):
            os.remove(video_path)
            print(f'✅ 임시 파일 삭제: {video_path}')
    except Exception as e:
        print(f'⚠️ 임시 파일 삭제 실패: {e}')
    
    # 결과 반환
    if upload_error:
        return jsonify({
            'success': False,
            'error': upload_error
        }), 400
    
    return jsonify({
        'success': True,
        'video_id': video_id,
        'title': title,
        'url': f'https://www.youtube.com/shorts/{video_id}'
    }), 200

# ==================== 7. 앱 실행 ====================
if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
