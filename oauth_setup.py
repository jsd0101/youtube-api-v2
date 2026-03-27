import os, pickle
from google_auth_oauthlib.flow import InstalledAppFlow

SCOPES = ['https://www.googleapis.com/auth/youtube.upload']
CLIENT_SECRET_FILE = 'client_secret.json'

def authenticate():
    flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRET_FILE, SCOPES)
    creds = flow.run_local_server(port=5000, open_browser=False)
    with open('token.pickle', 'wb') as f:
        pickle.dump(creds, f)
    print('OAuth 인증 성공! token.pickle이 생성되었습니다.')

if __name__ == '__main__':
    authenticate()
